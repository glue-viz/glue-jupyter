import ipywidgets as widgets
import echo.selection


def _is_traitlet(obj):
    return hasattr(obj, 'observe')


def _is_echo(link):
    return hasattr(getattr(type(link[0]), link[1]), 'add_callback')


class link(object):
    def __init__(self, source, target, f1=lambda x: x, f2=lambda x: x):
        self.source = source
        self.target = target

        self._link(source, target, 'source', f1, True)
        self._link(target, source, 'target', f2)

    def _link(self, source, target, name, f, sync_directly=False):
        def sync(*ignore):
            old_value = getattr(target[0], target[1])
            new_value = f(getattr(source[0], source[1]))
            if new_value != old_value:
                setattr(target[0], target[1], new_value)

        if _is_traitlet(source[0]):
            source[0].observe(sync, source[1])
        elif _is_echo(source):
            callback_property = getattr(type(source[0]), source[1])
            callback_property.add_callback(source[0], sync)
        else:
            raise ValueError('{} is unknown object'.format(name))
        if sync_directly:
            sync()


class dlink(link):
    def __init__(self, source, target, f1=lambda x: x):
        self.source = source
        self.target = target

        self._link(source, target, 'source', f1, True)


def _assign(object, value):
    if isinstance(object, widgets.Widget):
        object, trait = object, 'value'
    else:
        object, trait = object
    setattr(object, trait, value)


def calculation(inputs, output=None, initial_calculation=True):
    def decorator(f):
        def calculate(*ignore_args):
            values = [getattr(input, 'value') for input in inputs]
            result = f(*values)
            if output:
                _assign(output, result)
        for input in inputs:
            input.observe(calculate, 'value')
        if initial_calculation:
            calculate()
    return decorator


def on_change(inputs, initial_call=False, once=False):
    def decorator(f):
        for input in inputs:
            # input can be (obj, 'x', 'y'), or just obj, where 'value' is assumed for default
            # this is only support for widgets/HasTraits
            if _is_traitlet(input):
                obj, attrnames = input, ['value']
            else:
                obj, attrnames = input[0], input[1:]
            if _is_traitlet(input):
                obj.observe(lambda *ignore: f(), attrnames)
            elif _is_echo(input):
                for attrname in attrnames:
                    callback_property = getattr(type(obj), attrname)
                    callback_property.add_callback(obj, lambda *ignore: f())
            else:
                raise ValueError('{} is unknown object'.format(obj))
        if initial_call:
            f()
    return decorator


def link_component_id_to_select_widget(state, state_attr, widget, widget_attr='value'):

    def update(*ignore):
        options = [k for k in getattr(type(state), state_attr).get_choices(state)
                   if not isinstance(k, echo.selection.ChoiceSeparator)]
        display_func = getattr(type(state), state_attr).get_display_func(state)
        value = getattr(state, state_attr)
        widget.options = [(display_func(options[k]), k) for k in range(len(options))]
        # componentId's don't hash or compare well, use 'is' instead of ==
        # ISSUE: value can be a string, and then it will never match
        matches = [k for k in range(len(options)) if value is options[k]]
        if len(matches):
            widget.index = matches[0]

    getattr(type(state), state_attr).add_callback(state, update)

    def update_state(change):
        options = [k for k in getattr(type(state), state_attr).get_choices(state)
                   if not isinstance(k, echo.selection.ChoiceSeparator)]
        if change.new is not None:
            setattr(state, state_attr, options[change.new])

    widget.observe(update_state, 'index')

    update()
