import pytest
from glue.core import Data
import glue_jupyter as gj


@pytest.fixture
def dataxyz():
    data = Data(x=[1, 2, 3], y=[2, 3, 4], z=[5, 6, 7], label="xyz data")
    return data


@pytest.fixture
def dataxz():
    ox = 0
    oy = 1
    data = Data(x=[1 + ox, 2 + ox, 3 + ox], z=[2 + oy, 3 + oy, 4 + oy], label="xy data")
    return data


@pytest.fixture
def datax():
    ox = 0
    data = Data(x=[1 + ox, 2 + ox, 3 + ox], label="x data")
    return data


@pytest.fixture
def data_unlinked():
    data = Data(a=[1, 2], label="unlinked data")
    return data


@pytest.fixture
def data_volume():
    return gj.example_volume()


@pytest.fixture
def data_image():
    return gj.example_image()


@pytest.fixture
def app(dataxyz, datax, dataxz, data_volume, data_image):
    app = gj.jglue(dataxyz=dataxyz, dataxz=dataxz, datax=datax)
    app.add_link(dataxyz, 'x', dataxz, 'x')
    app.add_link(dataxyz, 'y', dataxz, 'z')
    app.add_link(dataxyz, 'x', datax, 'x')
    app.add_data(data_volume=data_volume)
    app.add_data(data_image=data_image)
    app.add_link(data_image, 'Pixel Axis 0 [y]', dataxyz, 'y')
    app.add_link(data_image, 'Pixel Axis 1 [x]', dataxyz, 'x')
    app.add_link(data_volume, 'Pixel Axis 0 [z]', dataxyz, 'z')
    app.add_link(data_volume, 'Pixel Axis 1 [y]', dataxyz, 'y')
    app.add_link(data_volume, 'Pixel Axis 2 [x]', dataxyz, 'x')
    return app
