from itertools import chain

# Translations common to all widget backends
_BASE_TRANSLATION = {
    "glue_wwt.viewer.qt_data_viewer.WWTQtViewer":
        "glue_wwt.viewer.jupyter_viewer.WWTJupyterViewer",
}

# 2D viewer translations: bqplot
_BQPLOT_TRANSLATION = {
    "glue.viewers.histogram.qt.data_viewer.HistogramViewer":
        "glue_jupyter.bqplot.histogram.BqplotHistogramView",
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
        "glue_jupyter.bqplot.histogram.BqplotHistogramLayerArtist",
    "glue.viewers.scatter.layer_artist.ScatterLayerArtist":
        "glue_jupyter.bqplot.scatter.BqplotScatterLayerArtist",
    "glue.viewers.image.state.ImageLayerState":
        "glue_jupyter.bqplot.image.state.BqplotImageLayerState",
    "glue.viewers.image.state.ImageViewerState":
        "glue_jupyter.bqplot.image.state.BqplotImageViewerState",
}

# 2D viewer translations: matplotlib
_MATPLOTLIB_TRANSLATION = {
    "glue.viewers.histogram.qt.data_viewer.HistogramViewer":
        "glue_jupyter.matplotlib.histogram.HistogramJupyterViewer",
    "glue_qt.viewers.histogram.data_viewer.HistogramViewer":
        "glue_jupyter.matplotlib.histogram.HistogramJupyterViewer",
    "glue_qt.viewers.image.data_viewer.ImageViewer":
        "glue_jupyter.matplotlib.image.ImageJupyterViewer",
    "glue_qt.viewers.profile.data_viewer.ProfileViewer":
        "glue_jupyter.matplotlib.profile.ProfileJupyterViewer",
    "glue_qt.viewers.scatter.data_viewer.ScatterViewer":
        "glue_jupyter.matplotlib.scatter.ScatterJupyterViewer",
    "glue_qt.viewers.profile.layer_artist.QThreadedProfileLayerArtist":
        "glue.viewers.profile.layer_artist.ProfileLayerArtist",
    "glue_qt.viewers.histogram.layer_artist.QThreadedHistogramLayerArtist":
        "glue.viewers.histogram.layer_artist.HistogramLayerArtist",
    "glue.viewers.histogram.layer_artist.QThreadedHistogramLayerArtist":
        "glue.viewers.histogram.layer_artist.HistogramLayerArtist",
}

# 3D viewer translations: vispy (Qt vispy -> Jupyter vispy)
_VISPY_TRANSLATION = {
    "glue_vispy_viewers.scatter.qt.scatter_viewer.VispyScatterViewer":
        "glue_vispy_viewers.scatter.jupyter.scatter_viewer.JupyterVispyScatterViewer",
    "glue_vispy_viewers.volume.qt.volume_viewer.VispyVolumeViewer":
        "glue_vispy_viewers.volume.jupyter.volume_viewer.JupyterVispyVolumeViewer",
}

# 3D viewer translations: ipyvolume (Qt vispy -> ipyvolume)
_IPYVOLUME_TRANSLATION = {
    "glue_vispy_viewers.scatter.qt.scatter_viewer.VispyScatterViewer":
        "glue_jupyter.ipyvolume.scatter.viewer.IpyvolumeScatterView",
    "glue_vispy_viewers.volume.qt.volume_viewer.VispyVolumeViewer":
        "glue_jupyter.ipyvolume.volume.viewer.IpyvolumeVolumeView",
    "glue_vispy_viewers.scatter.layer_artist.ScatterLayerArtist":
        "glue_jupyter.ipyvolume.scatter.layer_artist.IpyvolumeScatterLayerArtist",
    "glue_vispy_viewers.volume.layer_artist.VolumeLayerArtist":
        "glue_jupyter.ipyvolume.volume.layer_artist.IpyvolumeVolumeLayerArtist",
}


def _build_translation(widget_2d='bqplot', widget_3d='vispy'):
    translation = _BASE_TRANSLATION.copy()

    if widget_2d == 'bqplot':
        translation.update(_BQPLOT_TRANSLATION)
    elif widget_2d == 'matplotlib':
        translation.update(_MATPLOTLIB_TRANSLATION)
    else:
        raise ValueError("widget_2d should be 'bqplot' or 'matplotlib'")

    if widget_3d == 'vispy':
        translation.update(_VISPY_TRANSLATION)
    elif widget_3d == 'ipyvolume':
        translation.update(_IPYVOLUME_TRANSLATION)
    else:
        raise ValueError("widget_3d should be 'vispy' or 'ipyvolume'")

    return translation


def translate_qt_to_jupyter_session(session, widget_2d='bqplot', widget_3d='vispy'):

    if session['__main__']['_type'] != 'glue_qt.app.application.GlueApplication':
        return

    translation = _build_translation(widget_2d=widget_2d, widget_3d=widget_3d)

    session["__main__"]["_type"] = "glue_jupyter.app.JupyterApplication"
    session["__main__"]["viewers"] = list(chain(*session["__main__"]["viewers"]))

    # Remove Qt-specific plugins that aren't available in the Jupyter environment
    if "plugins" in session["__main__"]:
        session["__main__"]["plugins"] = [
            p for p in session["__main__"]["plugins"]
            if not p.startswith(("glue_qt.", "glue_vispy_viewers."))
        ]

    for key in session:

        while session[key]["_type"] in translation:
            session[key]["_type"] = translation[session[key]["_type"]]

        if "layers" in session[key]:
            layers = session[key]["layers"]
            for layer in layers:
                while layer["_type"] in translation:
                    layer["_type"] = translation[layer["_type"]]
