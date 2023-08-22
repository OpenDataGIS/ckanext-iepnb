import pytest
import types
from html.parser import HTMLParser
from ckan.tests import factories
import ckanext.iepnb.helpers as iepnb_helpers
import ckanext.iepnb.utils as iepnb_utils
import ckanext.iepnb.config as iepnb_config

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
    
class Fake_urlopen:
    ''' Mock para urlopen. Se crea un objeto pasando como parámetro la cadena
    que se quiere que devuelva la llamada a 
    urlopen(url,context).read().decode(encoding), y se asigna la función
    urlopen del objeto creado al side_effect del mock para que se emule el
    funcionamiento del urlopen original. Si no se indica ningún literal,
    devuelve el literal <servidor>:response
    Tras ejecutarlo se puede consultar el url con el que se ha invocado a
    urlopen por la función analizada, dentro del atributo url del objeto creado
    '''

    def __init__(self, _response=None):
        self.response = _response
        self.url = None

    def urlopen(self, _url, context):
        self.url = _url
        return self

    def read(self):
        class Fake_read():
            def __init__(self, _url, _response):
                self.url = _url
                self.response = _response
            def decode(self,encoding):
                if self.response:
                    return self.response
                else:
                    return "{0}:response".format(self.url)
        return Fake_read(self.url, self.response)
    
type_orig=type

def test_iepnb_decode_json():
    json_string = '{"primero":1,"segundo":2}'
    result = iepnb_helpers.iepnb_decode_json(json_string)
    assert str(type(result)) == "<class 'dict'>"
    assert result.get("primero",0) == 1

@patch("ckanext.iepnb.helpers.urlopen")
@patch("ckanext.iepnb.helpers.iepnb_config")
class TestIepnbBreadcrumbs:
    def test_no_path_to_download_defined(self,iepnb_config, urlopen, capsys):
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.locale_default = "lang" 
        iepnb_config.gcontext = ""
        iepnb_config.breadcrumbs = "default_breadcrumbs"
        iepnb_config.path_breadcrumbs = ""
    
        fake_urlopen_object = Fake_urlopen()
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_breadcrumbs() == "default_breadcrumbs"
        urlopen.assert_not_called()

    def test_downloads_unspecified_default_languaje(self,iepnb_config, urlopen, capsys):
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.locale_default = "lang" 
        iepnb_config.gcontext = ""
        iepnb_config.breadcrumbs = "default_breadcrumbs"
        iepnb_config.path_breadcrumbs = "/path_breadcrumbs"
    
        fake_urlopen_object = Fake_urlopen("breadcrumbs")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_breadcrumbs() == "breadcrumbs"
        assert fake_urlopen_object.url =="http://server_menu/lang/path_breadcrumbs"

    def test_downloads_specified_languaje(self,iepnb_config, urlopen, capsys):
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.locale_default = "other_lang" 
        iepnb_config.gcontext = ""
        iepnb_config.breadcrumbs = "default_breadcrumbs"
        iepnb_config.path_breadcrumbs = "/path_breadcrumbs"
    
        fake_urlopen_object = Fake_urlopen("breadcrumbs")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_breadcrumbs(iepnb_config.locale_default) == "breadcrumbs"
        assert fake_urlopen_object.url =="http://server_menu/other_lang/path_breadcrumbs"

@patch("ckanext.iepnb.helpers.urlopen")
@patch("ckanext.iepnb.helpers.iepnb_config")
class TestIepnbMenu:
    def test_downloads_menu_for_unspecified_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = None
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú por defecto")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu() == 'menú por defecto'
        assert iepnb_config.menu.get(iepnb_config.locale_default,None) == 'menú por defecto'
        assert fake_urlopen_object.url == "http://server_menu/path_menu"

    def test_downloads_menu_for_specified_default_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = None
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú por defecto")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu(iepnb_config.locale_default) == 'menú por defecto'
        assert iepnb_config.menu.get(iepnb_config.locale_default,None) == 'menú por defecto'
        assert fake_urlopen_object.url == "http://server_menu/path_menu"

    def test_downloads_menu_for_other_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = None
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú otro lenguaje")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu('other_lang') == "menú otro lenguaje"
        assert iepnb_config.menu.get('other_lang',None) == "menú otro lenguaje"
        assert fake_urlopen_object.url == "http://server_menu/other_lang/path_menu"

    def test_gets_yet_downloaded_menu_for_unspecified_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = {'lang':'menu for lang','other_lang':'menu for other lang'}
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú lenguaje")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu() == "menu for lang"
        urlopen.assert_not_called()
        
    def test_gets_yet_downloaded_menu_for_default_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = {'lang':'menu for lang','other_lang':'menu for other lang'}
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú lenguaje")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu(iepnb_config.locale_default) == "menu for lang"
        urlopen.assert_not_called()
        
    def test_gets_yet_downloaded_menu_for_other_language(self, iepnb_config, urlopen, capsys):
        iepnb_config.locale_default = "lang" 
        iepnb_config.menu = {'lang':'menu for lang','other_lang':'menu for other lang'}
        iepnb_config.server_menu = "http://server_menu"
        iepnb_config.path_menu = "/path_menu"
        iepnb_config.gcontext = ""
    
        fake_urlopen_object = Fake_urlopen("menú otro lenguaje")
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_menu('other_lang') == "menu for other lang"
        urlopen.assert_not_called()

