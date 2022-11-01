import json
import traitlets
from collections import defaultdict
from traitlets.utils.bunch import Bunch
from glue.core.state_objects import State
from glue.core import BaseCartesianData, Subset, ComponentID
from echo import CallbackList, CallbackDict
from matplotlib.colors import Colormap
from matplotlib.cm import get_cmap

MAGIC_IGNORE = '611cfa3b-ebb5-42d2-b5c7-ba9bce8b51a4'


def state_to_dict(state):

    # NOTE: we don't use state.as_dict since we need to treat lists
    # of states slightly differently.

    changes = {}
    for name in dir(state):
        if not name.startswith('_') and state.is_callback_property(name):
            item = getattr(state, name)
            if isinstance(item, CallbackList):
                item = [state_to_dict(value) if isinstance(value, State) else value
                        for value in item]
            elif isinstance(item, CallbackDict):
                item = {key: state_to_dict(value) if isinstance(value, State) else value
                        for key, value in item.items()}
            changes[name] = item
    return changes


def update_state_from_dict(state, changes):

    if len(changes) == 0:
        return

    groups = defaultdict(list)
    for name in changes:
        if state.is_callback_property(name):
            groups[state._update_priority(name)].append(name)

    for priority in sorted(groups, reverse=True):
        for name in groups[priority]:
            if isinstance(getattr(state, name), CallbackList):
                callback_list = getattr(state, name)
                for i in range(len(callback_list)):
                    # Note that for updates to CallbackLists, we support either
                    # a dictionary with integer indices (specifying the elements
                    # of the CallbackList to update) or a list. If a dict is
                    # specified, only indices referring to existing list items
                    # will be updated, and if a list, extra elements will be
                    # ignored.
                    if (isinstance(changes[name], dict) and i in changes[name]
                            or isinstance(changes[name], list) and i < len(changes[name])):
                        if isinstance(callback_list[i], State):
                            update_state_from_dict(callback_list[i], changes[name][i])
                        else:
                            if (changes[name][i] != MAGIC_IGNORE and
                                    callback_list[i] != changes[name][i]):
                                callback_list[i] = changes[name][i]
            elif isinstance(getattr(state, name), CallbackDict):
                callback_dict = getattr(state, name)

                for k in callback_dict:
                    if k in changes[name]:
                        if isinstance(callback_dict[k], State):
                            update_state_from_dict(callback_dict[k], changes[name][k])
                        else:
                            if (changes[name][k] != MAGIC_IGNORE and
                                    callback_dict[k] != changes[name][k]):
                                callback_dict[k] = changes[name][k]
            else:
                if changes[name] != MAGIC_IGNORE and getattr(state, name) != changes[name]:
                    if 'cmap' in name:
                        setattr(state, name, get_cmap(changes[name]))
                    else:
                        setattr(state, name, changes[name])


class GlueStateJSONEncoder(json.JSONEncoder):

    # Custom JSON encoder class that understands glue-specific objects, and
    # is used below in convert_state_to_json.

    def default(self, obj):
        if isinstance(obj, State):
            return state_to_dict(obj)
        elif isinstance(obj, (BaseCartesianData, Subset, ComponentID)):
            return MAGIC_IGNORE
        elif isinstance(obj, Colormap):
            return obj.name

        # JSON cannot serialized native numpy types, so check if the object
        #  is a numpy dtype, and if it is, convert to python type
        if hasattr(obj, 'dtype'):
            return obj.item()

        return json.JSONEncoder.default(self, obj)


class PartialCallback:

    def __init__(self, func, obj):
        self.func = func
        self.obj = obj

    def __call__(self, *args, **kwargs):
        return self.func(*args, obj=self.obj, **kwargs)


class GlueState(traitlets.Any):

    _block_on_state_change = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag(to_json=self.convert_state_to_json,
                 from_json=self.update_state_from_json)
        self._last_serialized = ''

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
        state.add_global_callback(PartialCallback(self.on_state_change, obj=obj))

    def on_state_change(self, *args, obj=None, **kwargs):

        if self._block_on_state_change:
            return

        state = self.get(obj)

        # To avoid unnecessary messages, we now check if the serialized version
        # of the state has actually changed since the last time it was sent to
        # front-end. In some cases it can happen that a glue state change doesn't
        # result in any actual change to the JSON because some items are ignored
        # in the serialization.

        serialized = self.convert_state_to_json(state, None)

        if serialized == self._last_serialized:
            return
        else:
            self._last_serialized = serialized

        obj.notify_change(Bunch({'name': self.name,
                                 'type': 'change',
                                 'value': state,
                                 'new': state}))

    # NOTE: the following two methods are implemented as methods on the trait
    # because we need update_state_from_json to have an unambiguous reference
    # to the correct state instance. This means that overwriting these means
    # inheriting from GlueState rather than overwriting the tag.

    def convert_state_to_json(self, state, widget):
        if state is None:
            return {}
        else:
            return json.loads(json.dumps(state_to_dict(state), cls=GlueStateJSONEncoder))

    def update_state_from_json(self, json, widget):
        state = getattr(widget, self.name)
        self._block_on_state_change = True
        try:
            update_state_from_dict(state, json)
        finally:
            self._block_on_state_change = False
        # In some cases changes to the state may have caused other attributes
        # in the glue state to change, so we do need to call on_state_change
        # once. We don't have a reference to 'obj' here so we have to do a bit
        # of hackery.
        for callback in state._global_callbacks:
            if isinstance(callback, PartialCallback):
                callback()
        return state
