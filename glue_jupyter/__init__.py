from __future__ import absolute_import

from ._version import __version__  # noqa
from .app import JupyterApplication  # noqa

__all__ = ['jglue', 'example_data_xyz', 'example_image', 'example_volume',
           'JupyterApplication']


def jglue(*args, **kwargs):
    """
    Create a new Jupyter-based glue application.

    It is typically easiest to call this function without arguments and load
    data and add links separately in subsequent calls. However, this function
    can also take the same inputs as the `~glue.qglue.qglue` function.

    Once this function is called, it will return a
    `~glue_jupyter.JupyterApplication` object, which can then be used to
    load data, set up links, and create visualizations. See the documentation
    for that class for more details.
    """
    show = kwargs.pop('show', False)
    from glue.core import DataCollection
    from glue.qglue import parse_data, parse_links
    from glue.core.data_factories import load_data

    links = kwargs.pop('links', None)

    dc = DataCollection()
    for label, data in kwargs.items():
        if isinstance(data, str):
            data = load_data(data)
        dc.extend(parse_data(data, label))
    for data in args:
        dc.append(data)

    if links is not None:
        dc.add_link(parse_links(dc, links))

    japp = JupyterApplication(dc)
    if show:
        display(app)
    return japp


def example_data_xyz(seed=42, N=500, loc=0, scale=1, label='xyz'):
    """
    Create an example dataset with three attributes x, y, and z set to random
    values.
    """
    from glue.core import Data
    import numpy as np
    rng = np.random.RandomState(seed)
    x, y, z = rng.normal(loc, scale, size=(3, N))
    vx = x - x.mean()
    vy = y - y.mean()
    vz = z - z.mean()
    speed = np.sqrt(vx**2 + vy**2 + vz**2)
    data_xyz = Data(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, speed=speed, label=label)
    return data_xyz


def example_volume(shape=64, limits=[-4, 4]):
    """
    Creates a test 3-d dataset containing a ball.
    """
    from glue.core import Data
    import ipyvolume as ipv
    ball_data = ipv.examples.ball(shape=shape, limits=limits, show=False, draw=False)
    data = Data()
    data.add_component(ball_data, label='intensity')
    return data


def example_image(shape=64, limits=[-4, 4]):
    """
    Creates a test 2-d dataset containing an image.
    """
    from glue.core import Data, Coordinates
    import numpy as np
    x = np.linspace(-3, 3, num=shape)
    X, Y = np.meshgrid(x, x)
    rho = 0.8
    I = np.exp(-X**2-Y**2-2*X*Y*rho)
    data = Data()
    data.coords = Coordinates()
    data.add_component(I, label='intensity')
    return data
