import json
from functools import partial
import traitlets
from traitlets.utils.bunch import Bunch
from glue.core.state_objects import State
from glue.core import Data, Subset, ComponentID


class GlueStateJSONEncoder(json.JSONEncoder):

    # Custom JSON encoder class that understands glue-specific objects, and
    # is used below in convert_state_to_json.

    def default(self, obj):
        if isinstance(obj, State):
            return obj.as_dict()
        elif isinstance(obj, (Data, Subset, ComponentID)):
            return obj.label
        return json.JSONEncoder.default(self, obj)


class GlueState(traitlets.Any):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag(to_json=self.convert_state_to_json,
                 from_json=self.update_state_from_json)

    def validate(self, obj, value):
        if value is None or isinstance(value, State):
            return value
        else:
            raise traitlets.TraitError('value should be a glue State instance')

    # When state objects change internally, the instance itself does not change
    # so we need to manually look for changes in the state and then manually
    # trigger a notification, which we do in the following two methods.

    def set(self, obj, state):
        super().set(obj, state)
        state.add_global_callback(partial(self.on_state_change, obj=obj))

    def on_state_change(self, *args, obj=None, **kwargs):
        obj.notify_change(Bunch({'name': self.name,
                                 'type': 'change',
                                 'value': self.get(obj)}))

    # NOTE: the following two methods are implemented as methods on the trait
    # because we need update_state_from_json to have an unambiguous reference
    # to the correct state instance. This means that overwriting these means
    # inheriting from GlueState rather than overwriting the tag.

    def convert_state_to_json(self, state, widget):
        if state is None:
            return "{}"
        else:
            return json.dumps(state.as_dict(), cls=GlueStateJSONEncoder)

    def update_state_from_json(self, json, widget):
        state = getattr(widget, self.name)
        state.update_from_dict(json)
