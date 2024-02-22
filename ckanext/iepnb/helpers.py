from ckan.common import json, config, is_flask_request, c, request
from ckan.lib.plugins import DefaultTranslation
from ckan.lib import helpers as ckan_helpers
import ckanext.iepnb.config as iepnb_config
from ckanext.iepnb.utils import *
from urllib.request import urlopen
from urllib.error import HTTPError
from html.parser import HTMLParser
import ckan.logic as logic
from babel import Locale
import logging
from six.moves.urllib.parse import urlencode

from sqlalchemy import Table, select, join, func, and_
from six import text_type
import ckan.plugins as p
import ckan.model as model

logger = logging.getLogger(__name__)
all_helpers = {}

def helper(fn):
    """
    collect helper functions into ckanext.scheming.all_helpers dict
    """
    all_helpers[fn.__name__] = fn
    return fn

@helper
def iepnb_decode_json(cadena):
    """Convierte un texto json en un objeto phyton
    """
    objeto=json.loads(cadena)
    #objeto=cadena    
    return objeto

@helper
def iepnb_breadcrumbs(lang = ''):
    """'Devuelve un texto con el json que contiene las migas de pan.
    Si puede, lo obtiene dinámicamente del servidor iepnb.home, con la ruta path_breadcrumbs.
    Si la ruta no está definida, toma por defecto el valor indicado en iepnb.breadcrumbs
    """
    
    if iepnb_config.path_breadcrumbs == '':
        return iepnb_config.breadcrumbs
    else:
        breadcrumbs_url = iepnb_config.server_menu
        tmp_lang = lang or iepnb_config.locale_default

        breadcrumbs_url += ('/'+tmp_lang+iepnb_config.path_breadcrumbs)
            
        breadcrumbs_page = urlopen(breadcrumbs_url, context=iepnb_config.gcontext)
        breadcrumbs_text_bytes = breadcrumbs_page.read()
        breadcrumbs_text = breadcrumbs_text_bytes.decode("utf-8")
        
        return breadcrumbs_text

@helper        
def iepnb_home():
    """Devuelve el servidor donde está instalado iepnb, configurado en iepnb.server
    """
    return iepnb_config.server_menu

@helper
def iepnb_locale_default():
    """DEvuelve el locale_default de la configuración
    """
    
    return iepnb_config.locale_default

@helper    
def iepnb_popular_tags():
    """Devuelve el número de etiquetas populares que se mostrarán, según iepnb.populat_tags
    """
    
    return iepnb_config.popular_tags

@helper
def iepnb_menu(lang = ''):
    """Busca el texto json con la descripción del menú en iepnb.server
    """
    tmp_lang = lang or iepnb_config.locale_default
    if not iepnb_config.menu:

        iepnb_config.menu={}

    if not iepnb_config.menu.get(tmp_lang, None):

        menu_url = iepnb_config.server_menu
        if tmp_lang == '' or tmp_lang ==iepnb_config.locale_default:
            menu_url += iepnb_config.path_menu
        else:
            menu_url += ('/'+lang+iepnb_config.path_menu)

        logger.debug(u'menu_url ({0}): {0}'.format(tmp_lang, menu_url))

        try:
            menu_page=urlopen(menu_url, context=iepnb_config.gcontext)
        except HTTPError as err:
            logger.warning("No se puede acceder a {0}: {1}".format(menu_url, err.reason))
            if tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
                return iepnb_menu()
            else:
                logger.error("No se puede recuperar el menú por defecto")
        logger.debug(u'menu_url open')
        menu_text_bytes = menu_page.read()
        logger.debug(u'menu_url received')
        iepnb_config.menu[tmp_lang] = menu_text_bytes.decode("utf-8")
    
    return iepnb_config.menu[tmp_lang]
    #return 'https://iepnb-des.tragsatec.es'

@helper
def iepnb_locale_name(lang):
    return Locale.parse(lang).get_display_name(lang)
    

@helper      
def iepnb_to_url_segment(cadena):
    """Obsolete: convierte un literal de nombre de página en un segmento de url según Drupal
    """
    
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    _lcadena = cadena.strip().lower()
    for a, b in replacements:
        _lcadena = _lcadena.replace(a, b)
    _lcadena = _lcadena.replace(" ","-")
    return _lcadena

@helper
def iepnb_organization_name(item):
    '''Returns the name of the organization from its id -> TO DELETE
    '''
    respuesta=item['display_name']
    try:
        org_dic = ckan_helpers.get_organization(item['display_name'])
        if org_dic is not None:
            respuesta=org_dic['name']
        else:
            logger.warning('No se ha podido encontrar el nombre de la organización con id %'.format(item['display_name']))
    except Exception as e:
        logger.error("Excepción al intentar encontrar el nombre de la organización: %".format(e))
    return respuesta

@helper
def iepnb_tag_img_ministerio():
    attrs = get_logo_ministerio_attrs()
    if attrs:
        tag = '<img'
        for x in attrs:
            tag = tag+" " + x[0]
            if x[1]:
                tag = tag + '="' + x[1]+'"'
        tag = tag+'>'
    else:
        tag=iepnb_config.default_logo_ministerio.format(ckan_helpers.url_for_static("/img/Logotipo_Minteco.png"))

    return tag

@helper
def iepnb_get_footer(lang=''):
    tmp_lang = lang or iepnb_config.locale_default
    if not iepnb_config.footer_iepnb.get(tmp_lang, None):
        url = iepnb_config.server_menu + "/"
        page = None
        if lang != iepnb_config.locale_default:
            url += lang
        try:
            page = urlopen(url, context=iepnb_config.gcontext)
        except HTTPError as err:
            logger.warning("No se puede acceder a {0}: {1}".format(url, err.reason))
            if tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
                return iepnb_get_footer()
            else:
                logger.error("No se puede recuperar el pie de página por defecto")
        if page:
            text_bytes=page.read()
            text=text_bytes.decode("utf-8")
            ClassParser=type("ClassParser", (HTMLParser,), {
                "handle_starttag":   iepnb_handle_starttag,
                "handle_endtag":     iepnb_handle_endtag,
                "handle_data":       iepnb_handle_data,
                "footer":            None,
                "header":            None,
                "header_counter":    0,
                "footer_counter":    False
                })
            parser=ClassParser()
            parser.feed(text)
            iepnb_config.footer_iepnb[tmp_lang] = parser.footer

    return iepnb_config.footer_iepnb.get(tmp_lang,'')

@helper
def iepnb_plugin_defined(_plugin):
    return plugin_defined(_plugin)
