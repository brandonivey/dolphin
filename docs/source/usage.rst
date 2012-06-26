Usage
=====

======
Python
======

There are multiple ways to use dolphin. The first is with a basic if statement::

    from dolphin import flipper
    if flipper.is_active("flag_name"):
        do_something()
    else:
        do_something_else

There is also a decorator that allows redirects, other view functions to be called,
or just a 404 by default::

    @flipper.switch_is_active("flag_name")
    def view(request):
        return ...

    @flipper.switch_is_active("flag_name", redirect="/")
    def view2(request):
        return ...

    @flipper.switch_is_active("flag_name", alt=view1)
    def view3(request):
        return ...

========
Template
========

In a template::

    {% load dolphin_tags %}
    {% ifactive "keyname" %}
    Active
    {% else %}
    Not active
    {% endifactive %}


There's also a template tag that will list active flags as a comma delimited list::

    {% active_flags %}


==========
Javascript
==========

For usage in javascript, there are a couple of convenience functions in dolphin.views
that can be added to your urls.py. As an example::

    url(r'^dolphin/js/$', 'dolphin.views.js'),
    url(r'^dolphin/json/$', 'dolphin.views.json'),

The js view provides a flipper object which has a function is_active that may
be used like the python is_active function::

    <script type="text/javascript" src="/dolphin/js/">
    <script type="text/javascript">
        if ( flipper.is_active("enabled") ) {
            ...
        }
        else {
            ...
        }
    </script>

The flipper object also has the active flags in an array called flipper.active_flags.

The json function returns a structure as follows::

    {"active_flags": ["enabled", "ab_random", "max"]}

All processing is done in python with the javascript views. If any frontend caching would 
cache this view, you may want to add never cache if you're utilizing geolocation, random, 
max, or date based flags.
