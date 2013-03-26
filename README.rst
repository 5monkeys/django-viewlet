Django Viewlet
==============

Render template parts with extended cache control.

.. image:: https://travis-ci.org/5monkeys/django-viewlet.png?branch=master
    :target: http://travis-ci.org/5monkeys/django-viewlet

Installation
------------

Install django-viewlet in your python environment

.. code:: sh

    $ pip install django-viewlet

Add ``viewlet`` to your ``INSTALLED_APPS`` setting so Django can find the template tag

.. code:: python

    INSTALLED_APPS = (
        ...
        'viewlet',
    )


If you're using Jinja2 as your template engine put this in your Django settings

.. code:: python

    JINJA2_GLOBALS = {
        'viewlet': 'viewlet.call_viewlet'
    }

    VIEWLET_TEMPLATE_ENGINE = 'jinja2'


Usage
-----

A viewlet is almost like a function based django view, taking a template context
as first argument instead of request.
Place your viewlets in ``viewlets.py`` or existing ``views.py`` in your django app directory.

.. code:: python

    from django.template.loader import render_to_string
    from viewlet import viewlet

    @viewlet
    def hello_user(context, name):
        return render_to_string('hello_user.html', {'name': name})


You can then render the viewlet with the ``viewlet`` template tag:

.. code:: html

    {% load viewlets %}
    <p>{% viewlet hello_user request.user.username %}</p>


... and in your Jinja2 templates:

.. code:: html

    <p>{{ viewlet('host_sponsors', host.id) }}</p>


Refreshing viewlets
___________________

A cached viewlet can be re-rendered and updated behind the scenes with ``viewlet.refresh``

.. code:: python

    import viewlet
    viewlet.refresh('hello_user', 'monkey')


The decorator
_____________

.. code:: python

    @viewlet(name, template, key, timeout, cached)


* name
    Optional reference name for the viewlet, defaults to function name.
* template
    Optional path to template. If specified the viewlet must return a context dict,
    otherwise it is responsible to return the rendered output itself.
* key
    Optional cache key, if not specified a dynamic key will be generated ``viewlet:name(args...)``
* timeout
    Cache timeout. Defaults to 60 sec, None = eternal, 0 = uncached.
* cached
    Defaults to True, if set to False timeout will be 0 and therefore uncached.


Examples
________

The content returned by the viewlet will by default be cached for 60s. Use the ``timeout`` argument to change this.

.. code:: python

    @viewlet(timeout=30*60)
    def hello_user(context, name):
        return render_to_string('hello_user.html', {'name': name})

..

    **Tip:** Set ``timeout`` to ``None`` to cache forever and use ``viewlet.refresh`` to update the cache.


Django viewlet will by default build a cache key ``viewlet:name(args...)``.
To customize this key pass a string to the viewlet decorator argument ``key``

.. code:: python

    @viewlet(timeout=30*60, key='some_cache_key')
    def hello_user(context, name):
        return render_to_string('hello_user.html', {'name': name})


Django viewlet will cache context instead of html by using the ``template`` decorator argument.
This is useful if cached html is too heavy, or your viewlet template needs to be rendered on every call.

.. code:: python

    @viewlet(template='hello_user.html', timeout=30*60)
    def hello_user(context, name):
        return {'name': name}

..

    **Note:** Return context dict for the template, not rendered html/text


If there is no need for caching, set the viewlet decorator argument ``cached`` to ``False``

.. code:: python

    @viewlet(cached=False)
    def hello_user(context, name):
        return render_to_string('hello_user.html', {'name': name})


By default you viewlets will be named as the function. To override this you can set the decorator argument ``name``

.. code:: python

    @viewlet(name='greeting')
    def hello_user(context, name):
        return render_to_string('hello_user.html', {'name': name})


A powerful usage of ``viewlet.refresh`` is to use it together with Django signals:

.. code:: python

    class Product(Model):
        name = CharField(max_length=255)

    @viewlet(timeout=None)
    def product_teaser(context, id):
        product = get_context_object(Product, id, context)
        return render_to_string('product_teaser.html', locals())

    def refresh_product_teaser(instance, **kwargs):
        viewlet.refresh('product_teaser', instance.id)

    post_save.connect(refresh_product_teaser, Product)


Viewlets can also be accesses with AJAX by adding ``viewlet.urls`` to your Django root urls:

.. code:: python

    urlpatterns = patterns('',
        (r'^viewlet/', include('viewlet.urls')),
    )


The url ends with the viewlet name followed by a querystring used as ``kwargs`` to the viewlet:

..

    http://localhost:8000/viewlet/[name]/?arg=1...
