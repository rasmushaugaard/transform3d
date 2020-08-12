from tempfile import TemporaryFile

import numpy as np

from .. import Transform


def test_transform_operations():
    p, rotvec = (1, 2, 3), (.1, .2, .3)
    f = Transform(p=p, rotvec=rotvec)
    assert f.equals(Transform(p=p) @ Transform(rotvec=rotvec))
    assert f.inv.equals(Transform(matrix=np.linalg.inv(f.matrix)))


def test_point_transformation():
    t = Transform.random()
    p, R = t.p, t.R

    for pts in np.random.randn(3), np.random.randn(100, 3):
        assert np.all(t.rotate(pts) == pts @ R.T)
        assert np.all(t @ pts == pts @ R.T + p)


def test_save_load():
    t = Transform.random()
    with TemporaryFile() as f:
        t.save(f)
        f.seek(0)
        t_ = Transform.load(f)
    assert t_.equals(t)


def test_list():
    t = Transform(p=(1, 2, 3), rotvec=(.1, .2, .3))
    assert t[2] == 3
    xyz_rotvec = list(t)
    assert xyz_rotvec == [1, 2, 3, .1, .2, .3]
