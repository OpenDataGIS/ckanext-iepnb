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
def iepnb_default_facet_search_operator():
    '''Returns the default facet search operator: AND/OR 
    '''
    facet_operator = iepnb_config.default_facet_operator #config.get('ckanext.dge.facet.default.search.operator', 'AND')
    if facet_operator and (facet_operator.upper() == 'AND' or facet_operator.upper() == 'OR'):
        facet_operator = facet_operator.upper()
    else:
        facet_operator = 'AND'
    return facet_operator

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
def iepnb_get_facet_class(name,item):
    respuesta=""
    if name=="theme":
        respuesta=item.split('/')[-1].lower()
    elif name=="theme_es":
        respuesta=respuesta=item.split('/')[-1].lower()
        
    return respuesta


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

@helper
def iepnb_organization_name(item):
    '''Returns the name of the organization from its id
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
def iepnb_get_facet_label(facet):    
    return get_facets_dict[facet]
    
@helper
def iepnb_get_facet_items_dict(
        facet, search_facets=None, limit=None, exclude_active=False, scheming_choices=None):
    '''Return the list of unselected facet items for the given facet, sorted
    by count.

    Returns the list of unselected facet contraints or facet items (e.g. tag
    names like "russian" or "tolstoy") for the given search facet (e.g.
    "tags"), sorted by facet item count (i.e. the number of search results that
    match each facet item).

    Reads the complete list of facet items for the given facet from
    c.search_facets, and filters out the facet items that the user has already
    selected.
    
    List of facet items are ordered acording the faccet_sort parameter

    Arguments:
    facet -- the name of the facet to filter.
    search_facets -- dict with search facets(c.search_facets in Pylons)
    limit -- the max. number of facet items to return.
    exclude_active -- only return unselected facets.
    scheming_choices -- scheming choices to use to get label from value.

    '''
    
    logger.debug("Returning facets for: {0}".format(facet))
    order="default"
    if search_facets is None:
        search_facets = getattr(c, u'search_facets', None)

    if not search_facets \
       or not isinstance(search_facets, dict) \
       or not search_facets.get(facet, {}).get('items'):
        return []
    
    facets = []
    for facet_item in search_facets.get(facet)['items']:
        if scheming_choices:
            facet_item['label']=scheming_choices_label(scheming_choices,facet_item['name'])
        else:
            facet_item['label']=facet_item['display_name']
        if not len(facet_item['name'].strip()):
            continue
        params_items = request.params.items(multi=True) \
            if is_flask_request() else request.params.items()
        if not (facet, facet_item['name']) in params_items:
            facets.append(dict(active=False, **facet_item))
        elif not exclude_active:
            facets.append(dict(active=True, **facet_item))
            
        #logger.debug("params: {0}:{1}".format(facet,request.params.getlist("_%s_sort" % facet)))
        order_lst=request.params.getlist("_%s_sort" % facet)
        if len(order_lst):
            order=order_lst[0]
    # Sort descendingly by count and ascendingly by case-sensitive display name
    #facets.sort(key=lambda it: (-it['count'], it['display_name'].lower()))
    if order=="name":
        facets.sort(key=lambda it: (it['label']))
    elif order=="name_r":
        facets.sort(key=lambda it: (it['label']),reverse=True)
    elif order=="count":
        facets.sort(key=lambda it: (it['count']),reverse=True)
    elif order=="count_r":
        facets.sort(key=lambda it: (it['count']))
    else:
        facets.sort(key=lambda it: (-it['count'], it['label'].lower()))
        
    if hasattr(c, 'search_facets_limits'):
        if c.search_facets_limits and limit is None:
            limit = c.search_facets_limits.get(facet)
    # zero treated as infinite for hysterical raisins
    if limit is not None and limit > 0:
        return facets[:limit]
    return facets

@helper
def iepnb_new_order_url(name,orden):
    '''Returns a url with the order parameter for the given facet and concept to use
    Based in the actual order it rotates ciclically from no order->direct order->inverse order over the given concept
    Arguments:
    name -- the name of the facet to order.
    orden -- the concept (name or count) that will be used to order
    
    '''
    old_order=None
    param="_%s_sort" % name
    order_lst=request.params.getlist(param)
    new_param=None
    
    controller = getattr(c, 'controller', False) or request.blueprint
    action = getattr(c, 'action', False) or p.toolkit.get_endpoint()[1]
    extras = {}
    url = ckan_helpers.url_for(controller=controller, action=action, **extras)

    
    if len(order_lst):
        old_order=order_lst[0]
    
    if orden=="name":
        if old_order=="name":
            new_param=(param,"name_r")
        elif old_order=="name_r":
            pass
        else:
            new_param=(param,"name")
    if orden=="count":
        if old_order=="count":
            new_param=(param,"count_r")
        elif old_order=="count_r":
            pass
        else:
            new_param=(param,"count")
            
    params_items = request.params.items(multi=True) \
        if is_flask_request() else request.params.items()
    params_nopage = [
        (k, v) for k, v in params_items
        if k != param
    ]
    
    if new_param:
        params_nopage.append(new_param)
    if params_nopage:    
        url=url + u'?' + urlencode(params_nopage)
           
    return url

@helper
def iepnb_schema_get_icons_dir(field):
    """
    :param field: scheming field definition
    :returns: defined icons directory or None if not found.
    """
    
    if field:
        if 'icons_dir' in field:
            return field['icons_dir']
        
        if 'field_name' in field:
            dir = iepnb_config.icons_dir + '/' + field['field_name']
            if public_dir_exists(dir):  
                return dir
        logger.debug("No hay directorio para ".format(field['field_name']))
    return None
    
@helper
def iepnb_schema_get_no_icon(field):
    """
    :param field: scheming field definition
    :returns: defined icons directory or None if not found.
    """
    if 'no_icon' in field:
        return field['no_icon']

@helper
def iepnb_schema_icon(choice, dir=None):
    """ Returns path for icon for the item
    :param choice: Choice selected for field
    :param dir: Path to search for icon
    
    :returns: Relative url to icon
    """
    
    extensiones=['.svg','.png','jpg','gif']
    nombre=None
    logger.debug("Busco icono para {0}".format(choice))
    if 'icon' in choice:
        return (dir+"/" if dir else "") + choice['icon']
    cadena=choice['value'].split('/')

    if len(cadena)==1:
        nombre=cadena[-1].lower()
    else:
        nombre=cadena[-2].lower()+'/'+cadena[-1].lower()
    
    url_path=(dir+"/" if dir else "") + nombre
    
    for extension in extensiones:
        if public_file_exists(url_path+extension):
            return url_path+extension
    
    return None

@helper
def iepnb_get_choice_dic(field, value):
    """Gets whole choice item for the given value in field
    :param field: scheming field to look for choice item into
    :param value: option item value
    
    :returns: The whole option item in scheming
    """
    if field and ('choices' in field):
        logger.debug("Busco {0} en {1}".format(value,field['choices']))
        for choice in field['choices']:
            if choice['value']==value:
                return choice
    
    return None


