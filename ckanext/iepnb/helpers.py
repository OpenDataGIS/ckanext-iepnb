from ckan.common import json, config, is_flask_request, c, request
from ckan.lib.plugins import DefaultTranslation
from ckan.lib import helpers as ckan_helpers
import ckanext.iepnb.config as iepnb_config
from ckanext.iepnb.utils import get_facets_dict, public_file_exists, public_dir_exists
from ckanext.scheming.helpers import scheming_choices_label
from urllib.request import urlopen
import ckan.logic as logic
import logging
from six.moves.urllib.parse import urlencode



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
        if lang == '' or lang =='es':
            breadcrumbs_url += path_breadcrumbs
        else:
            breadcrumbs_url += ('/'+lang+path_breadcrumbs)
            
        logger.debug(u'breadcrumbs_url {0}'.format(iepnb_config.menu_url))
        
        breadcrumbs_page=urlopen(breadcrumbs_url, context=gcontext)
        breadcrumbs_text_bytes = breadcrumbs_page.read()
        breadcrumbs_text = breadcrumbs_text_bytes.decode("utf-8")
        
        return breadcrumbs_text

@helper        
def iepnb_home():
    """Devuelve el servidor donde está instalado ckan, configurado en ckan.site_url
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
    menu_url=iepnb_config.server_menu
    if lang == '' or lang =='es':
        menu_url += iepnb_config.path_menu
    else:
        menu_url += ('/'+lang+path_menu)
        
    logger.debug(u'menu_url: {0}'.format(menu_url))
        
    menu_page=urlopen(menu_url, context=iepnb_config.gcontext)
    logger.debug(u'menu_url open')
    menu_text_bytes = menu_page.read()
    logger.debug(u'menu_url received')
    menu_text = menu_text_bytes.decode("utf-8")
    
    
    return menu_text
    #return 'https://iepnb-des.tragsatec.es'
    
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
