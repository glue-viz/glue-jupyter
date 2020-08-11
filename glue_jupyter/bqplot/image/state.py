from echo import CallbackProperty

from glue.viewers.image.state import ImageLayerState


class BqplotImageLayerState(ImageLayerState):

    # TODO: change contour_visible to False by default once it can be toggled in UI

    bitmap_visible = CallbackProperty(True, 'whether to show the image as a bitmap')
    contour_visible = CallbackProperty(True, 'whether to show the image as contours')
