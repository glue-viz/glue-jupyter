import os
import traitlets


def load_template(file_name, path=None):
    path = os.path.dirname(path)
    with open(os.path.join(path, file_name)) as f:
        return traitlets.Unicode(f.read()).tag(sync=True)


def link_glue(widget, widget_prop, state, glue_prop = None, from_glue_fn = lambda x: x,
              to_glue_fn = lambda x:x):

    if not glue_prop:
        glue_prop = widget_prop

    def from_glue_state(*args):
        setattr(widget, widget_prop, from_glue_fn(getattr(state, glue_prop)))

    state.add_callback(glue_prop, from_glue_state)
    from_glue_state()

    def to_glue_state(change):
        setattr(state, glue_prop, to_glue_fn(change['new']))

    widget.observe(to_glue_state, names=[widget_prop])


class WidgetCache():

    def __init__(self):
        self.cache = {}

    def get_or_create(self, key, create_fn):
        # TODO: use weakref for object-keys
        if key not in self.cache.keys():
            self.cache[key] = create_fn()
        return self.cache[key]
