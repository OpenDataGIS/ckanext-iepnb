# encoding: utf-8

import pytest
import six
from ckan.lib.helpers import url_for
from bs4 import BeautifulSoup
import ckanext.iepnb.helpers as iepnb_helpers
import ckanext.iepnb.utils as iepnb_utils

from ckan.tests import factories

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


#@pytest.mark.usefixtures("with_request_context")
class TestHome(object):
    
    def init(self,monkeypatch):
        #patch every helper which does a network connection
        menu = '''[
           {
              "title":"Nuestros datos",
              "relative":"/nuestros-datos",
              "uri":"node/88",
              "below":[{
                 "title":"Catálogo",
                 "relative":"/catalogo",
                 "uri":"node/88"                 
              }]
           },
           {
              "title":"Menu 1",
              "relative":"/menu_1",
              "uri":"node/menu_1",
              "below":[{
                 "title":"Submenu 1 1",
                 "relative":"/submenu_1_1",
                 "uri":"node/submenu_1_1"                 
              },
              {
                 "title":"Submenu 1 2",
                 "relative":"/submenu_1_2",
                 "uri":"node/submenu_1_2"                 
              }]
           },
           {
              "title":"Menu 2",
              "relative":"/menu_2",
              "uri":"node/menu_2",
              "below":[{
                 "title":"Submenu 2 1",
                 "relative":"/submenu_2_1",
                 "uri":"node/submenu_2_1"                 
              },
              {
                 "title":"Submenu 2 2",
                 "relative":"/submenu_2_2",
                 "uri":"node/submenu_2_2"                 
              }]
           }

        ]
        '''
        
        breadcrumbs = '''[
        {"title":"Nuestros datos","description":"Nuestros datos", "relative":"/nuestros-datos"},
        {"title":"Catálogo de datos","description":"Catálogo de datos", "relative":"/catalogo"}
        ]
        '''
        
        self.footer = "<footer>FAKE FOOTER</footer>"
        monkeypatch.setattr("ckan.plugins.toolkit.h.iepnb_breadcrumbs", lambda x: breadcrumbs)
        
        monkeypatch.setattr("ckan.plugins.toolkit.h.iepnb_tag_img_ministerio", lambda: '<img src="/fake_img.png"/>')
        
        monkeypatch.setattr("ckanext.iepnb.helpers.iepnb_tag_img_ministerio", lambda: '<img src="/fake_img.png"/>')
        monkeypatch.setattr("ckan.plugins.toolkit.h.iepnb_menu", lambda x: menu)
        
        monkeypatch.setattr("ckan.plugins.toolkit.h.iepnb_get_footer", lambda x: self.footer)
        
        
    def test_home_renders(self, monkeypatch, app):
        self.init(monkeypatch)
        response = app.get(url_for("home.index"))
        assert "Catálogo de datos" in response.body

    def ntest_template_head_end(self, app):
        # test-core.ini sets ckan.template_head_end to this:
        test_link = (
            '<link rel="stylesheet" href="TEST_TEMPLATE_HEAD_END.css" type="text/css">'
        )
        response = app.get(url_for("home.index"))
        assert test_link in response.body
        
    def test_iepnb_logo(self, monkeypatch, app):
        self.init(monkeypatch)
        response = app.get(url_for("home.index"))
        html = BeautifulSoup(response.body)
        assert '<img src="/fake_img.png"/>' in str(html.find("div",class_="logoGobierno"))

    def test_iepnb_menu_nuestros_datos(self, monkeypatch, app):
        self.init(monkeypatch)
        response = app.get(url_for("home.index"))
        html = BeautifulSoup(response.body)
        li_item = html.find("ul",attrs={"aria-labelledby":"submenu"}).find("li",class_="active")
        link = li_item.find("a",class_="dropdown-toggle")
        sub_item = li_item.find("div",class_="dropdown-menu")
        
        assert 'href="/nuestros-datos"' in str(link)
        assert "Nuestros datos" in link.string
        assert 'href="/catalogo"' in str(sub_item.find("a",class_="active"))
        assert "Catálogo" in sub_item.find("a",class_="active").string

    def test_iepnb_menu_other_items(self, monkeypatch, app):
        self.init(monkeypatch)
        response = app.get(url_for("home.index"))
        html = BeautifulSoup(response.body)
        
        #Recojo los 'li' del menú
        li_items = html.find("ul",attrs = {"aria-labelledby":"submenu"}).find_all("li")
        
        #Extraigo los enlaces principales
        links = [y for x in li_items if len(x) for y in x.find_all("a", class_="nav-link") if len(y)]
        
        #Selecciono el enlace titulado "Menu 1" (en una lista)
        link =[x for x in links if "Menu 1" in x]
        
        #Compruebo que solo hay un enlace titulado Menu 1
        assert len(link) == 1
        assert "Menu 1" in str(link[0])
        
        #Compruebo que enlaza a donde debe
        assert "/menu_1" in str (link[0])
        
        #Del li con el enlace a /menu_1 extraigo los submenús
        subdiv = [x.find("div",class_="dropdown-menu") for x in li_items if x.find("a",href="/menu_1")]
        
        assert len(subdiv) == 1
        
        #Extraigo los enlaces del submenu, y compruebo que están los correctos y en su orden
        sublinks = subdiv[0].find_all("a")
        
        assert len(sublinks) == 2

        assert 'href="/submenu_1_1"' in str(sublinks[0])
        assert 'Submenu 1 1' == sublinks[0].string
        
        assert 'href="/submenu_1_2"' in str(sublinks[1])
        assert 'Submenu 1 2' == sublinks[1].string
        

    def test_template_footer_end(self, monkeypatch, app):
        self.init(monkeypatch)

        response = app.get(url_for("home.index"))
        assert self.footer in response.body

    @pytest.mark.usefixtures("clean_db")
    def ntest_email_address_no_nag(self, app):
        user = factories.User(email="filled_in@nicely.com")
        env = {"REMOTE_USER": six.ensure_str(user["name"])}

        response = app.get(url=url_for("home.index"), extra_environ=env)

        assert "add your email address" not in response

