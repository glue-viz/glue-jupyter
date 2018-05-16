import numpy as np
import bqplot
import ipywidgets as widgets
import ipywidgets.widgets.trait_types as tt
from IPython.display import display

from glue.core.layer_artist import LayerArtistBase
from glue.core.roi import RectangularROI, RangeROI
from glue.core.command import ApplySubsetState
from glue.viewers.histogram.state import HistogramViewerState, HistogramLayerState

from ..link import link

# FIXME: monkey patch ipywidget to accept anything
tt.Color.validate = lambda self, obj, value: value


from .. import IPyWidgetView


class BqplotHistogramLayerArtist(LayerArtistBase):
    _layer_state_cls = HistogramLayerState

    def __init__(self, view, viewer_state, layer, layer_state):
        super(BqplotHistogramLayerArtist, self).__init__(layer)
        self.reset_cache()
        self.view = view
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        self._viewer_state = viewer_state
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)
        self.bars = bqplot.Bars(
            scales=self.view.scales, x=[0, 1], y=[0, 1])
        self.view.figure.marks = list(self.view.figure.marks) + [self.bars]
        link((self.bars, 'colors'), (self.state, 'color'),
             lambda x: x[0], lambda x: [x])
        #link((self.bars, 'default_opacities'), (self.state, 'alpha'), lambda x: x[0], lambda x: [x])
        #link((self.bars, 'default_size'), (self.state, 'size'))

        self._viewer_state.add_global_callback(self._update_histogram)
        self.state.add_global_callback(self._update_histogram)
        self.bins = None

    def reset_cache(self):
        self._last_viewer_state = {}
        self._last_layer_state = {}

    def _update_xy_att(self, *args):
        self.update()

    def redraw(self):
        pass

    def clear(self):
        pass

    def _calculate_histogram(self):
        # TODO: comes from glue/viewers/histogram/layer_artist.py

        # self.remove()

        try:
            x = self.layer[self._viewer_state.x_att]
        except AttributeError:
            return
        except (IncompatibleAttribute, IndexError):
            self.disable_invalid_attributes(self._viewer_state.x_att)
            return
        else:
            self.enable()

        x = x[~np.isnan(x) & (x >= self._viewer_state.hist_x_min) &
                             (x <= self._viewer_state.hist_x_max)]

        if len(x) == 0:
            self.redraw()
            return

        # For histogram
        xmin, xmax = sorted([self._viewer_state.hist_x_min,
                             self._viewer_state.hist_x_max])
        if self._viewer_state.x_log:
            range = None
            bins = np.logspace(np.log10(xmin), np.log10(
                xmax), self._viewer_state.hist_n_bin)
        else:
            range = [xmin, xmax]
            bins = self._viewer_state.hist_n_bin

        self.hist_unscaled, self.bins = np.histogram(x, bins, range=range)

    def _scale_histogram(self):
        # TODO: comes from glue/viewers/histogram/layer_artist.py
        if self.bins is None:
            return  # can happen when the subset is empty

        if self.bins.size == 0 or self.hist_unscaled.sum() == 0:
            return

        self.hist = self.hist_unscaled.astype(np.float)
        dx = self.bins[1] - self.bins[0]

        if self._viewer_state.cumulative:
            self.hist = self.hist.cumsum()
            if self._viewer_state.normalize:
                self.hist /= self.hist.max()
        elif self._viewer_state.normalize:
            self.hist /= (self.hist.sum() * dx)

        bottom = 0 if not self._viewer_state.y_log else 1e-100

        # TODO this won't work for log ...
        centers = (self.bins[:-1] + self.bins[1:]) / 2
        assert len(centers) == len(self.hist)
        self.bars.x = centers
        self.bars.y = self.hist

        # We have to do the following to make sure that we reset the y_max as
        # needed. We can't simply reset based on the maximum for this layer
        # because other layers might have other values, and we also can't do:
        #
        #   self._viewer_state.y_max = max(self._viewer_state.y_max, result[0].max())
        #
        # because this would never allow y_max to get smaller.

        self.state._y_max = self.hist.max()
        if self._viewer_state.y_log:
            self.state._y_max *= 2
        else:
            self.state._y_max *= 1.2

        if self._viewer_state.y_log:
            self.state._y_min = self.hist[self.hist > 0].min() / 10
        else:
            self.state._y_min = 0

        largest_y_max = max(getattr(layer, '_y_max', 0)
                            for layer in self._viewer_state.layers)
        if largest_y_max != self._viewer_state.y_max:
            self._viewer_state.y_max = largest_y_max

        smallest_y_min = min(getattr(layer, '_y_min', np.inf)
                             for layer in self._viewer_state.layers)
        if smallest_y_min != self._viewer_state.y_min:
            self._viewer_state.y_min = smallest_y_min

        self.redraw()

    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def _update_histogram(self, force=False, **kwargs):
        # TODO: comes from glue/viewers/histogram/layer_artist.py
        if (self._viewer_state.hist_x_min is None or
                self._viewer_state.hist_x_max is None or
                self._viewer_state.hist_n_bin is None or
                self._viewer_state.x_att is None or
                self.state.layer is None):
            return
        # Figure out which attributes are different from before. Ideally we shouldn't
        # need this but currently this method is called multiple times if an
        # attribute is changed due to x_att changing then hist_x_min, hist_x_max, etc.
        # If we can solve this so that _update_histogram is really only called once
        # then we could consider simplifying this. Until then, we manually keep track
        # of which properties have changed.

        changed = set()

        if not force:

            for key, value in self._viewer_state.as_dict().items():
                if value != self._last_viewer_state.get(key, None):
                    changed.add(key)

            for key, value in self.state.as_dict().items():
                if value != self._last_layer_state.get(key, None):
                    changed.add(key)

        self._last_viewer_state.update(self._viewer_state.as_dict())
        self._last_layer_state.update(self.state.as_dict())

        if force or any(prop in changed for prop in ('layer', 'x_att', 'hist_x_min', 'hist_x_max', 'hist_n_bin', 'x_log')):
            self._calculate_histogram()
            force = True  # make sure scaling and visual attributes are updated

        if force or any(prop in changed for prop in ('y_log', 'normalize', 'cumulative')):
            self._scale_histogram()

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder', 'visible')):
            self._update_visual_attributes()

    def update(self):
        self._update_histogram(force=True)
        self.redraw()


