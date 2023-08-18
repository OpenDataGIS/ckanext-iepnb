import pytest
from ckan.common import request
from ckan.lib.base import render_snippet
import contextlib

@pytest.mark.usefixtures("with_request_context")
class TestPublisherInfo(object):
    def test_publisher_name_visible(self, monkeypatch):

        monkeypatch.setitem(request.environ, 'CKAN_CURRENT_URL', '/dataset/somedataset')
        html = render_snippet(
            "snippets/publisher_info.html", pkg={"publisher_name": "ACME", "publisher_url": "https://www.acme.com", "publisher_email":"WillyECoyote@acme.com"}
        )
        assert '<a href="/dataset/?publisher_name=ACME" target="_blank"> ACME</a>' in html

    def test_publisher_url_visible(self, monkeypatch):

        monkeypatch.setitem(request.environ, 'CKAN_CURRENT_URL', '/dataset/somedataset')
        html = render_snippet(
            "snippets/publisher_info.html", pkg={"publisher_name": "ACME", "publisher_url": "https://www.acme.com", "publisher_email":"WillyECoyote@acme.com"}
        )
        assert '<a href="https://www.acme.com" target="_blank" class="fa fa-external-link"> https://www.acme.com</a>' in html

    def test_publisher_email_visible(self, monkeypatch):

        monkeypatch.setitem(request.environ, 'CKAN_CURRENT_URL', '/dataset/somedataset')
        html = render_snippet(
            "snippets/publisher_info.html", pkg={"publisher_name": "ACME", "publisher_url": "https://www.acme.com", "publisher_email":"WillyECoyote@acme.com"}
        )
        assert '<a class="fa fa-envelope-o" href="mailto:WillyECoyote@acme.com" target="_blank"> WillyECoyote@acme.com</a>' in html

    def test_publisher_no_url_visible(self, monkeypatch):

        monkeypatch.setitem(request.environ, 'CKAN_CURRENT_URL', '/dataset/somedataset')
        html = render_snippet(
            "snippets/publisher_info.html", pkg={"publisher_name": "ACME", "publisher_email":"WillyECoyote@acme.com"}
        )
        assert 'fa-external-link' not in html

    def test_publisher_no_email_visible(self, monkeypatch):

        monkeypatch.setitem(request.environ, 'CKAN_CURRENT_URL', '/dataset/somedataset')
        html = render_snippet(
            "snippets/publisher_info.html", pkg={"publisher_name": "ACME", "publisher_url": "https://www.acme.com"}
        )
        assert 'href="mailto:' not in html
