def _is_traitlet(link):
    return hasattr(link[0], 'observe')

def _is_echo(link):
    return hasattr(getattr(type(link[0]), link[1]), 'add_callback')


class link(object):
    def __init__(self, source, target, f1=lambda x: x, f2=lambda x: x):
        self.source = source
        self.target = target
        
        self._link(source, target, 'source', f1)
        self._link(target, source, 'target', f2, True)

    def _link(self, source, target, name, f, sync_directly=False):
        def sync(*ignore):
            old_value = getattr(target[0], target[1])
            new_value = f(getattr(source[0], source[1]))
            #print('old/new', old_value, new_value)
            if new_value != old_value:
                setattr(target[0], target[1], new_value)

        if _is_traitlet(source):
            source[0].observe(sync, source[1])
        elif _is_echo(source):
            callback_property = getattr(type(source[0]), source[1])
            callback_property.add_callback(source[0], sync)
        else:
            raise ValueError('{} is unknown object'.format(name))
        if sync_directly:
            sync()

