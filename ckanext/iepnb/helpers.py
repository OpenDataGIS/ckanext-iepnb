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

from functools import lru_cache


log = logging.getLogger(__name__)
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
    objeto="{}"
    if cadena:
        objeto=json.loads(cadena)
    #objeto=cadena    
    return objeto

@lru_cache(maxsize=100)
def get_breadcrumbs_url(tmp_lang):
    breadcrumbs_url = iepnb_config.server_menu
    if iepnb_config.server_i18n and tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
        return f'{breadcrumbs_url}/{iepnb_config.path_breadcrumbs}/{tmp_lang}'
    return f'{breadcrumbs_url}{iepnb_config.path_breadcrumbs}'

@lru_cache(maxsize=100)
def get_breadcrumbs_from_url(breadcrumbs_url):
    try:
        breadcrumbs_page = urlopen(breadcrumbs_url, context=iepnb_config.gcontext)
        breadcrumbs_text_bytes = breadcrumbs_page.read()
        return breadcrumbs_text_bytes.decode("utf-8")
    except HTTPError as err:
        log.warning(f"No se puede acceder a {breadcrumbs_url}: {err.reason}")
        return None

@helper
def iepnb_breadcrumbs(lang = ''):
    respuesta = iepnb_config.default_breadcrumbs
    if iepnb_config.path_breadcrumbs:
        tmp_lang = lang or iepnb_config.locale_default
        if not tmp_lang in iepnb_config.breadcrumbs:
            tmp_lang = iepnb_config.locale_default
        if not iepnb_config.breadcrumbs[tmp_lang]:
            breadcrumbs_url = get_breadcrumbs_url(tmp_lang)
            respuesta = get_breadcrumbs_from_url(breadcrumbs_url)
            if respuesta is None:
                if tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
                    respuesta = iepnb_breadcrumbs()+"Sin acceso"
                else:
                    log.error("No se puede recuperar el menú por defecto")
                    respuesta = iepnb_config.default_breadcrumbs+"Error html"
            else:
                iepnb_config.breadcrumbs[tmp_lang] = respuesta
    return respuesta

@helper        
def iepnb_home():
    """Devuelve el servidor donde está instalado iepnb, configurado en iepnb.server
    """
    return iepnb_config.server_menu

@helper
def iepnb_server_i18n():
    """Devuelve si el CMS tiene habilitado el 18n de la configuración
    """
    
    return iepnb_config.server_i18n

@helper
def iepnb_root_path():
    """Devuelve el root_path de la configuración
    """
    return p.toolkit.config.get("ckan.root_path", "").replace("/{{LANG}}", "")

@helper
def iepnb_locale_default():
    """Devuelve el locale_default de la configuración
    """
    
    return iepnb_config.locale_default

@helper    
def iepnb_popular_tags():
    """Devuelve el número de etiquetas populares que se mostrarán, según iepnb.popular_tags
    """
    
    return iepnb_config.popular_tags

@helper    
def iepnb_featured_datasets():
    """Devuelve el número de datasets destacados que se mostrarán, según iepnb.featured_datasets
    """
    
    return iepnb_config.featured_datasets

@helper
def iepnb_menu(lang = ''):
    """Busca el texto json con la descripción del menú en iepnb.server
    """
    tmp_lang = lang or iepnb_config.locale_default
    
    if not tmp_lang in iepnb_config.menu:
        tmp_lang = iepnb_config.locale_default

    if not iepnb_config.menu[tmp_lang]:

        menu_url = iepnb_config.server_menu
        if tmp_lang == '' or tmp_lang ==iepnb_config.locale_default:
            menu_url += iepnb_config.path_menu
        else:
            menu_url += ('/'+lang+iepnb_config.path_menu)

        #log.debug(u'menu_url ({0}): {0}'.format(tmp_lang, menu_url))
        
        menu_page = None

        try:
            menu_page=urlopen(menu_url, context=iepnb_config.gcontext)
        except HTTPError as err:
            log.warning("No se puede acceder a {0}: {1}".format(menu_url, err.reason))
            if tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
                return iepnb_menu()
            else:
                log.error("No se puede recuperar el menú por defecto")

        if menu_page:
            #log.debug(u'menu_url open')
            menu_text_bytes = menu_page.read()
            #log.debug(u'menu_url received')
            iepnb_config.menu[tmp_lang] = menu_text_bytes.decode("utf-8")
        else:
            iepnb_config.menu[tmp_lang] = ""
    
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
            log.warning('No se ha podido encontrar el nombre de la organización con id %'.format(item['display_name']))
    except Exception as e:
        log.error("Excepción al intentar encontrar el nombre de la organización: %".format(e))
    return respuesta

@helper
def iepnb_tag_img_ministerio():
    try:
        attrs = get_logo_ministerio_attrs()
        tag = '<img'
        for x in attrs:
            tag = tag+" " + x[0]
            if x[1]:
                tag = tag + '="' + x[1]+'"'
        tag = tag+'>'
    except:
        tag=iepnb_config.default_logo_ministerio.format(ckan_helpers.url_for_static("/img/logo/Logotipo_Minteco.png"))
    return tag

@helper
def iepnb_get_footer(lang=''):
    tmp_lang = lang or iepnb_config.locale_default
    
    if not tmp_lang in iepnb_config.footer_iepnb:
        tmp_lang = iepnb_config.locale_default

    if not iepnb_config.footer_iepnb.get(tmp_lang, None):
        url = iepnb_config.server_menu + "/"
        page = None
        if lang != iepnb_config.locale_default:
            url += lang
        try:
            page = urlopen(url, context=iepnb_config.gcontext)
        except HTTPError as err:
            log.warning("No se puede acceder a {0}: {1}".format(url, err.reason))
            if tmp_lang != '' and tmp_lang != iepnb_config.locale_default:
                return iepnb_get_footer()
            else:
                log.error("No se puede recuperar el pie de página por defecto")
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
