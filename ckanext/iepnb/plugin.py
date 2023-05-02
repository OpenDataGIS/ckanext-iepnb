import ckanext.iepnb.config as iepnb_config
import ckanext.iepnb.helpers as iepnb_helpers
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


class IepnbPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
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
