from ipywidgets import Checkbox, VBox, ToggleButton

import ipyvolume as ipv

from ...link import link, dlink
from ...widgets import LinkedDropdown


__all__ = ['Viewer3DStateWidget']


class Viewer3DStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = Checkbox(value=False, description="Show axes")
        link((self.state, 'visible_axes'), (self.widget_show_axes, 'value'))

        self.widgets_axis = []
        for i, axis_name in enumerate('xyz'):
            widget_axis = LinkedDropdown(self.state, axis_name + '_att',
                                         label=axis_name + ' axis')
            self.widgets_axis.append(widget_axis)

        super().__init__([self.widget_show_axes] + self.widgets_axis)

        if hasattr(self.state, 'figure'):
            self.widget_show_movie_maker = ToggleButton(value=False, description="Show movie maker")
            self.movie_maker = ipv.moviemaker.MovieMaker(self.state.figure,
                                                         self.state.figure.camera)
            dlink((self.widget_show_movie_maker, 'value'),
                  (self.movie_maker.widget_main.layout, 'display'),
                  lambda value: None if value else 'none')
            self.children += (self.widget_show_movie_maker, self.movie_maker.widget_main)
