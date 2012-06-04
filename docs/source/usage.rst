Usage
=====

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


In a template::

    {% load dolphin_tags %}
    {% ifactive "keyname" %}
    Active
    {% else %}
    Not active
    {% endifactive %}


There's also a template tag that will list active flags as a comma delimited list::

    {% active_tags %}
