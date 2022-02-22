from .widgets.linked_dropdown import get_choices


def link_glue(widget, widget_prop, state, glue_prop=None, from_glue_fn=lambda x: x,
              to_glue_fn=lambda x: x):

    if not glue_prop:
        glue_prop = widget_prop

    def from_glue_state(*args):
        setattr(widget, widget_prop, from_glue_fn(getattr(state, glue_prop)))

    state.add_callback(glue_prop, from_glue_state)
    from_glue_state()

    def to_glue_state(change):
        setattr(state, glue_prop, to_glue_fn(change['new']))

    widget.observe(to_glue_state, names=[widget_prop])


def link_glue_choices(widget, state, prop):
    """
    Links the choices of state.prop to the traitlet widget.{prop}_items, the
    selected value to the traitlet widget.{prop}_selected.
    """

    def update_choices(*args):
        labels = get_choices(state, prop)[1]
        items = [dict(text=label, value=index) for index, label in enumerate(labels)]
        setattr(widget, f'{prop}_items', items)

    state.add_callback(prop, update_choices)
    update_choices()

    def choice_to_index(choice):
        if choice is None:
            return None
        return get_choices(state, prop)[0].index(choice)

    def index_to_choice(index):
        if index is None:
            return None
        return get_choices(state, prop)[0][index]

    link_glue(widget, f'{prop}_selected', state, prop,
              from_glue_fn=choice_to_index,
              to_glue_fn=index_to_choice)


class WidgetCache():

    def __init__(self):
        self.cache = {}

    def get_or_create(self, key, create_fn):
        # TODO: use weakref for object-keys
        if key not in self.cache.keys():
            self.cache[key] = create_fn()
        return self.cache[key]
