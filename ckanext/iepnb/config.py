proxy = None
gcontext = None

#migas de pan por defecto definidas en el fichero de configuración con iepnb.default_breadcrumbs
default_breadcrumbs = ""

#servidor al que se ha de solicitar el objeto json con el menú y las migas de pan
server_menu = "https://iepnb-des.tragsatec.es"

#path dentro del servidor para solicitar el menu. Va separado para poder intercalar el prefijo de idioma
#se define en el menú ini con epnb.path_menu
path_menu = "/api/menu_items/main"

#Ruta a la descarga de migas de pan del servidor definida en el fichero de configuración con iepnb.path.default_breadcrumbs 
path_breadcrumbs = ""

# número de etiquetas populares para mostrar en la página principal
popular_tags = 3

# lista de campos sobre los que realizar un facetado y etiqueta correspondiente
facets_dict_default = {
        'theme'                 : 'Temas INSPIRE',
        'theme_es'              : 'Theme',
        'dcat_theme'            : 'Resource DCAT theme',
        'dcat_type'             : 'Resource DCAT type',
        'owner_org'             : 'Organization',
        'res_format'            : 'Format',
        'publisher_identifier'  : 'Publisher identifier',
        'publisher_type'        : 'Administration level',
        'frequency'             : 'Update frequency',
        'tag_string'            : 'Tag',
        'tag_uri'               : 'Tag uri',
        'conforms_to'           : 'Conforms to'

    }


default_facet_operator = 'OR'

locale_default = 'es'

schema_info = {}

icons_dir = 'images/icons'

attrs_logo_ministerio = None

default_logo_ministerio='<img class="imagenMinisterio" src="{0}" alt="Logotipo del Ministerio para la transición ecológica y el reto demográfico">'

footer_iepnb = None

menu = None

breadcrumbs = None

stats = False
