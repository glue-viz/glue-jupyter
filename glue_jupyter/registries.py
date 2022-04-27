from glue.config import DictRegistry

__all__ = ['viewer_registry', 'ViewerRegistry']


class ViewerRegistry(DictRegistry):
    """
    Registry containing references to custom viewers.
    """

    def __call__(self, name=None):
        def decorator(cls):
            self.add(name, cls)
            return cls
        return decorator

    def add(self, name, cls):
        """
        Add an item to the registry.

        Parameters
        ----------
        name : str
            The key referencing the associated class in the registry
            dictionary.
        cls : type
            The class definition (not instance) associated with the name given
            in the first parameter.
        """
        if name in self.members:
            raise ValueError(f"Viewer with the name {name} already exists, "
                             f"please choose a different name.")
        else:
            self.members[name] = {'cls': cls}


viewer_registry = ViewerRegistry()
