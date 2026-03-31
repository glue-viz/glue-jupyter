import ipyvuetify as v


__all__ = ['Scatter3DLayerStateWidget']


class Scatter3DLayerStateWidget(v.VuetifyTemplate):

    template_file = (__file__, 'layer_style_widget.vue')

    def __init__(self, layer_state):

        self.state = layer_state