class BqplotHistogramView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    _state_cls = HistogramViewerState
    _data_artist_cls = BqplotHistogramLayerArtist
    _subset_artist_cls = BqplotHistogramLayerArtist
    large_data_size = 1e5

    def __init__(self, session):
        super(BqplotHistogramView, self).__init__(session)
        # session.hub.subscribe(self, SubsetCreateMessage,
        #                       handler=self.receive_message)
        self.state = self._state_cls()

        self.scale_x = bqplot.LinearScale(min=0, max=1)
        self.scale_y = bqplot.LinearScale(min=0, max=1)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        self.axis_x = bqplot.Axis(
            scale=self.scale_x, grid_lines='solid', label='x')
        self.axis_y = bqplot.Axis(scale=self.scale_y, orientation='vertical', tick_format='0.2f',
                                  grid_lines='solid', label='y')

        def update_axes(*ignore):
            self.axis_x.label = str(self.state.x_att)
            self.axis_y.label = 'Number'  # TODO: should this be fixed, not for normalized
        self.state.add_callback('x_att', update_axes)
        #self.state.add_callback('y_att', update_axes)
        self.figure = bqplot.Figure(scales=self.scales, axes=[
                                    self.axis_x, self.axis_y])

        actions = ['move', 'brush', 'brush x']  # , 'brush y']
        self.interact_map = {}
        self.panzoom = bqplot.PanZoom(
            scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.interact_map['move'] = self.panzoom

        self.brush = bqplot.interacts.BrushSelector(
            x_scale=self.scale_x, y_scale=self.scale_y, color="green")
        self.interact_map['brush'] = self.brush
        self.brush.observe(self.update_brush, "brushing")

        self.brush_x = bqplot.interacts.BrushIntervalSelector(
            scale=self.scale_x, color="green")
        self.interact_map['brush x'] = self.brush_x
        self.brush_x.observe(self.update_brush_x, "brushing")

        self.brush_y = bqplot.interacts.BrushIntervalSelector(
            scale=self.scale_y, color="green")
        self.interact_map['brush y'] = self.brush_y
        self.brush_y.observe(self.update_brush_y, "brushing")

        self.button_action = widgets.ToggleButtons(description='Mode: ', options=[(action, action) for action in actions],
                                                   icons=["arrows", "pencil-square-o"])
        self.button_action.observe(self.change_action, "value")
        self.change_action()  # 'fire' manually for intial value

        self.button_normalize = widgets.ToggleButton(
            value=False, description='normalize', tooltip='Normalize histogram')
        link((self.button_normalize, 'value'), (self.state, 'normalize'))

        self.button_cumulative = widgets.ToggleButton(
            value=False, description='cumulative', tooltip='cumulative histogram')
        link((self.button_cumulative, 'value'), (self.state, 'cumulative'))

        self.box_state_options = widgets.HBox(
            children=[self.button_normalize, self.button_cumulative])

        self.button_box = widgets.VBox(
            children=[self.button_action, self.box_state_options])
        self.main_box = widgets.VBox(children=[self.button_box, self.figure])


#         self.state.add_callback('y_att', self._update_axes)
#         self.state.add_callback('x_log', self._update_axes)
#         self.state.add_callback('y_log', self._update_axes)

        self.state.add_callback('x_min', self.limits_to_scales)
        self.state.add_callback('x_max', self.limits_to_scales)
        self.state.add_callback('y_min', self.limits_to_scales)
        self.state.add_callback('y_max', self.limits_to_scales)

    @staticmethod
    def update_viewer_state(rec, context):
        print('update viewer state', rec, context)

    def change_action(self, *ignore):
        self.figure.interaction = self.interact_map[self.button_action.value]
        self.brush.selected = []
        self.brush_x.selected = []

    def update_brush(self, *ignore):
        if not self.brush.brushing:  # only select when we ended
            (x1, y1), (x2, y2) = self.brush.selected
            x = [x1, x2]
            y = [y1, y2]
            roi = RectangularROI(xmin=min(x), xmax=max(x),
                                 ymin=min(y), ymax=max(y))
            self.apply_roi(roi)

    def update_brush_x(self, *ignore):
        if not self.brush_x.brushing:  # only select when we ended
            x = self.brush_x.selected
            if x is not None and len(x):
                roi = RangeROI(min=min(x), max=max(x), orientation='x')
                self.apply_roi(roi)

    def update_brush_y(self, *ignore):
        if not self.brush_y.brushing:  # only select when we ended
            y = self.brush_y.selected
            if y is not None and len(y):
                roi = RangeROI(min=min(y), max=max(y), orientation='y')
                self.apply_roi(roi)

    def apply_roi(self, roi):
        # TODO: partial copy paste from glue/viewers/matplotlib/qt/data_viewer.py
        if len(self.layers) > 0:
            subset_state = self._roi_to_subset_state(roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state)
            self._session.command_stack.do(cmd)
        # else:
        #     # Make sure we force a redraw to get rid of the ROI
        #    self.axes.figure.canvas.draw()

    def apply_roi(self, roi):
        if len(self.layers) > 0:
            subset_state = self._roi_to_subset_state(roi)
            cmd = ApplySubsetState(data_collection=self._data,
                                   subset_state=subset_state)
            self._session.command_stack.do(cmd)
        else:
            # Make sure we force a redraw to get rid of the ROI
            self.axes.figure.canvas.draw()

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

        x_comp = self.state.x_att.parent.get_component(self.state.x_att)

        return x_comp.subset_from_roi(self.state.x_att, roi_new, coord='x')

    def show(self):
        display(self.main_box)

    def limits_to_scales(self, *args):
        if self.state.hist_x_min is not None and self.state.hist_x_max is not None:
            self.scale_x.min = float(self.state.hist_x_min)
            self.scale_x.max = float(self.state.hist_x_max)

        if self.state.y_min is not None and self.state.y_max is not None:
            self.scale_y.min = self.state.y_min
            self.scale_y.max = self.state.y_max

    def get_subset_layer_artist(*args, **kwargs):
        layer = DataViewerWithState.get_data_layer_artist(*args, **kwargs)
        #layer.bars.colors = ['orange']
        return layer

    def receive_message(self, message):
        print("Message received:")
        print("{0}".format(message))
        self.last_msg = message

    def redraw(self):
        pass  # print('redraw view', self.state.x_att, self.state.y_att)


from glue.viewers.common.qt.data_viewer_with_state import DataViewerWithState
BqplotHistogramView.add_data = DataViewerWithState.add_data
BqplotHistogramView.add_subset = DataViewerWithState.add_subset
BqplotHistogramView.get_data_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotHistogramView.get_subset_layer_artist = DataViewerWithState.get_data_layer_artist
#BqplotView.get_layer_artist = DataViewerWithState.get_layer_artist
#s = histogram2d(catalog.id['RAJ2000'], catalog.id['DEJ2000'], dc)
