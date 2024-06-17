proxy = None
gcontext = None

#migas de pan por defecto definidas en el fichero de configuración con iepnb.default_breadcrumbs
default_breadcrumbs = ""

#servidor al que se ha de solicitar el objeto json con el menú y las migas de pan
server_menu = "https://iepnb-des.tragsatec.es"

#sí el servidor tiene habilitado i18n, para aplicar las breadcrumbs correctamente. False por defecto
server_i18n = False

#path dentro del servidor para solicitar el menu. Va separado para poder intercalar el prefijo de idioma
#se define en el menú ini con epnb.path_menu
path_menu = "/api/menu_items/main"

#Ruta a la descarga de migas de pan del servidor definida en el fichero de configuración con iepnb.path.default_breadcrumbs 
path_breadcrumbs = ""

# número de etiquetas populares para mostrar en la página principal
popular_tags = 3

# número de datasets destacados para mostrar en la página principal
featured_datasets = 4

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

# Vocabs
IEPNB_DEFAULT_DATASET_SCHEMA_NAME = "dataset"
SCHEMINGDCAT_IEPNB_KEYWORDS_VOCAB = "keyword_iepnb"

static_logos = {
    "logo_footer_prtr": "/img/logo/miteco-prtr_1.png",
    "logo_ministerio": "/img/logo/Logotipo_Minteco.png",
    "logo_iepnb": "/img/logo/logoIEPNB.png",
    "logo_footer_ue": "/img/logo/financiacion_UE.png",
    "logo_footer_minbn": "/img/logo/logo_ministerio_bn",
}

# Dataset default values
IEPNB_HARVESTER_MD_CONFIG = {
    'access_rights': 'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations',
    'conformance': [
        'http://inspire.ec.europa.eu/documents/inspire-metadata-regulation','http://inspire.ec.europa.eu/documents/commission-regulation-eu-no-13122014-10-december-2014-amending-regulation-eu-no-10892010-0'
    ],
    'author': 'ckanext-schemingdcat',
    'author_email': 'admin@{ckan_instance}',
    'author_url': '{ckan_instance}/organization/test',
    'author_uri': '{ckan_instance}/organization/test',
    'contact_name': 'Área de Banco de Datos de la Naturaleza. Dirección General Biodiversidad, Bosques y Desertificación. Ministerio para la Transición Ecológica y el Reto Demográfico',
    'contact_email': 'buzon-bdatos@miteco.es',
    'contact_url': 'https://www.miteco.gob.es/',
    'contact_uri': 'http://datos.gob.es/recurso/sector-publico/org/Organismo/E05068001',
    'dcat_type': {
        'series': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/series',
        'dataset': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset',
        'spatial_data_service': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/service',
        'default': 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/dataset',
        'collection': 'http://purl.org/dc/dcmitype/Collection',
        'event': 'http://purl.org/dc/dcmitype/Event',
        'image': 'http://purl.org/dc/dcmitype/Image',
        'still_image': 'http://purl.org/dc/dcmitype/StillImage',
        'moving_image': 'http://purl.org/dc/dcmitype/MovingImage',
        'physical_object': 'http://purl.org/dc/dcmitype/PhysicalObject',
        'interactive_resource': 'http://purl.org/dc/dcmitype/InteractiveResource',
        'service': 'http://purl.org/dc/dcmitype/Service',
        'sound': 'http://purl.org/dc/dcmitype/Sound',
        'software': 'http://purl.org/dc/dcmitype/Software',
        'text': 'http://purl.org/dc/dcmitype/Text',
    },
    'encoding': 'UTF-8',
    'frequency' : 'http://publications.europa.eu/resource/authority/frequency/UNKNOWN',
    'inspireid_theme': 'HB',
    'language': 'http://publications.europa.eu/resource/authority/language/ENG',
    'license': 'http://creativecommons.org/licenses/by/4.0/',
    'license_id': 'cc-by',
    'lineage_process_steps': 'ckanext-schemingdcat lineage process steps.',
    'maintainer': 'ckanext-schemingdcat',
    'maintainer_email': 'admin@{ckan_instance}',
    'maintainer_url': '{ckan_instance}/organization/test',
    'maintainer_uri': '{ckan_instance}/organization/test',
    'metadata_profile': [
        "http://semiceu.github.io/GeoDCAT-AP/releases/2.0.0","http://inspire.ec.europa.eu/document-tags/metadata"
    ],
    'notes_translated': {
        'es': 'Metadatos del conjunto de datos',
        'en': 'Dataset metadata.'
    },
    'provenance': 'ckanext-schemingdcat provenance statement.',
    'publisher_name': 'Área de Banco de Datos de la Naturaleza. Dirección General Biodiversidad, Bosques y Desertificación. Ministerio para la Transición Ecológica y el Reto Demográfico',
    'publisher_email': 'buzon-bdatos@miteco.es',
    'publisher_url': 'https://www.miteco.gob.es/',
    'publisher_identifier': 'http://datos.gob.es/recurso/sector-publico/org/Organismo/E05068001',
    'publisher_uri': 'https://iepnb.es/catalogo/organization/iepnb',
    'publisher_type': 'http://purl.org/adms/publishertype/NationalAuthority',
    'reference_system': 'http://www.opengis.net/def/crs/EPSG/0/4258',
    'representation_type': {
        'wfs': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'wcs': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/grid',
        'default': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'grid': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/grid',
        'vector': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/vector',
        'textTable': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/textTable',
        'tin': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/tin',
        'stereoModel': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/stereoModel',
        'video': 'http://inspire.ec.europa.eu/metadata-codelist/SpatialRepresentationType/video',
    },
    'resources': {
        'availability': 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE',
        'name': {
            'es': 'Distribución {format}',
            'en': 'Distribution {format}'
        },
    },
    'rights': 'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations',
    'spatial': None,
    'spatial_uri': 'http://datos.gob.es/recurso/sector-publico/territorio/Pais/España',
    'status': 'http://purl.org/adms/status/UnderDevelopment',
    'temporal_start': None,
    'temporal_end': None,
    'theme': 'http://inspire.ec.europa.eu/theme/hb',
    'theme_es': 'http://datos.gob.es/kos/sector-publico/sector/medio-ambiente',
    'theme_eu': 'http://publications.europa.eu/resource/authority/data-theme/ENVI',
    'topic': 'http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/biota',
    'valid': None
}

IEPNB_PUBLISHER_TYPES = {
    'national_authority': {
        'label': 'ministerio',
        'value': 'http://purl.org/adms/publishertype/NationalAuthority'
    },
    'regional_authority': {
        'label': 'consejeria',
        'value': 'http://purl.org/adms/publishertype/RegionalAuthority'
    },
    'local_authority': {
        'label': 'concejalia',
        'value': 'http://purl.org/adms/publishertype/LocalAuthority'
    }
}