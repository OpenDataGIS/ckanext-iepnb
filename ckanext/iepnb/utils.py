import ckanext.iepnb.config as iepnb_config
import ckan.logic as logic
import ckan.plugins as plugins
from ckan.common import config
from ckan.lib import helpers as ckan_helpers
import logging
from html.parser import HTMLParser
from urllib.request import urlopen
from ckanext.audioview import plugin

logger = logging.getLogger(__name__)

_facets_dict=None
_public_dirs = None
_plugins_defined={}


def get_facets_dict():
    global _facets_dict
    if not _facets_dict:
        _facets_dict= {}

        schema = logic.get_action('scheming_dataset_schema_show')({}, {'type': 'dataset'})

        for item in schema['dataset_fields']:
            _facets_dict[item['field_name']] = item['label']
        for item in schema['resource_fields']:
            _facets_dict[item['field_name']] = item['label']
        #logger.debug("Diccionario etiquetas: {0}".format(_facets_dict))
    return _facets_dict

def get_logo_ministerio_attrs():
    if not iepnb_config.attrs_logo_ministerio:

        page=urlopen(iepnb_config.server_menu, context=iepnb_config.gcontext)
        text_bytes=page.read()
        text=text_bytes.decode("utf-8")
        lineas=[x for x in text.splitlines() if "imagenMinisterio" in x]
        if not lineas:
            return None
        logo_line=lineas[0]
        ClassParser=type("ClassParser", (HTMLParser,), {"handle_starttag": lambda self, tag, attrs: (not tag=="img" or ('imagenMinisterio' not in [x[1] for x in attrs if x[0]=='class']) or setattr(self,"attrs",attrs))})
        parser=ClassParser()
        parser.feed(logo_line)

        if not parser.attrs:
            return None

        iepnb_config.attrs_logo_ministerio=parser.attrs

    return iepnb_config.attrs_logo_ministerio


def iepnb_handle_starttag(obj, tag, attrs):
    '''Starts saving a header (defined as a 'div' block with a 'header' class) in 
    obj.header and a footer (defined as a 'footer' block) in obj.footer with their
    attributes, and starts their counters to keep filling these obj attributes
    with the block contents.
    If there is a footer inside the header, it keeps account of each, but keeping
    also the footer inside the header.

    TO-DO: handle:
        -header inside header
        -repeated header
        -footer inside footer
        -repeated footer
        -header inside footer
        -footer inside header
        
    '''
    
    if obj.header_counter or (tag == "div" and "header" in " ".join([x[1] for x in attrs if x[0] == "class"])):
        if not obj.header_counter:
            obj.header = ""

        if tag == "div":
            obj.header_counter=obj.header_counter+1

        obj.header = obj.header+'<'+tag
        for x in attrs:
            obj.header = obj.header+" "+x[0]
            if x[1]:
                obj.header = obj.header+'="'+x[1]+'"'
        obj.header=obj.header+">"

    if tag == "footer" or obj.footer_counter:
        if not obj.footer_counter:
            obj.footer_counter = True
            obj.footer = ""

        obj.footer=obj.footer+"<"+tag
        for x in attrs:
            obj.footer = obj.footer+" "+x[0]
            if x[1]:
                contenido = x[1]
                if tag == "footer" and x[0] == "class":
                    contenido = contenido+" iepnb"
                obj.footer = obj.footer+'="'+contenido+'"'

        obj.footer = obj.footer+">"

def iepnb_handle_endtag(obj,tag):
    '''keeps filling obj.header and obj.footer and check if this tag closes any
    of these blocks.
    '''

    if obj.header_counter:
        if tag == 'div':
            obj.header_counter=obj.header_counter-1
        obj.header = obj.header+'</'+tag+">"

    if obj.footer_counter:
        if tag == 'footer':
            obj.footer_counter=False
        obj.footer = obj.footer+'</'+tag+">"

def iepnb_handle_data(obj,data):
    '''keeps filling obj.header and obj.footer while they are open (their
    counters are equivalent to true (true or a number greater than 0).
    '''
    if obj.header_counter:
        obj.header=obj.header+data

    if obj.footer_counter:
        if data.strip(" \t\n\r")!="":
            obj.footer=obj.footer+data
            #logger.debug("Datos: ---{0!s}---".format(data))
            #logger.debug("longitud: {}".format(len(data)))
            
def plugin_defined(_plugin):

    if _plugins_defined.get(_plugin) is None:
        _plugins_defined[_plugin] = (_plugin in config.get('ckan.plugins','').split())

    return _plugins_defined[_plugin]