def test_iepnb_locale_name():
    assert iepnb_helpers.iepnb_locale_name('es') == 'español' 

@patch("ckanext.iepnb.helpers.ckan_helpers")
class TestIepnbOrganizationName:
    def test_gets_existent_organization_name(self, ckan_helpers):
        dicionario={'organización':'nombre de organización'}
        ckan_helpers.get_organization =  lambda x: {'name': dicionario.get(x,None)}
        item={'display_name': 'organización'}
        
        assert iepnb_helpers.iepnb_organization_name(item) == 'nombre de organización'

    def test_gets_none_as_nonexistent_organization_name(self, ckan_helpers):
        dicionario={'organización':'nombre de organización'}
        ckan_helpers.get_organization =  lambda x: {'name': dicionario.get(x,None)}
        item={'display_name': 'unexisten organización'}
        
        assert iepnb_helpers.iepnb_organization_name(item) == None

@patch("ckanext.iepnb.helpers.ckan_helpers.url_for_static")
@patch("ckanext.iepnb.helpers.iepnb_config")
@patch("ckanext.iepnb.helpers.get_logo_ministerio_attrs")
class TestIepnbTagImgMinisterio:
    def test_gets_attributes_from_utils(self, get_logo_ministerio_attrs,iepnb_config,url_for_static):
        get_logo_ministerio_attrs.return_value = [('atributo1','valor1'),('atributo2','valor2')]
        iepnb_config.default_logo_ministerio = "*{0}*"
        url_for_static.side_effect = lambda x: "test"
        assert iepnb_helpers.iepnb_tag_img_ministerio() == '<img atributo1="valor1" atributo2="valor2">'
        
    def test_use_default_template(self, get_logo_ministerio_attrs, iepnb_config,url_for_static):
        get_logo_ministerio_attrs.return_value = None
        iepnb_config.default_logo_ministerio = "*{0}*"
        url_for_static.side_effect = lambda x: "test"
        assert iepnb_helpers.iepnb_tag_img_ministerio() == '*test*'
    
@patch("ckanext.iepnb.helpers.urlopen")
class TestIepnbGetFooter:

    def test_gets_stored_footer_for_unspecified_language(self, urlopen, monkeypatch):

        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {'lang':'test','other_lang':'other_test'})
        fake_urlopen_object = Fake_urlopen()
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_get_footer() == 'test'
        urlopen.assert_not_called()

    def test_gets_stored_footer_for_specified_language(self, urlopen, monkeypatch):

        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {'lang':'test','other_lang':'other_test'})
        fake_urlopen_object = Fake_urlopen()
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_get_footer('other_lang') == 'other_test'
        urlopen.assert_not_called()

    def test_gets_stored_footer_for_specified_default_language(self, urlopen, monkeypatch):

        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {'lang':'test','other_lang':'other_test'})
        fake_urlopen_object = Fake_urlopen()
        urlopen.side_effect = fake_urlopen_object.urlopen

        assert iepnb_helpers.iepnb_get_footer('lang') == 'test'
        urlopen.assert_not_called()

    def test_downloads_footer_for_unspecified_language_and_store_it(self, urlopen, monkeypatch):
        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {})
        monkeypatch.setattr(HTMLParser,"feed", lambda obj,x: setattr(obj,"footer",x))
        fake_urlopen_object = Fake_urlopen("default_language")
        urlopen.side_effect = fake_urlopen_object.urlopen
        
        assert iepnb_helpers.iepnb_get_footer() == "default_language"
        urlopen.assert_called()
        assert fake_urlopen_object.url == "http://server_menu/"
        iepnb_config.footer_iepnb["lang"]="default_language"

    def test_downloads_footer_for_specified_language_and_store_it(self, urlopen, monkeypatch):
        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {})
        monkeypatch.setattr(HTMLParser,"feed", lambda obj,x: setattr(obj,"footer",x))
        fake_urlopen_object = Fake_urlopen("specified_language")
        urlopen.side_effect = fake_urlopen_object.urlopen
        
        assert iepnb_helpers.iepnb_get_footer("other_lang") == "specified_language"
        urlopen.assert_called()
        assert fake_urlopen_object.url == "http://server_menu/other_lang"
        iepnb_config.footer_iepnb["lang"]="specified_language"

    def test_downloads_footer_for_specified_default_language_and_store_it(self, urlopen, monkeypatch):
        monkeypatch.setattr(iepnb_config, "gcontext", "")
        monkeypatch.setattr(iepnb_config, "locale_default", "lang")
        monkeypatch.setattr(iepnb_config, "server_menu", "http://server_menu")
        monkeypatch.setattr(iepnb_config, "footer_iepnb", {})
        monkeypatch.setattr(HTMLParser,"feed", lambda obj,x: setattr(obj,"footer",x))
        fake_urlopen_object = Fake_urlopen("specified_default_language")
        urlopen.side_effect = fake_urlopen_object.urlopen
        
        assert iepnb_helpers.iepnb_get_footer("lang") == "specified_default_language"
        urlopen.assert_called()
        assert fake_urlopen_object.url == "http://server_menu/"
        iepnb_config.footer_iepnb["lang"]="specified_default_language"
