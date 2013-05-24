# coding=utf-8
from time import time, sleep
from django.core.urlresolvers import reverse
from django.template import Context
from django.template import TemplateSyntaxError
from django.template.loader import get_template_from_string
from django.test import TestCase, Client
from django import VERSION as django_version
import viewlet
from ..exceptions import UnknownViewlet
from ..cache import get_cache
from ..conf import settings
from ..loaders import jinja2_loader
from ..loaders.jinja2_loader import get_env

cache = get_cache()
__all__ = ['ViewletTest']


class ViewletTest(TestCase):

    def setUp(self):
        cache.clear()
        settings.VIEWLET_TEMPLATE_ENGINE = 'django'

        @viewlet.viewlet
        def hello_world(context):
            return u'Hello wörld!'

        @viewlet.viewlet
        def hello_name(context, name=u"wurld"):
            return u'Hello %s' % name

        @viewlet.viewlet(template='hello_world.html', cached=False)
        def hello_nocache(context, name="wurld"):
            return {'name': name}

        @viewlet.viewlet(template='hello_world.html', timeout=10)
        def hello_cache(context, name):
            return {
                'name': name,
                'timestamp': time(),
            }

        @viewlet.viewlet(name='hello_new_name', template='hello_world.html', timeout=10)
        def hello_named_world(context, name):
            return {
                'name': name,
            }

        @viewlet.viewlet(template='hello_timestamp.html', timeout=10)
        def hello_cached_timestamp(context, name):
            return {
                'name': name,
                'timestamp': time(),
            }

        @viewlet.viewlet(template='hello_timestamp.html', timeout=None)
        def hello_infinite_cache(context, name):
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

        @viewlet.viewlet(template='hello_strong_world.html', timeout=10)
        def hello_strong(context, name):
            return {
                'name': name
            }
    
    def tearDown(self):
        jinja2_loader._env = None
        settings.VIEWLET_JINJA2_ENVIRONMENT = 'viewlet.loaders.jinja2_loader.create_env'

    def get_django_template(self, source):
        return '\n'.join(('{% load viewlets %}',
                          source))

    def get_jinja_template(self, source):
        settings.VIEWLET_TEMPLATE_ENGINE = 'jinja2'
        return get_env().from_string(source)

    def render(self, source, context=None):
        return get_template_from_string(source).render(Context(context or {})).strip()

    def test_version(self):
        self.assertEqual(viewlet.get_version((1, 2, 3, 'alpha', 1)), '1.2.3a1')
        self.assertEqual(viewlet.get_version((1, 2, 3, 'beta', 2)), '1.2.3b2')
        self.assertEqual(viewlet.get_version((1, 2, 3, 'rc', 3)), '1.2.3c3')
        self.assertEqual(viewlet.get_version((1, 2, 3, 'final', 4)), '1.2.3')

    def test_get_existing_viewlet(self):
        viewlet.get('hello_cache')

    def test_get_non_existing_viewlet(self):
        self.assertRaises(UnknownViewlet, viewlet.get, 'i_do_not_exist')

    def test_empty_decorator(self):
        template = self.get_django_template("<h1>{% viewlet hello_world %}</h1>")
        html1 = self.render(template)
        self.assertEqual(html1, u'<h1>Hello wörld!</h1>')
        html2 = self.render(template)
        sleep(0.01)
        self.assertEqual(html1, html2)

    def test_render_tag(self):
        template = self.get_django_template("<h1>{% viewlet hello_nocache name=viewlet_arg %}</h1>")
        html = self.render(template, {'viewlet_arg': u'wörld'})
        self.assertEqual(html.strip(), u'<h1>Hello wörld!\n</h1>')
        template = self.get_django_template("<h1>{% viewlet unknown_viewlet %}</h1>")
        self.assertRaises(UnknownViewlet, self.render, template)
        template = self.get_django_template("<h1>{% viewlet hello_world name= %}</h1>")
        self.assertRaises(TemplateSyntaxError, self.render, template)

    def test_cached_tag(self):
        template = self.get_django_template("<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertEqual(html1, html2)

    def test_non_cached_tag(self):
        template = self.get_django_template("<h1>{% viewlet hello_non_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertNotEqual(html1, html2)

    def test_cache(self):
        html1 = viewlet.call('hello_cache', None, 'world')
        sleep(0.01)
        html2 = viewlet.call('hello_cache', None, 'world')
        self.assertEquals(html1, html2)

    def test_unicode_cache(self):
        html1 = viewlet.call('hello_cache', None, u'wörld')
        sleep(0.01)
        html2 = viewlet.call('hello_cache', None, u'wörld')
        self.assertEquals(html1, html2)

    def test_refresh(self):
        template = self.get_django_template("<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>")
        html1 = self.render(template)
        sleep(0.01)
        html2 = viewlet.refresh('hello_cached_timestamp', 'world')
        self.assertNotEqual(html1, html2)

    def test_view(self):
        client = Client()
        url = reverse('viewlet', args=['hello_cache'])
        response = client.get(url, {'name': u'wörld'})
        self.assertEqual(response.status_code, 200)
        html = viewlet.call('hello_cache', None, u'wörld')
        self.assertEqual(response.content.decode('utf-8'), html)

    def test_jinja_tag(self):
        template = self.get_jinja_template(u"<h1>{% viewlet 'hello_nocache', viewlet_arg %}</h1>")
        html = template.render({'extra': u'Räksmörgås', 'viewlet_arg': u'wörld'})
        self.assertEqual(html.strip(), u'<h1>RäksmörgåsHello wörld!</h1>')

    def test_custom_jinja2_environment(self):
        env = get_env()
        self.assertEqual(env.optimized, True)
        self.assertEqual(env.autoescape, False)
        settings.VIEWLET_JINJA2_ENVIRONMENT = 'coffin.common.env'
        jinja2_loader._env = None
        env = get_env()
        self.assertEqual(env.optimized, False)
        # Jingo does not support django <= 1.2
        if django_version[:2] > (1, 2):
            settings.VIEWLET_JINJA2_ENVIRONMENT = 'jingo.get_env'
            env = get_env()
            self.assertEqual(env.autoescape, True)

    def test_context_tag(self):
        template = self.get_django_template("<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>")
        self.render(template)
        v = viewlet.get('hello_cached_timestamp')
        cache_key = v._build_cache_key('world')
        viewlet_data = cache.get(cache_key)
        self.assertTrue('name' in viewlet_data)
        self.assertEqual(viewlet_data['name'], 'world')
        self.assertTrue(isinstance(viewlet_data, dict))

    def test_infinite_cache(self):
        template = self.get_django_template("<h1>{% viewlet hello_infinite_cache 'world' %}</h1>")
        self.render(template)
        v = viewlet.get('hello_infinite_cache')
        self.assertEqual(v.timeout, settings.VIEWLET_INFINITE_CACHE_TIMEOUT)

    def test_expire_cache(self):
        v = viewlet.get('hello_cache')
        v.call({}, 'world')
        cache_key = v._build_cache_key('world')
        sleep(0.01)
        self.assertTrue(cache.get(cache_key) is not None)
        v.expire('world')
        self.assertTrue(cache.get(cache_key) is None)

    def test_mark_safe(self):
        # Test django
        template = self.get_django_template("<h1>{% viewlet hello_strong 'wörld' %}</h1>")
        html = self.render(template.strip())
        self.assertEqual(html, u'<h1>Hello <strong>wörld!</strong>\n</h1>')
        # Test jinja2
        template = self.get_jinja_template(u"<h1>{% viewlet 'hello_strong', 'wörld' %}</h1>")
        html = template.render()
        self.assertEqual(html, u'<h1>Hello <strong>wörld!</strong></h1>')

    def test_cached_string(self):
        template = self.get_django_template("<h1>{% viewlet hello_name name='wörld' %}</h1>")
        html = self.render(template)
        self.assertTrue(isinstance(html, unicode))
        v = viewlet.get('hello_name')
        cache_key = v._build_cache_key(u'wörld')
        cached_value = cache.get(cache_key)
        self.assertTrue(isinstance(cached_value, str))

    def test_named(self):
        template = self.get_django_template("<h1>{% viewlet hello_new_name 'wörld' %}</h1>")
        self.render(template)
        self.assertTrue(viewlet.get('hello_new_name') is not None)