@pytest.mark.usefixtures("with_request_context")
class nTestI18nURLs(object):
    def test_right_urls_are_rendered_on_language_selector(self, app):

        response = app.get(url_for("home.index"))
        html = BeautifulSoup(response.body)

        select = html.find("div", class_="language_switch")
        assert select != None
        for option in select.find_all("li"):
            if option.string == u"English":
                assert option["hreflang"] == "en"
            elif option.string == u"español":
                assert option["value"] == "es"
            elif option.string == u"catalan":
                assert option["value"] == "ca"
            elif option.string == u"galego":
                assert option["value"] == "gl"
            elif option.string == u"euskera":
                assert option["value"] == "eu"

    def ntest_default_english_option_is_selected_on_language_selector(
        self, app
    ):
        response = app.get(url_for("home.index"))
        html = BeautifulSoup(response.body)

        select = html.find(id="field-lang-select")
        for option in select.find_all("option"):
            if option["value"] == "/en/":
                assert option["selected"] == "selected"
            else:
                assert not option.has_attr("selected")

    def ntest_right_option_is_selected_on_language_selector(self, app):
        response = app.get(url_for("home.index", locale="ca"))
        html = BeautifulSoup(response.body)

        select = html.find(id="field-lang-select")
        for option in select.find_all("option"):
            if option["value"] == "/ca/":
                assert option["selected"] == "selected"
            else:
                assert not option.has_attr("selected")

    def ntest_redirects_legacy_locales(self, app):
        locales_mapping = [
            ('zh_TW', 'zh_Hant_TW'),
            ('zh_CN', 'zh_Hans_CN'),
        ]

        for locale in locales_mapping:

            legacy_locale = locale[0]
            new_locale = locale[1]

            response = app.get('/{}/'.format(legacy_locale), follow_redirects=False)

            assert response.status_code == 308
            assert (
                response.headers['Location'] ==
                'http://test.ckan.net/{}'.format(new_locale)
            )

            response = app.get('/{}/dataset'.format(legacy_locale), follow_redirects=False)

            assert response.status_code == 308
            assert (
                response.headers['Location'] ==
                'http://test.ckan.net/{}/dataset'.format(new_locale)
            )