# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "glue-jupyter"
copyright = "2018-2023, Maarten A. Breddels and Thomas Robitaille"
author = "Maarten A. Breddels and Thomas Robitaille"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo',
              'sphinx.ext.mathjax',
              'sphinx.ext.viewcode',
              'nbsphinx',
              'numpydoc',
              'sphinx_automodapi.automodapi',
              'sphinx_automodapi.smart_resolver']

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autoclass_content = "both"

default_role = 'obj'
nitpicky = True
nitpick_ignore = [('py:class', 'ipywidgets.widgets.widget_box.Box'),
                  ('py:class', 'ipywidgets.widgets.widget_box.VBox'),
                  ('py:class', 'ipywidgets.widgets.widget.Widget'),
                  ('py:class', 'ipywidgets.widgets.widget.LoggingHasTraits'),
                  ('py:class', 'ipywidgets.widgets.domwidget.DOMWidget'),
                  ('py:class', 'ipywidgets.widgets.widget_core.CoreWidget'),
                  ('py:class', 'ipyvuetify.VuetifyTemplate.VuetifyTemplate'),
                  ('py:class', 'traitlets.traitlets.HasTraits'),
                  ('py:class', 'traitlets.traitlets.HasDescriptors'),
                  ('py:class', 'echo.core.HasCallbackProperties'),
                  ('py:class', 'glue.viewers.image.layer_artist.ImageLayerArtist'),
                  ('py:class', 'glue.viewers.image.layer_artist.BaseImageLayerArtist'),
                  ('py:class', 'glue_vispy_viewers.volume.layer_state.VolumeLayerState'),
                  ('py:class', 'glue_vispy_viewers.common.layer_state.VispyLayerState')]

automodapi_inheritance_diagram = False

viewcode_follow_imported_members = False

numpydoc_show_class_members = False
autosummary_generate = True
automodapi_toctreedirnm = "api"

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.11', None),
    'echo': ('https://echo.readthedocs.io/en/latest/', None),
    'ipywidgets': ('https://ipywidgets.readthedocs.io/en/stable/', None),
    'traitlets': ('https://traitlets.readthedocs.io/en/stable/', None),
    'glue': ('https://glue-core.readthedocs.io/en/latest/', None),
    'glueviz': ('https://docs.glueviz.org/en/latest/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_theme_options = {'navigation_with_keys': False}

