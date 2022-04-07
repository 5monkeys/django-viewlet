import importlib
import logging
from time import sleep, time
from unittest import skipIf

import django
import django.conf
import six
from django.template import TemplateSyntaxError, engines
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .. import (
    cache as cache_m,
    call,
    conf,
    exceptions,
    get,
    get_version,
    library,
    models,
    refresh,
    viewlet,
)
from ..cache import get_cache, make_key_args_join
from ..conf import settings
from ..exceptions import UnknownViewlet
from ..loaders import jinja2_loader
from ..loaders.jinja2_loader import get_env

cache = get_cache()

__all__ = ["ViewletTest", "ViewletCacheBackendTest", "ViewletKeyTest"]


def get_template_from_string(template_code):
    return engines["django"].from_string(template_code)


class ViewletTest(TestCase):
    def setUp(self):
        cache.clear()
        settings.VIEWLET_TEMPLATE_ENGINE = "django"

        @viewlet
        def hello_world(context):
            return "Hello wörld!"

        @viewlet
        def hello_name(context, name="wurld"):
            return "Hello %s" % name

        @viewlet(template="hello_world.html", timeout=0)
        def hello_nocache(context, name="wurld"):
            return {"name": name}

        @viewlet(template="hello_world.html", timeout=10)
        def hello_cache(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

        @viewlet(name="hello_new_name", template="hello_world.html", timeout=10)
        def hello_named_world(context, name):
            return {
                "name": name,
            }

        @viewlet(template="hello_timestamp.html", timeout=10)
        def hello_cached_timestamp(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

        self.hello_cached_timestamp = hello_cached_timestamp

        @viewlet(template="hello_timestamp.html", timeout=None)
        def hello_infinite_cache(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

        @viewlet(template="hello_timestamp.html", timeout=0)
        def hello_non_cached_timestamp(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

        @viewlet(template="hello_strong_world.html", timeout=10)
        def hello_strong(context, name):
            return {"name": name}

        @viewlet(template="hello_request.html", timeout=0)
        def hello_request(context, greeting):
            return {"greeting": greeting}

        @viewlet(template="hello_from_dir.html", timeout=0)
        def hello_from_dir(context, greeting):
            return {"greeting": greeting}

        @viewlet(timeout=0)
        def hello_render_to_string(context):
            from django.template.loader import render_to_string

            context["greeting"] = "Hello"
            return render_to_string("hello_request.html", context)

        self.tail = "\n"

    def tearDown(self):
        jinja2_loader._env = None
        settings.VIEWLET_JINJA2_ENVIRONMENT = "viewlet.loaders.jinja2_loader.create_env"

    def get_django_template(self, source):
        return "\n".join(("{% load viewlets %}", source))

    def get_jinja_template(self, source):
        with override_settings(TEMPLATES=django.conf.settings.JINJA2_TEMPLATES):
            from django.template import engines

            return engines["jinja2"].from_string(source)

    def render(self, source, context=None, request=None):
        kwargs = {"context": context or {}, "request": request}

        return get_template_from_string(source).render(**kwargs).strip()

    def test_version(self):
        self.assertEqual(get_version((1, 2, 3, "alpha", 1)), "1.2.3a1")
        self.assertEqual(get_version((1, 2, 3, "beta", 2)), "1.2.3b2")
        self.assertEqual(get_version((1, 2, 3, "rc", 3)), "1.2.3c3")
        self.assertEqual(get_version((1, 2, 3, "final", 4)), "1.2.3")

    def test_get_existing_viewlet(self):
        get("hello_cache")

    def test_get_non_existing_viewlet(self):
        self.assertRaises(UnknownViewlet, get, "i_do_not_exist")

    def test_empty_decorator(self):
        template = self.get_django_template("<h1>{% viewlet hello_world %}</h1>")
        html1 = self.render(template)
        self.assertEqual(html1, "<h1>Hello wörld!</h1>")
        sleep(0.01)
        html2 = self.render(template)
        self.assertEqual(html1, html2)

    def test_render_tag(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_nocache name=viewlet_arg %}</h1>"
        )
        html = self.render(template, {"viewlet_arg": "wörld"})
        self.assertEqual(html.strip(), "<h1>Hello wörld!\n</h1>")
        template = self.get_django_template("<h1>{% viewlet unknown_viewlet %}</h1>")
        logging.disable(logging.ERROR)
        self.assertRaises(UnknownViewlet, self.render, template)
        logging.disable(logging.NOTSET)
        template = self.get_django_template("<h1>{% viewlet hello_world name= %}</h1>")
        self.assertRaises(TemplateSyntaxError, self.render, template)

    def test_cached_tag(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>"
        )
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertEqual(html1, html2)

    def test_non_cached_tag(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_non_cached_timestamp 'world' %}</h1>"
        )
        html1 = self.render(template)
        sleep(0.01)
        html2 = self.render(template)
        self.assertNotEqual(html1, html2)

    def test_cache(self):
        html1 = call("hello_cache", None, "world")
        sleep(0.01)
        html2 = call("hello_cache", None, "world")
        self.assertEqual(html1, html2)

    def test_unicode_cache(self):
        html1 = call("hello_cache", None, "wörld")
        sleep(0.01)
        html2 = call("hello_cache", None, "wörld")
        self.assertEqual(html1, html2)

    def test_refresh(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>"
        )
        html1 = self.render(template)

        sleep(0.01)
        refresh("hello_cached_timestamp", "world")
        html2 = self.render(template)
        self.assertNotEqual(html1, html2)

        sleep(0.01)
        self.hello_cached_timestamp.refresh("world")
        html3 = self.render(template)
        self.assertNotEqual(html3, html2)

        sleep(0.01)
        html4 = self.render(template)
        self.assertEqual(html3, html4)

        self.hello_cached_timestamp.expire("world")
        html5 = self.render(template)
        self.assertNotEqual(html5, html4)

    def test_view(self):
        client = Client()
        url = reverse("viewlet", args=["hello_cache"])
        response = client.get(url, {"name": "wörld"})
        self.assertEqual(response.status_code, 200)
        html = call("hello_cache", None, "wörld")
        self.assertEqual(response.content.decode("utf-8"), html)

    def test_view_request(self):
        client = Client()
        url = reverse("viewlet", args=["hello_request"])
        response = client.get(url, {"greeting": "wörld"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "wörld AnonymousUser!")

    def test_jinja_tag(self):
        template = self.get_jinja_template(
            "<h1>{% viewlet 'hello_nocache', viewlet_arg %}</h1>"
        )
        html = template.render({"extra": "Räksmörgås", "viewlet_arg": "wörld"})
        self.assertEqual(html.strip(), "<h1>RäksmörgåsHello wörld!%s</h1>" % self.tail)

    def test_context_tag(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_cached_timestamp 'world' %}</h1>"
        )
        self.render(template)
        v = get("hello_cached_timestamp")
        cache_key = v._build_cache_key("world")
        viewlet_data = cache.get(cache_key)
        self.assertTrue("name" in viewlet_data)
        self.assertEqual(viewlet_data["name"], "world")
        self.assertTrue(isinstance(viewlet_data, dict))

    def test_infinite_cache(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_infinite_cache 'world' %}</h1>"
        )
        self.render(template)
        v = get("hello_infinite_cache")
        self.assertEqual(v.timeout, settings.VIEWLET_INFINITE_CACHE_TIMEOUT)

    def test_expire_cache(self):
        v = get("hello_cache")
        v.call({}, "world")
        cache_key = v._build_cache_key("world")
        self.assertTrue(cache.get(cache_key) is not None)
        v.expire("world")
        self.assertTrue(cache.get(cache_key) is None)

    def test_mark_safe(self):
        # Test django
        template = self.get_django_template(
            "<h1>{% viewlet hello_strong 'wörld' %}</h1>"
        )
        html = self.render(template.strip())
        self.assertEqual(html, "<h1>Hello <strong>wörld!</strong>\n</h1>")
        # Test jinja2
        template = self.get_jinja_template(
            "<h1>{% viewlet 'hello_strong', 'wörld' %}</h1>"
        )
        html = template.render()
        self.assertEqual(html, "<h1>Hello <strong>wörld!</strong>%s</h1>" % self.tail)

    def test_cached_string(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_name name='wörld' %}</h1>"
        )
        html = self.render(template)
        self.assertTrue(isinstance(html, str))
        v = get("hello_name")
        cache_key = v._build_cache_key("wörld")
        cached_value = cache.get(cache_key)
        self.assertTrue(isinstance(cached_value, bytes))

    def test_named(self):
        template = self.get_django_template(
            "<h1>{% viewlet hello_new_name 'wörld' %}</h1>"
        )
        self.render(template)
        self.assertTrue(get("hello_new_name") is not None)

    def test_refreshing_context_viewlet_expecting_request_while_rendering_using_jinja2(
        self,
    ):
        template = self.get_jinja_template(
            "{% viewlet 'hello_request', 'nice to see you' %}"
        )
        html = template.render({"request": {"user": "nicolas cage"}})
        refresh("hello_request", "nice to see you")
        self.assertNotEqual(template.render({"request": {"user": "castor troy"}}), html)

    def test_django_template_from_dir(self):
        template = self.get_django_template(
            "{% viewlet hello_from_dir 'nice to see you' %}"
        )
        req = {"user": "castor troy"}
        html = self.render(template, context={"request": req}, request=req)
        self.assertTrue(isinstance(html, str))
        self.assertEqual(html, "nice to see you castor troy!")

    def test_jinja_template_from_dir(self):
        template = self.get_jinja_template(
            "{% viewlet 'hello_from_dir', 'nice to see you' %}"
        )
        html = template.render({"request": {"user": "nicolas cage"}})
        self.assertTrue(isinstance(html, str))
        self.assertEqual(html, "nice to see you nicolas cage!\n")

    def test_jinja_template_from_dir_warning(self):
        settings.VIEWLET_TEMPLATE_ENGINE = "jinja2"
        template = self.get_jinja_template("{% viewlet 'hello_from_dir' %}")
        func = self.assertRaisesRegex
        template.render()

    def test_request_context(self):
        template = self.get_django_template(
            """
            <h1>{% viewlet hello_render_to_string %}</h1>
            {% viewlet hello_render_to_string %}
            {% viewlet hello_render_to_string %}
            {% viewlet hello_render_to_string %}
            {% viewlet hello_render_to_string %}
        """
        )

        context = {"test": "test"}
        html = self.render(template, context=context, request="Request")
        self.assertTrue(isinstance(html, str))


