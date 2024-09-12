from itertools import chain
from glue.config import session_patch
from glue.core.state import PATH_PATCHES

TRANSLATION = PATH_PATCHES.copy()
TRANSLATION.update(
    {
        "glue.viewers.histogram.qt.data_viewer.HistogramViewer":
            "glue_jupyter.bqplot.histogram.BqplotHistogramView",  # remove?
        "glue_qt.viewers.histogram.data_viewer.HistogramViewer":
            "glue_jupyter.bqplot.histogram.BqplotHistogramView",
        "glue_qt.viewers.image.data_viewer.ImageViewer":
            "glue_jupyter.bqplot.image.BqplotImageView",
        "glue_qt.viewers.profile.data_viewer.ProfileViewer":
            "glue_jupyter.bqplot.profile.BqplotProfileView",
        "glue_qt.viewers.scatter.data_viewer.ScatterViewer":
            "glue_jupyter.bqplot.scatter.BqplotScatterView",
        "glue.viewers.image.layer_artist.ImageLayerArtist":
            "glue_jupyter.bqplot.image.BqplotImageLayerArtist",
        "glue.viewers.image.layer_artist.ImageSubsetLayerArtist":
            "glue_jupyter.bqplot.image.BqplotImageSubsetLayerArtist",
        "glue_qt.viewers.profile.layer_artist.QThreadedProfileLayerArtist":
            "glue_jupyter.bqplot.profile.BqplotProfileLayerArtist",
        "glue_qt.viewers.histogram.layer_artist.QThreadedHistogramLayerArtist":
            "glue_jupyter.bqplot.histogram.BqplotHistogramLayerArtist",
        "glue.viewers.histogram.layer_artist.QThreadedHistogramLayerArtist":
            "glue_jupyter.bqplot.histogram.BqplotHistogramLayerArtist",  # remove?
        "glue.viewers.scatter.layer_artist.ScatterLayerArtist":
            "glue_jupyter.bqplot.scatter.BqplotScatterLayerArtist",
        "glue.viewers.image.state.ImageLayerState":
            "glue_jupyter.bqplot.image.state.BqplotImageLayerState",
        "glue.viewers.image.state.ImageViewerState":
            "glue_jupyter.bqplot.image.state.BqplotImageViewerState",
        "glue_vispy_viewers.scatter.qt.scatter_viewer.VispyScatterViewer":
            "glue_vispy_viewers.scatter.jupyter.scatter_viewer.JupyterVispyScatterViewer",
        "glue_vispy_viewers.volume.qt.volume_viewer.VispyVolumeViewer":
            "glue_vispy_viewers.volume.jupyter.volume_viewer.JupyterVispyVolumeViewer",
        "glue_wwt.viewer.qt_data_viewer.WWTQtViewer":
            "glue_wwt.viewer.jupyter_viewer.WWTJupyterViewer",
    }
)


@session_patch()
def translate_qt_to_jupyter_session(session):

    if session['__main__']['_type'] != 'glue_qt.app.application.GlueApplication':
        return

    session["__main__"]["_type"] = "glue_jupyter.app.JupyterApplication"
    session["__main__"]["viewers"] = list(chain(*session["__main__"]["viewers"]))

    for key in session:

        while session[key]["_type"] in TRANSLATION:
            session[key]["_type"] = TRANSLATION[session[key]["_type"]]

        if "layers" in session[key]:
            layers = session[key]["layers"]
            for layer in layers:
                while layer["_type"] in TRANSLATION:
                    layer["_type"] = TRANSLATION[layer["_type"]]
