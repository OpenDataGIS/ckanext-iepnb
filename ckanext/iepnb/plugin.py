from ckanext.iepnb.iepnb_faceted import IepnbFaceted
from ckanext.iepnb.iepnb_package_controller import IepnbPackageController
import ckanext.iepnb.config as iepnb_config
import ckanext.iepnb.helpers as iepnb_helpers
#from ckanext.iepnb.utils import get_public_dirs
#import ckanext.iepnb.dge_helpers as helpers
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckan.logic as logic
from ckan.lib.plugins import DefaultTranslation
import logging
from urllib.request import urlopen
import ssl
#from ckanext.iepnb.iepnb_action import all_actions 

logger = logging.getLogger(__name__)
server_menu=""
path_menu=""
breadcrumbs=""
gcontext=""
path_breadcrumbs=""
popular_tags=None
proxy=None

    
#def _get_dge_helpers():
#    return {
#        'dge_add_additional_facet_fields': helpers.dge_add_additional_facet_fields,
#        'dge_api_swagger_url': helpers.dge_api_swagger_url,
#        'dge_dataset_display_fields': helpers.dge_dataset_display_fields,
#        'dge_dataset_display_frequency': helpers.dge_dataset_display_frequency,
#        'dge_dataset_display_name': helpers.dge_dataset_display_name,
#        'dge_dataset_field_value': helpers.dge_dataset_field_value,
#        'dge_dataset_tag_field_value': helpers.dge_dataset_tag_field_value,
#        'dge_dataset_tag_list_display_names': helpers.dge_dataset_tag_list_display_names,
#        'dge_default_facet_search_operator': helpers.dge_default_facet_search_operator,
#        'dge_default_facet_sort_by_facet': helpers.dge_default_facet_sort_by_facet,
#        'dge_default_locale': helpers.dge_default_locale,
#        'dge_exported_catalog_files': helpers.dge_exported_catalog_files,
#        'dge_get_dataset_administration_level': helpers.dge_get_dataset_administration_level,
#        'dge_get_dataset_publisher': helpers.dge_get_dataset_publisher,
#        'dge_get_endpoints_menu': helpers.dge_get_endpoints_menu,
#        'dge_get_facet_items_dict': helpers.dge_get_facet_items_dict,
#        'dge_get_organization_administration_level_code': helpers.dge_get_organization_administration_level_code,
#        'dge_get_show_sort_facet': helpers.dge_get_show_sort_facet,
#        'dge_harvest_frequencies': helpers.dge_harvest_frequencies,
#        'dge_is_downloadable_resource': helpers.dge_is_downloadable_resource,
#        'dge_list_reduce_resource_format_label': helpers.dge_list_reduce_resource_format_label,
#        'dge_list_themes': helpers.dge_list_themes,
#        'dge_package_list_for_source': helpers.dge_package_list_for_source,
#        'dge_parse_datetime': helpers.dge_parse_datetime,
#        'dge_render_datetime': helpers.dge_render_datetime,
#        'dge_resource_display_name': helpers.dge_resource_display_name,
#        'dge_resource_display_name_or_desc': helpers.dge_resource_display_name_or_desc,
#        'dge_resource_format_label': helpers.dge_resource_format_label,
#        'dge_sort_alphabetically_resources': helpers.dge_sort_alphabetically_resources,
#        'dge_sparql_yasgui_doc_url': helpers.dge_sparql_yasgui_doc_url,
#        'dge_sparql_yasgui_endpoint': helpers.dge_sparql_yasgui_endpoint,
#        'dge_swagger_doc_url': helpers.dge_swagger_doc_url,
#        'dge_tag_link': helpers.dge_tag_link,
#        'dge_searched_facet_item_filter': helpers.dge_searched_facet_item_filter,
#        'dge_theme_id': helpers.dge_theme_id,
#        'dge_url_for_user_organization': helpers.dge_url_for_user_organization,
#    }
    

class IepnbPlugin(plugins.SingletonPlugin,IepnbFaceted,IepnbPackageController, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.ITranslation)
#    plugins.implements(plugins.IActions)


    # IConfigurer

    def update_config(self, config_):
        
        logger.debug('Doing config...')

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'iepnb')
        toolkit.add_resource('assets', 'ckanext-iepnb')
        toolkit.add_template_directory(config_, 'templates')
              
        iepnb_config.server_menu = config.get('iepnb.server', iepnb_config.server_menu)
        iepnb_config.path_menu = config.get('iepnb.path_menu', iepnb_config.path_menu)
        iepnb_config.breadcrumbs = config.get('iepnb.breadcrumbs', '')
        iepnb_config.proxy = config.get('iepnb.proxy', '')
        iepnb_config.popular_tags= toolkit.asint(config.get('iepnb.popular_tags', 3))
        iepnb_config.locale_default=config.get('ckan.locale_default', iepnb_config.locale_default)
        
        self.facet_load_config(config.get('iepnb.facet_list', '').split())
        self.package_controller_config(config.get('iepnb.default_facet_operator', iepnb_config.default_facet_operator))
        #self.package_controller_config('OR')
        #if breadcrumbs != '':
        #    breadcrumbs = json.loads(breadcrumbs)
        iepnb_config.path_breadcrumbs = config.get('iepnb.path_breadcrumbs', '')
        iepnb_config.gcontext = ssl.SSLContext()
        
    def get_helpers(self):
        logger.debug('Getting helpers...')
        #respuesta= _get_dge_helpers().copy()
        #respuesta.update(dict(all_helpers))
        respuesta=dict(iepnb_helpers.all_helpers)
        return respuesta
    
 #   def get_actions(self):
 #       return all_actions
