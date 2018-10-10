from __future__ import absolute_import
from glue.core import message as msg
import six

# from glue.core.session import Session
# from glue.viewers.scatter.layer_artist import ScatterLayerArtist


def load(path):
    from glue.core.data_factories import load_data
    return load_data(path)

def jglue(*args, **kwargs):
    from glue.core import DataCollection
    from glue.app.qt import GlueApplication
    from glue.qglue import parse_data, parse_links
    from glue.core.data_factories import load_data
    from .app import JupyterApplication

    links = kwargs.pop('links', None)

    dc = DataCollection()
    for label, data in kwargs.items():
        if isinstance(data, six.string_types):
            data = load_data(data)
        dc.extend(parse_data(data, label))
    for data in args:
        dc.append(data)

    if links is not None:
        dc.add_link(parse_links(dc, links))

    japp = JupyterApplication(dc)
    return japp

def example_data_xyz(seed=42, N=500, loc=0, scale=1):
    from glue.core import Data
    import numpy as np
    rng = np.random.RandomState(seed)
    x, y, z = rng.normal(loc, scale, size=(3, N))
    vx = x - x.mean()
    vy = y - y.mean()
    vz = z - z.mean()
    speed = np.sqrt(vx**2 + vy**2 + vz**2)
    data_xyz = Data(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, speed=speed, label="xyz")
    return data_xyz

def example_volume(shape=64, limits=[-4, 4]):
    """Creates a test data set containing a ball"""
    from glue.core import Data
    import numpy as np
    import ipyvolume as ipv
    ball_data = ipv.examples.ball(shape=shape, limits=limits, show=False, draw=False)
    data = Data()
    data.add_component(ball_data, label='intensity')
    return data

def example_image(shape=64, limits=[-4, 4]):
    """Creates a test data set containing a ball"""
    from glue.core import Data, Coordinates
    import numpy as np
    import ipyvolume as ipv
    x = np.linspace(-3, 3, num=shape)
    X, Y = np.meshgrid(x, x)
    rho = 0.8
    I = np.exp(-X**2-Y**2-2*X*Y*rho)
    data = Data()
    data.coords = Coordinates()
    data.add_component(I, label='intensity')
    return data
