from ipywidgets import FloatSlider, IntText, VBox

from ...link import link

__all__ = ['HistogramLayerStateWidget']


class HistogramLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_opacity = FloatSlider(min=0, max=1, step=0.01, value=self.state.alpha,
                                          description='opacity')
        link((self.state, 'alpha'), (self.widget_opacity, 'value'))

        self.widget_zorder = IntText(description='z-order')
        link((self.state, 'zorder'), (self.widget_zorder, 'value'))

        super().__init__([self.widget_opacity, self.widget_zorder])

    def cleanup(self):
        pass
