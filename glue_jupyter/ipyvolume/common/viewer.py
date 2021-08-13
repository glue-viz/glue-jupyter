import ipyvolume as ipv
import ipyvolume.moviemaker

from glue.core.subset import RoiSubsetState3d
from glue.core.command import ApplySubsetState

from ...view import IPyWidgetView
from ...link import dlink

from .viewer_options_widget import Viewer3DStateWidget

__all__ = ['IpyvolumeBaseView']


class IpyvolumeBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _options_cls = Viewer3DStateWidget

    tools = ['ipyvolume:lasso', 'ipyvolume:circle', 'ipyvolume:rectangle']

    def __init__(self, *args, **kwargs):

        self.figure = ipv.figure(animation_exponent=1.)
        self.figure.selector = ''

        super(IpyvolumeBaseView, self).__init__(*args, **kwargs)

        # FIXME: hack for the movie maker to have access to the figure
        self.state.figure = self.figure

        # note that for ipyvolume, we use axis in the order x, z, y in order to have
        # the z axis of glue pointing up
        def attribute_to_label(attribute):
            return 'null' if attribute is None else attribute.label

        dlink((self.state, 'x_att'), (self.figure, 'xlabel'), attribute_to_label)
        dlink((self.state, 'y_att'), (self.figure, 'zlabel'), attribute_to_label)
        dlink((self.state, 'z_att'), (self.figure, 'ylabel'), attribute_to_label)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)
        if hasattr(self.state, 'z_min'):
            self.state.add_callback('z_min', self.limits_to_scales)
            self.state.add_callback('z_max', self.limits_to_scales)

        self.state.add_callback('visible_axes', self._update_axes_visibility)

        self._figure_widget = ipv.gcc()

        self.create_layout()

    def _update_axes_visibility(self, *args):
        with self.figure:
            if self.state.visible_axes:
                ipv.style.axes_on()
                ipv.style.box_on()
            else:
                ipv.style.axes_off()
                ipv.style.box_off()

    @property
    def figure_widget(self):
        return self._figure_widget

    def apply_roi(self, roi, use_current=False):
        if len(self.layers) > 0:
            # self.state.x_att.parent.get_component(self.state.x_att)
            x = self.state.x_att
            # self.state.y_att.parent.get_component(self.state.y_att)
            y = self.state.y_att
            # self.state.z_att.parent.get_component(self.state.z_att)
            z = self.state.z_att
            subset_state = RoiSubsetState3d(x, y, z, roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state,
                                   override_mode=use_current)
            self._session.command_stack.do(cmd)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.figure.xlim = self.state.x_min, self.state.x_max
        if self.state.y_min is not None and self.state.y_max is not None:
            self.figure.zlim = self.state.y_min, self.state.y_max
        # if self.state.z_min is not None and self.state.z_max is not None:
        #     self.figure.zlim = self.state.z_min, self.state.z_max
        if hasattr(self.state, 'z_min'):
            if self.state.z_min is not None and self.state.z_max is not None:
                self.figure.ylim = self.state.z_min, self.state.z_max

    def redraw(self):
        pass
