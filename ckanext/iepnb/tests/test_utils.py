import pytest
import ckanext.iepnb.utils as iepnb_utils
import ckanext.iepnb.config as iepnb_config
import ckan.logic as logic
from html.parser import HTMLParser
import ckan.tests.helpers as helpers
from pathlib import Path

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

@pytest.fixture
def make_parser_object(request):
    diccionario= {
        "handle_starttag":  None,
        "handle_endtag":    None,
        "handle_data":      None,
        "footer":           None,
        "header":           None,
        "header_counter":   0,
        "footer_counter":   False
        }
    marker = request.node.get_closest_marker("parser_function")
    if marker is not None and len(marker.args) == 2:
        diccionario[marker.args[0]] = marker.args[1]
    
    ClassParser=type("ClassParser", (HTMLParser,), diccionario)
    return ClassParser()

class Fake_urlopen:
    def __init__(self, _file):
        self.file = _file
        self.url = None
    
    def urlopen(self, _url, context):
        self.url = _url
        return self

    def read(self):
        class Fake_read():
            def __init__(self, _file):
                self.file = _file
            def decode(self, encoding):
                return Path(__file__).resolve(True).parent.joinpath(self.file).read_text(encoding)
        return Fake_read(self.file)

class TestGetFacetsDict:
    
    def test_get_stored_facets_dict(self, monkeypatch):
        stored_dict = {"campo":"etiqueta"}
        monkeypatch.setattr(iepnb_utils, "_facets_dict", stored_dict)
        #iepnb_utils._facets_dict = stored_dict
        assert iepnb_utils.get_facets_dict() == stored_dict
        
    def test_recover_facets_dict(self, monkeypatch):
        test_dataset = {
            'dataset_fields':[
                {"field_name":"dataset_name1", "label":"dataset_label1"},
                {"field_name":"dataset_name2", "label":"dataset_label2"},
                ],
            "resource_fields":[
                {"field_name":"resource_name1", "label":"resource_label1"},
                {"field_name":"resource_name2", "label":"resource_label2"},
                ]
            }
        result_dataset = { elemento['field_name']:elemento['label'] for nombre,lista in test_dataset.items() for elemento in lista }
        monkeypatch.setattr(iepnb_utils, "_facets_dict", None)
    
        def innerpach(context, data_dict):
            assert context == {}
            assert data_dict == {'type': 'dataset'}
            return test_dataset
    
        def patch(funcion):
            assert funcion == 'scheming_dataset_schema_show'
            return innerpach
    
        monkeypatch.setattr(logic,"get_action", patch)
        
        assert iepnb_utils.get_facets_dict() == result_dataset
        assert iepnb_utils._facets_dict == result_dataset

@patch("ckanext.iepnb.utils.urlopen")
@patch("ckanext.iepnb.utils.iepnb_config")
class TestGetLogoMinisterioAttrs:

    def test_get_stored_attrs_from_config(self, iepnb_config, urlopen):

        iepnb_config.attrs_logo_ministerio="atributos"
        assert iepnb_utils.get_logo_ministerio_attrs() == "atributos"
        
    def test_get_attrs_from_downloaded_page(self, iepnb_config, urlopen):

        iepnb_config.attrs_logo_ministerio = None
        iepnb_config.server_menu="server_menu"

        fake_urlopen_object = Fake_urlopen("demo_main_page_iepnb.txt")
        urlopen.side_effect = fake_urlopen_object.urlopen
        
        response = [
        ("class","imagenMinisterio"),
        ("src","/sites/default/files/2023-04/64351c7630215d49e51c67d7_1024px-Logotipo_del_Ministerio_para_la_TransiciB3n_EcolB3gica_y_el_Reto_DemogrA1fico.svg-p-500.png"),
        ("alt","Logotipo del Ministerio para la transición ecológica y el reto demográfico")
        ]
        
        assert iepnb_utils.get_logo_ministerio_attrs() == response
        assert fake_urlopen_object.url == "server_menu"
        assert iepnb_config.attrs_logo_ministerio == response

# En los test de las funciones del parseador html en vez de testar directamente
# las funciones, como sería lo esperable, he decidido testarlas dejando que sea
# el propio parseador el que las invoque, para asegurarme de que reciben la
# información como se espera.

# Probablemente con un poco más de seguridad en el funcionamiento de HTMLParser no
# sería necesario hacerlo así, pero de momento prefiero hacer el test de esta manera

@pytest.mark.parser_function("handle_starttag", iepnb_utils.iepnb_handle_starttag)
class TestIepnbHandleStarttag(object):
    
    def test_div_without_header_class_doesnt_open_header(self,make_parser_object):

        parser = make_parser_object

        parser.feed('<div class="fake pinocho" custom1="custom_value1" custom2>')

        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == None
        assert parser.footer_counter == False

    def test_div_with_header_class_opens_header(self, make_parser_object):

        parser = make_parser_object

        parser.feed('<div class="fake pinocho header" custom1="custom_value1" custom2>')

        assert parser.header == '<div class="fake pinocho header" custom1="custom_value1" custom2>'
        assert parser.header_counter == 1
        assert parser.footer == None
        assert parser.footer_counter == False

    def test_div_gets_into_opened_header_incrementing_counter(self, make_parser_object):

        parser = make_parser_object
        parser.header = 'fake_header'
        parser.header_counter = 1

        parser.feed('<div class="subdiv">')

        assert parser.header == 'fake_header<div class="subdiv">'
        assert parser.header_counter == 2
        assert parser.footer == None
        assert parser.footer_counter == False
       
    def test_other_open_tags_gets_into_opened_header_leaving_counter(self, make_parser_object):

        parser = make_parser_object
        parser.header = 'fake_header'
        parser.header_counter = 1

        parser.feed('<img src="fuente">')

        assert parser.header == 'fake_header<img src="fuente">'
        assert parser.header_counter == 1
        assert parser.footer == None
        assert parser.footer_counter == False

    def test_footer_tag_opens_footer_with_iepnb_class_added(self, make_parser_object):

        parser = make_parser_object
        parser.header = "fake"
        parser.header_counter = 0

        parser.feed('<footer class="fuente">')

        assert parser.header == "fake"
        assert parser.header_counter == 0
        assert parser.footer == '<footer class="fuente iepnb">'
        assert parser.footer_counter == True

