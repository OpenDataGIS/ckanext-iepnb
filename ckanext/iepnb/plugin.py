import ckanext.iepnb.config as iepnb_config
import ckanext.iepnb.helpers as iepnb_helpers
import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckan.logic as logic
from ckan.lib.plugins import DefaultTranslation
import logging
from urllib.request import urlopen
import ssl

logger = logging.getLogger(__name__)

class IepnbPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)

    # IConfigurer

    def update_config(self, config_):

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'iepnb')
        toolkit.add_resource('assets', 'ckanext-iepnb')
        toolkit.add_template_directory(config_, 'templates')
              
        iepnb_config.server_menu = config.get('iepnb.server', iepnb_config.server_menu)
        iepnb_config.path_menu = config.get('iepnb.path_menu', iepnb_config.path_menu)
        iepnb_config.default_breadcrumbs = config.get('iepnb.breadcrumbs', '')
        iepnb_config.proxy = config.get('iepnb.proxy', '')
        iepnb_config.popular_tags = toolkit.asint(config.get('iepnb.popular_tags', 3))
        iepnb_config.locale_default = config.get('ckan.locale_default', iepnb_config.locale_default)
        
        iepnb_config.path_breadcrumbs = config.get('iepnb.path_breadcrumbs', '')
        iepnb_config.gcontext = ssl.SSLContext()
        
        iepnb_config.stats = ('stats' in config.get('ckan.plugins','').split())
        
        languages = config.get('ckan.locales_offered',iepnb_config.locale_default)
        iepnb_config.menu = {}
        iepnb_config.footer_iepnb = {}
        iepnb_config.breadcrumbs = {}
        for language in languages.split():
            iepnb_config.menu[language] = None
            iepnb_config.footer_iepnb[language] = None
            iepnb_config.breadcrumbs[language] = None
        
        
    
    # ITemplateHelper    
    def get_helpers(self):

        respuesta=dict(iepnb_helpers.all_helpers)
        return respuesta
    
 #   def get_actions(self):
 #       return all_actions
