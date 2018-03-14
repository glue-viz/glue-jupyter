import ipyvolume as ipv
import ipywidgets as widgets
import traitlets
from IPython.display import display
import numpy as np

from .scatter import IpyvolumeScatterLayerArtist
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
        self._viewer_state = ipyvolume_viewer.state
        assert ipyvolume_viewer.state == state
        self.state = layer_state or IpyvolumeLayerState(layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        ipv.figure(self.ipyvolume_viewer.figure)

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
        self.volume = ipv.volshow(data, data_min=data_min, data_max=data_max)




#from glue_vispy_viewers.common.vispy_data_viewer import BaseVispyViewer


#$IpyvolumeVolumeView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
