import bqplot
import ipywidgets as widgets
import ipymaterialui as mui
from IPython.display import display

import glue.icons
from glue.core.subset import roi_to_subset_state
from glue.core.roi import RectangularROI, RangeROI
from glue.core.command import ApplySubsetState

import glue_jupyter.widgets.component
from ..view import IPyWidgetView
from ..link import link, dlink, calculation, link_component_id_to_select_widget, on_change
from ..utils import float_or_none

ICON_WIDTH = 20
icon_brush = widgets.Image.from_file(glue.icons.icon_path('glue_square', icon_format='svg'), width=ICON_WIDTH)
icon_pan = widgets.Image.from_file(glue.icons.icon_path('glue_move', icon_format='svg'), width=ICON_WIDTH)
icon_brush_x = widgets.Image.from_file(glue.icons.icon_path('glue_xrange_select', icon_format='svg'), width=ICON_WIDTH)
icon_brush_y = widgets.Image.from_file(glue.icons.icon_path('glue_yrange_select', icon_format='svg'), width=ICON_WIDTH)
icon_brush_lasso = widgets.Image.from_file(glue.icons.icon_path('glue_lasso', icon_format='svg'), width=ICON_WIDTH)


class BqplotBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True
    # _state_cls = ImageViewerState
    # _data_artist_cls = BqplotImageLayerArtist
    # _subset_artist_cls = BqplotImageLayerArtist

    def __init__(self, session, state=None):
        super(BqplotBaseView, self).__init__(session, state=state)
        # session.hub.subscribe(self, SubsetCreateMessage,
        #                       handler=self.receive_message)

        # if we allow padding, we sometimes get odd behaviour with the interacts
        self.scale_x = bqplot.LinearScale(min=0, max=1, allow_padding=False)
        self.scale_y = bqplot.LinearScale(min=0, max=1)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='solid', label='x')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='solid', label='y')
        def update_axes(*ignore):
            self.axis_x.label = str(self.state.x_att)
            if self.is2d:
                self.axis_y.label = str(self.state.y_att)
        self.state.add_callback('x_att', update_axes)
        if self.is2d:
            self.state.add_callback('y_att', update_axes)
        self.figure = bqplot.Figure(scales=self.scales, animation_duration=0, axes=[
                                    self.axis_x, self.axis_y])
        self.figure.padding_y = 0
        self._fig_margin_default = self.figure.fig_margin
        self._fig_margin_zero = dict(self.figure.fig_margin)
        self._fig_margin_zero['left'] = 0
        self._fig_margin_zero['bottom'] = 0

        self.interact_map = {}
        self.interact_panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})

        self.interacts = []
        self.interacts.append((icon_pan, self.interact_panzoom))

        if self.is2d:
            self.interact_brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
            self.interact_brush.observe(self.update_brush, "brushing")
            self.interacts.append((icon_brush, self.interact_brush))

        self.interact_brush_x = bqplot.interacts.BrushIntervalSelector(scale=self.scale_x, color="green" )
        self.interact_brush_x.observe(self.update_brush_x, "brushing")
        self.interacts.append((icon_brush_x, self.interact_brush_x))

        if self.is2d:
            self.interact_brush_y = bqplot.interacts.BrushIntervalSelector(scale=self.scale_y, color="green", orientation='vertical')
            self.interact_brush_y.observe(self.update_brush_y, "brushing")
            self.interacts.append((icon_brush_y, self.interact_brush_y))


        self.widget_button_interact = mui.ToggleButtonGroup(exclusive=True, value=self.interact_panzoom, style={'margin': '4px'},
            children=[mui.ToggleButton(children=[icon], value=value) for k, (icon, value) in enumerate(self.interacts)]
        )
        self.widget_button_interact.observe(self.change_action, "value")

        self.widget_toolbar = self.widget_button_interact
        self.change_action()  # 'fire' manually for intial value

        link((self.state, 'x_min'), (self.scale_x, 'min'), float_or_none)
        link((self.state, 'x_max'), (self.scale_x, 'max'), float_or_none)
        link((self.state, 'y_min'), (self.scale_y, 'min'), float_or_none)
        link((self.state, 'y_max'), (self.scale_y, 'max'), float_or_none)

        on_change([(self.state, 'show_axes')])(self._sync_show_axes)

        self.create_tab()
        self.output_widget = widgets.Output()
        self.widget_toolbar = widgets.HBox([
                        self.session.application.widget_subset_select,
                        self.session.application.widget_subset_mode]
             )
        self.main_widget = widgets.VBox([
                self.widget_toolbar,
                widgets.HBox([self.figure, self.tab]),
                self.output_widget
            ])

    def show(self):
        display(self.main_widget)

    def create_tab(self):
        COLOR = 'blue'
        # self.widget_show_axes = widgets.Checkbox(value=True, description="Show axes")
        self.widget_show_axes = mui.Checkbox(checked=True, style={'color': COLOR})
        self.widget_show_axes_fcl = mui.FormControlLabel(control=self.widget_show_axes, label="Show axes")
        self.widgets_axis = []
        self.tab_general = widgets.VBox([
                self.widget_toolbar, self.widget_show_axes_fcl] + self.widgets_axis)#, self.widget_y_axis, self.widget_z_axis])
        children = [self.tab_general]
        self.tab = widgets.Tab(children)
        self.tab.set_title(0, "General")
        self.tab.set_title(1, "Axes")
        link((self.state, 'show_axes'), (self.widget_show_axes, 'checked'))

    def _sync_show_axes(self):
        # TODO: if moved to state, this would not rely on the widget
        self.axis_x.visible = self.axis_y.visible = self.state.show_axes
        self.figure.fig_margin = self._fig_margin_default if self.state.show_axes else self._fig_margin_zero

    @staticmethod
    def update_viewer_state(rec, context):
        print('update viewer state', rec, context)

    def change_action(self, *ignore):
        index = self.widget_button_interact.value
        self.figure.interaction = self.widget_button_interact.value #self.interact_map[self.button_action.value]
        if self.is2d:
            self.interact_brush.selected_x = []
            self.interact_brush_y.selected = []
        self.interact_brush_x.selected = []

    def update_brush(self, *ignore):
        with self.output_widget:
            if self.interact_brush.brushing is not None and self.interact_brush.selected_x is not None and len(self.interact_brush.selected_x):  # only select when we ended
                x = self.interact_brush.selected_x
                y = self.interact_brush.selected_y
                roi = RectangularROI(xmin=min(x), xmax=max(x), ymin=min(y), ymax=max(y))
                self.apply_roi(roi)

    def update_brush_x(self, *ignore):
        with self.output_widget:
            if not self.interact_brush_x.brushing:  # only select when we ended
                x = self.interact_brush_x.selected
                if x is not None and len(x):
                    roi = RangeROI(min=min(x), max=max(x), orientation='x')
                    self.apply_roi(roi)

    def update_brush_y(self, *ignore):
        with self.output_widget:
            if not self.interact_brush_y.brushing:  # only select when we ended
                y = self.interact_brush_y.selected
                if y is not None and len(y):
                    roi = RangeROI(min=min(y), max=max(y), orientation='y')
                    self.apply_roi(roi)

    def apply_roi(self, roi, use_current=False):
        # TODO: partial copy paste from glue/viewers/matplotlib/qt/data_viewer.py
        with self.output_widget:
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(data_collection=self._data,
                                       subset_state=subset_state,
                                       use_current=use_current)
                self._session.command_stack.do(cmd)
        # else:
        #     # Make sure we force a redraw to get rid of the ROI
        #    self.axes.figure.canvas.draw()

    def apply_roi(self, roi, use_current=False):
        with self.output_widget:
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(data_collection=self._data,
                                       subset_state=subset_state,
                                       use_current=use_current)
                self._session.command_stack.do(cmd)
            else:
                # Make sure we force a redraw to get rid of the ROI
                self.axes.figure.canvas.draw()

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/image/qt/data_viewer.py#L66

        # next lines don't work.. comp has no datetime?
        #x_date = any(comp.datetime for comp in self.state._get_x_components())
        #y_date = any(comp.datetime for comp in self.state._get_y_components())

        #if x_date or y_date:
        #    roi = roi.transformed(xfunc=mpl_to_datetime64 if x_date else None,
        #                          yfunc=mpl_to_datetime64 if y_date else None)
        if self.is2d:
            x_comp = self.state.x_att
            y_comp = self.state.y_att

            return roi_to_subset_state(roi, x_att=self.state.x_att, y_att=self.state.y_att)

    def limits_to_scales(self, *args):
        if self.state.x_min is not None and self.state.x_max is not None:
            self.scale_x.min = float(self.state.x_min)
            self.scale_x.max = float(self.state.x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            self.scale_y.min = float(self.state.y_min)
            self.scale_y.max = float(self.state.y_max)

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            if self.is2d:
                cls = BqplotScatterLayerArtist
            else:
                cls = BqplotHistogramLayerArtist
        else:
            cls = BqplotImageLayerArtist
        layer = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        self._add_layer_tab(layer)
        return layer

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            if self.is2d:
                cls = BqplotScatterLayerArtist
            else:
                cls = BqplotHistogramLayerArtist
        else:
            cls = BqplotImageLayerArtist
        layer = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        self._add_layer_tab(layer)
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass # print('redraw view', self.state.x_att, self.state.y_att)

    def redraw(self):
        pass



from glue.viewers.image.state import ImageViewerState
from glue.viewers.scatter.state import ScatterViewerState
from glue.viewers.image.composite_array import CompositeArray

from .image import BqplotImageLayerArtist
from .scatter import BqplotScatterLayerArtist
from ..utils import rgba_to_png_data
import numpy as np

class BqplotImageView(BqplotBaseView):
    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ImageViewerState
    large_data_size = 2e7

    def __init__(self, session):
        super(BqplotImageView, self).__init__(session)
        on_change([(self.state, 'aspect')])(self._sync_figure_aspect)
        self._sync_figure_aspect()

    def _sync_figure_aspect(self):
        with self.figure.hold_trait_notifications():
            if self.state.aspect == 'equal':
                self.figure.max_aspect_ratio = 1
                self.figure.min_aspect_ratio = 1
            else:
                self.figure.min_aspect_ratio = bqplot.Figure.min_aspect_ratio.default_value
                self.figure.max_aspect_ratio = bqplot.Figure.max_aspect_ratio.default_value

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        layer = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        self._add_layer_tab(layer)
        return layer

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = BqplotScatterLayerArtist
        else:
            cls = BqplotImageLayerArtist
        layer = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        self._add_layer_tab(layer)
        return layer

    def create_tab(self):
        super(BqplotImageView, self).create_tab()
        self.widgets_aspect = widgets.Checkbox(description='Equal aspect ratio')
        aspect_mapping = {'equal': True, 'auto': False}
        aspect_mapping_inverse = {True: 'equal', False: 'auto'}
        link((self.state, 'aspect'), (self.widgets_aspect, 'value'), lambda x: aspect_mapping[x], lambda x: aspect_mapping_inverse[x])

        self.tab_general.children += (self.widgets_aspect,)



class BqplotScatterView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = ScatterViewerState
    _data_artist_cls = BqplotScatterLayerArtist
    _subset_artist_cls = BqplotScatterLayerArtist
    large_data_size = 1e7

    def create_tab(self):
        super(BqplotScatterView, self).create_tab()
        self.widgets_axis = []
        for i, axis_name in enumerate('xy'):
            if hasattr(self.state, axis_name + '_att_helper'):
                widget_axis = glue_jupyter.widgets.component.Component(
                    self.state, axis_name + '_att', label=axis_name + ' axis'
                )
                self.widgets_axis.append(widget_axis)
        self.tab_general.children += tuple(self.widgets_axis)


from .histogram import BqplotHistogramLayerArtist, HistogramViewerState

class BqplotHistogramView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = HistogramViewerState
    _data_artist_cls = BqplotHistogramLayerArtist
    _subset_artist_cls = BqplotHistogramLayerArtist
    large_data_size = 1e5
    is2d = False

    def create_tab(self):
        super(BqplotHistogramView, self).create_tab()
        self.button_normalize = widgets.ToggleButton(
            value=False, description='normalize', tooltip='Normalize histogram')
        link((self.button_normalize, 'value'), (self.state, 'normalize'))

        self.button_cumulative = widgets.ToggleButton(
            value=False, description='cumulative', tooltip='cumulative histogram')
        link((self.button_cumulative, 'value'), (self.state, 'cumulative'))


        self.widgets_axis = []
        for i, axis_name in enumerate('x'):
            if hasattr(self.state, axis_name + '_att_helper'):
                widget_axis = glue_jupyter.widgets.component.Component(
                    self.state, axis_name + '_att', label=axis_name + ' axis'
                )
                self.widgets_axis.append(widget_axis)
        # @on_change([(self.state, 'hist_n_bin')])
        # def trigger():

        # self.widget_hist_x_min = widgets.FloatText(description='x min')
        # link((self.state, 'hist_x_min'), (self.widget_hist_x_min, 'value'))

        # self.widget_hist_n_bin = widgets.IntSlider(min=1, max=1000, step=1, description='bins')
        # link((self.state, 'hist_n_bin'), (self.widget_hist_n_bin, 'value'))

        self.tab_general.children += (widgets.HBox([self.button_normalize, self.button_cumulative] ),) + tuple(self.widgets_axis)


    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
