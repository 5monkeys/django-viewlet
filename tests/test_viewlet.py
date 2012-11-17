from time import time, sleep
from django.core.cache import cache
from django.contrib.formtools.tests import DummyRequest
from django.template import Context
from django.template.loader import get_template_from_string
from django.test import TestCase
import viewlet
from viewlet.exceptions import ViewletException
from viewlet.utils.jinja2_loader import call_viewlet
from viewlet.views import viewlet_view


class ViewletTest(TestCase):

    def setUp(self):

        cache.clear()

        @viewlet.viewlet
        def hello_world(context):
            return 'Hello world!'

        @viewlet.viewlet(template='hello_world.html', cached=False)
        def hello_nocache(context, name):
            return {'name': name}

        @viewlet.viewlet(template='hello_world.html', timeout=10)
        def hello_cache(context, name):
            return {
                'name': name,
                'timestamp': time(),
            }

        @viewlet.viewlet(template='hello_timestamp.html', timeout=10)
        def hello_cached_timestamp(context, name):
            return {
                'name': name,
                'timestamp': time(),
            }

        @viewlet.viewlet(template='hello_timestamp.html', cached=False)
        def hello_non_cached_timestamp(context, name):
            return {
                'name': name,
                'timestamp': time(),
            }

    def get_template(self, source):
        return '\n'.join(('{% load viewlets %}',
                          source))

    def render(self, source, context=None):
        return get_template_from_string(source).render(Context(context or {})).strip()

    def test_get_existing_viewlet(self):
        viewlet.get('hello_cache')

    def test_get_non_existing_viewlet(self):
        self.assertRaises(ViewletException, viewlet.get, 'i_do_not_exist')

    def test_empty_decorator(self):
        template = self.get_template("<h1>{% viewlet hello_world %}</h1>")
        html = self.render(template)
        self.assertEqual(html, '<h1>Hello world!</h1>')

    def test_render_tag(self):
        template = self.get_template("<h1>{% viewlet hello_nocache 'world' %}</h1>")
        html = self.render(template)
        self.assertEqual(html.strip(), '<h1>Hello world!</h1>')

    def test_cached_tag(self):
        template = self.get_template("<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertEqual(html1, html2)

    def test_non_cached_tag(self):
        template = self.get_template("<h1>{% viewlet hello_non_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertNotEqual(html1, html2)

    def test_cache(self):
        html1 = viewlet.call('hello_cache', None, 'world')
        sleep(0.01)
        html2 = viewlet.call('hello_cache', None, 'world')
        self.assertEquals(html1, html2)

    def test_refresh(self):
        template = self.get_template("<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = viewlet.refresh('hello_cached_timestamp', 'world')
        self.assertNotEqual(html1, html2)

    def test_view(self):
        request = DummyRequest()
        request.GET['name'] = ('world',)
        response = viewlet_view(request, 'hello_cache')
        html = viewlet.call('hello_cache', None, 'world')
        self.assertEqual(response.content, html)

    def test_jinja_tag(self):
        html = call_viewlet({}, 'hello_nocache', 'world')
        self.assertEqual(html.strip(), 'Hello world!')