# Los tests que siguen en esta clase se refieren a la forma de operar en caso de
# una página mal formada. Hay que analizar si se prefiere en cada caso lanzar una
# excepción o se prefiere otra acción, y modificar el test en su caso

    def test_new_header_deletes_previous(self, make_parser_object):

        parser = make_parser_object
        parser.header = 'fake_header'
        parser.header_counter = 0

        parser.feed('<div class="fake gepetto header" custom1="custom_value1" custom2>')

        assert parser.header == '<div class="fake gepetto header" custom1="custom_value1" custom2>'
        assert parser.header_counter == 1
        assert parser.footer == None
        assert parser.footer_counter == False

    def test_footer_inside_header_saved_inside_footer_and_header(self, make_parser_object):

        parser = make_parser_object
        parser.header = "fake"
        parser.header_counter = 1
        parser.footer = None
        parser.footer_counter = False

        parser.feed('<footer class="fuente">')
 
        assert parser.header == 'fake<footer class="fuente">'
        assert parser.header_counter == 1
        assert parser.footer == '<footer class="fuente iepnb">'
        assert parser.footer_counter == True

    def test_new_footer_deletes_previous(self, make_parser_object):

        parser = make_parser_object
        parser.footer = "fake_footer"
        parser.footer_counter = False

        parser.feed('<footer class="fuente2">')

        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == '<footer class="fuente2 iepnb">'
        assert parser.footer_counter == True

@pytest.mark.parser_function("handle_endtag",iepnb_utils.iepnb_handle_endtag)
class TestIepnbHandleEndtag(object):

    def test_close_div_doesnt_afect_closed_header_or_footer(self,make_parser_object):

        parser = make_parser_object
#Con el header y el footer cerrados, los /div no afectan a ninguno
        parser.feed('</div>')

        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == None
        assert parser.footer_counter == False
        
    def test_closing_div_decrements_header_div_counter(self,make_parser_object):

        parser = make_parser_object
        parser.header = "fake"
        parser.header_counter=2       
#Una vez abierto el header, los /div van disminuyendo el contador
        parser.feed('</div>')

        assert parser.header == "fake</div>"
        assert parser.header_counter == 1
        assert parser.footer == None
        assert parser.footer_counter == False
    
    def test_closing_div_tags_gets_into_open_footer(self,make_parser_object): 

        parser = make_parser_object
        parser.footer = "fakefooter"
        parser.footer_counter = True
    
#Las etiquetas /div se incorporan en el footer abierto    
        parser.feed('</div>')
        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == "fakefooter</div>"
        assert parser.footer_counter == True

    def test_closing_footer_tag_closes_footer(self,make_parser_object):

        parser = make_parser_object
        parser.footer = "fakefooter"
        parser.footer_counter = True

#La etiqueta /footer cierra el footer
        parser.feed('</footer>')
        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == "fakefooter</footer>"
        assert parser.footer_counter == False

@pytest.mark.parser_function("handle_data",iepnb_utils.iepnb_handle_data)
class TestIepnbHandleData(object):
    def test_doesnt_get_text_outside_header_or_footer(self,make_parser_object):

        parser = make_parser_object
        parser.feed('Fake text')

        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == None
        assert parser.footer_counter == False
    
    def test_gets_text_to_header(self,make_parser_object):

        parser=make_parser_object

        parser.header = "<fake>"
        parser.header_counter = 1
        parser.feed('Fake text')
    
        assert parser.header == "<fake>Fake text"
        assert parser.header_counter == 1
        assert parser.footer == None
        assert parser.footer_counter == False
        
    def test_gets_text_to_footer(self,make_parser_object):

        parser=make_parser_object

        parser.footer = "<fake footer>"
        parser.footer_counter = True
        parser.feed('Fake footer text')
    
        assert parser.header == None
        assert parser.header_counter == 0
        assert parser.footer == "<fake footer>Fake footer text"
        assert parser.footer_counter == True

@pytest.mark.ckan_config("ckan.plugins","plugin1 plugin2 plugin3 plugin4")
class TestPluginDefined(object):
        
    def test_can_find_plugin(self):
        assert iepnb_utils.plugin_defined("plugin1") == True

    def test_cant_find_inexistent_plugin(self):
        assert iepnb_utils.plugin_defined("plugin10") == False

    def test__plugins_defined_changed_after_search_for_existent_plugin(self):
        iepnb_utils.plugin_defined("plugin1")
        assert iepnb_utils._plugins_defined.get("plugin1",None) == True

    def test__plugins_defined_changed_after_search_for_inexistent_plugin(self):
        iepnb_utils.plugin_defined("plugin10")
        assert iepnb_utils._plugins_defined.get("plugin10",None) == False



    