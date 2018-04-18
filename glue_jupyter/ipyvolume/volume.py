import ipyvolume as ipv
import ipywidgets as widgets
import traitlets
from IPython.display import display
import numpy as np

from .scatter import IpyvolumeScatterLayerArtist
from ..utils import reduce_size

from glue_vispy_viewers.common.layer_state import VispyLayerState
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.external.echo import (CallbackProperty, SelectionCallbackProperty)
from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute


class IpyvolumeLayerState(VispyLayerState):
    attribute = SelectionCallbackProperty()

    def __init__(self, layer=None, **kwargs):
        super(IpyvolumeLayerState, self).__init__(layer=layer)

        if self.layer is not None:

            self.color = self.layer.style.color
            self.alpha = self.layer.style.alpha

        self.att_helper = ComponentIDComboHelper(self, 'attribute')

        self.add_callback('layer', self._on_layer_change)
        if layer is not None:
            self._on_layer_change()

        self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):
        if self.layer is None:
            self.att_helper.set_multiple_data([])
        else:
            self.att_helper.set_multiple_data([self.layer])


from glue_vispy_viewers.common.layer_artist import VispyLayerArtist


class IpyvolumeVolumeLayerArtist(VispyLayerArtist):
    def __init__(self, ipyvolume_viewer=None, state=None, layer=None, layer_state=None):
        super(IpyvolumeVolumeLayerArtist, self).__init__(layer)
        self.layer = layer or layer_state.layer
        self.ipyvolume_viewer = ipyvolume_viewer
        self.figure = self.ipyvolume_viewer.figure
        self._viewer_state = ipyvolume_viewer.state
        assert ipyvolume_viewer.state == state
        self.state = layer_state or IpyvolumeLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        #ipv.figure(self.ipyvolume_viewer.figure)
        self.volume = None
        self.last_shape = None

    def clear(self):
        pass

    def redraw(self):
        pass

    def update(self):
        # print(self.layer)
        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                # The following includes a call to self.clear()
                self.disable("Subset cannot be applied to this data")
                return
            else:
                self._enabled = True
            # if self.state.subset_mode == 'outline':
            #     data = mask.astype(np.float32)
            # else:
            data = self.layer.data[self.state.attribute].astype(np.float32)
            data *= mask
        else:
            data = self.layer[self.state.attribute]
        #data = self.layer.data[self.state.attribute].astype(np.float32)
        #print(data, data.shape, self.state.attribute)
        finite_mask = np.isfinite(data)
        data_min, data_max = np.percentile(
            data[finite_mask], 1), np.percentile(data[finite_mask], 99)
        #data_min, data_max = None, None
        self.last_shape = shape = data.shape
        data = reduce_size(data, self.widget_max_resolution.value)
        if self.volume is None:
            with self.figure:
                self.volume = ipv.volshow(data, data_min=data_min, data_max=data_max, extent=[[0, shape[0]], [0, shape[1]], [0, shape[2]]])
        else:
            self.ipyvolume_viewer.figure.volume_data = data



    def create_widgets(self):
        self.size_options = [128, 128+64, 256, 256+128, 512]
        options = [(str(k), k) for k in self.size_options]
        self.widget_max_resolution = widgets.Dropdown(options=options, value=128, description='max resolution')

        self.widget_reset_zoom = widgets.Button(description="Reset zoom")
        def reset_zoom(*ignore):
            with self.figure:
                if self.last_shape is not None:
                    ipv.xlim(0, self.last_shape[0])
                    ipv.ylim(0, self.last_shape[1])
                    ipv.zlim(0, self.last_shape[2])
        self.widget_reset_zoom.on_click(reset_zoom)
        return widgets.VBox([self.widget_max_resolution, self.widget_reset_zoom])

#from glue_vispy_viewers.common.vispy_data_viewer import BaseVispyViewer


#$IpyvolumeVolumeView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
