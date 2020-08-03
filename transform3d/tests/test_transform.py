from tempfile import TemporaryFile

import numpy as np

from .. import Transform


def test_transform_operations():
    t, rotvec = (1, 2, 3), (.1, .2, .3)
    f = Transform(t=t, rotvec=rotvec)
    assert f.equals(Transform(t=t) @ Transform(rotvec=rotvec))
    assert f.inv.equals(Transform(matrix=np.linalg.inv(f.matrix)))


def test_point_transformation():
    T = Transform.random()
    t, R = T.t, T.R

    for p in np.random.randn(3), np.random.randn(100, 3):
        assert np.all(T.rotate(p) == p @ R.T)
        assert np.all(T @ p == p @ R.T + t)


def test_save_load():
    t = Transform.random()
    with TemporaryFile() as f:
        t.save(f)
        f.seek(0)
        t_ = Transform.load(f)
    assert t_.equals(t)