class ViewletCacheBackendTest(TestCase):
    @override_settings(VIEWLET_DEFAULT_CACHE_ALIAS="dummy")
    @override_settings(
        CACHES={
            "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
            "short": {"BACKEND": "viewlet.tests.utils.ShortLocMemCache"},
            "dummy": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
        }
    )
    def setUp(self):

        self.assertNotEqual("dummy", conf.settings.VIEWLET_DEFAULT_CACHE_ALIAS)
        for m in [
            conf,
            cache_m,
            library,
            models,
        ]:  # conf must be reloaded first; do NOT move to a function
            importlib.reload(m)
        self.assertEqual("dummy", conf.settings.VIEWLET_DEFAULT_CACHE_ALIAS)

        @viewlet(template="hello_timestamp.html", timeout=10)
        def hello_cached_timestamp_settings_cache(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

        @viewlet(template="hello_timestamp.html", using="short")
        def hello_cached_timestamp_argument_cache(context, name):
            return {
                "name": name,
                "timestamp": time(),
            }

    def tearDown(self):
        del django.conf.settings.VIEWLET_DEFAULT_CACHE_ALIAS
        for m in [
            conf,
            cache_m,
            library,
            models,
        ]:  # conf must be reloaded first; do NOT move to a function
            importlib.reload(m)
        self.assertNotEqual("dummy", conf.settings.VIEWLET_DEFAULT_CACHE_ALIAS)

    def test_cache_backend_from_settings(self):
        v = get("hello_cached_timestamp_settings_cache")
        v.call({}, "world")
        cache_key = v._build_cache_key("world")
        self.assertIsNone(v._cache_get(cache_key))

    def test_cache_backend_from_argument(self):
        v = get("hello_cached_timestamp_argument_cache")
        v.call({}, "world")
        cache_key = v._build_cache_key("world")
        self.assertIsNotNone(v._cache_get(cache_key))
        sleep(v.cache.default_timeout + 0.01)
        self.assertIsNone(v._cache_get(cache_key))


class ViewletKeyTest(TestCase):
    def setUp(self):
        @viewlet(timeout=1, key="somekey")
        def custom_key_without_args(context):
            return "hello"

        @viewlet(timeout=1, key="somekey")
        def custom_key_missing_args(context, greet, name):
            return f"{greet} {name}!"

        @viewlet(timeout=1, key="somekey:{args}")
        def custom_key_with_args(context, greet, name):
            return f"{greet} {name}!"

        @viewlet(timeout=1, key="somekey(%s,%s)")
        def custom_key_old_format(context, greet, name):
            return f"{greet} {name}!"

    def test_custom_key_without_args(self):
        v = get("custom_key_without_args")
        self.assertEqual(v._build_cache_key(), "somekey")

    def test_custom_key_missing_args(self):
        v = get("custom_key_missing_args")
        args = ("Hello", "world")
        self.assertRaises(exceptions.WrongKeyFormat, v._build_cache_key, *args)

    def test_custom_key_with_args(self):
        v = get("custom_key_with_args")
        args = ("Hello", "world")
        v.call({}, *args)
        cache_key = v._build_cache_key(*args)
        self.assertTrue(v._build_cache_key().startswith("somekey:"))
        self.assertEqual(v._cache_get(cache_key), "%s %s!" % args)

    def test_custom_key_old_format(self):
        v = get("custom_key_old_format")
        args = ("Hello", "world")
        self.assertRaises(exceptions.DeprecatedKeyFormat, v._build_cache_key, *args)

    def test_key_args_join(self):
        self.key_func = "viewlet.cache.make_key_args_join"
        django.conf.settings.VIEWLET_CACHE_KEY_FUNCTION = self.key_func
        self.assertNotEqual(self.key_func, conf.settings.VIEWLET_CACHE_KEY_FUNCTION)
        for m in [
            conf,
            cache_m,
            library,
            models,
        ]:  # conf must be reloaded first; do NOT move to a function
            importlib.reload(m)
        self.assertEqual(self.key_func, conf.settings.VIEWLET_CACHE_KEY_FUNCTION)

        @viewlet(timeout=10)
        def name_args_join(context, greet, name):
            return f"{greet} {name}!"

        v = get("name_args_join")
        args = ("Hello", "world")
        v.call({}, *args)
        cache_key = v._build_cache_key(*args)
        self.assertEqual(cache_key, make_key_args_join(v, args))
        self.assertEqual(v._cache_get(cache_key), "%s %s!" % args)

        del django.conf.settings.VIEWLET_CACHE_KEY_FUNCTION
        for m in [
            conf,
            cache_m,
            library,
            models,
        ]:  # conf must be reloaded first; do NOT move to a function
            importlib.reload(m)
        self.assertNotEqual(self.key_func, conf.settings.VIEWLET_CACHE_KEY_FUNCTION)
