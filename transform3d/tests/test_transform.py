import numpy as np

from .. import Transform


def test_transform_operations(atol=1e-13):
    for _ in range(100):
        t = np.random.randn(3)
        rpy = np.random.randn(3)
        f = Transform(t=t, rpy=rpy)

        # matmul
        f_ = Transform(t=t) @ Transform(rpy=rpy)
        err = np.abs(f.matrix - f_.matrix).max()
        assert err < atol, err

        # inverse
        assert np.abs((f.inv @ f).matrix - np.eye(4)).max() < atol
        assert np.abs(np.linalg.inv(f.matrix) - f.inv.matrix).max() < atol


def test_point_identity_transformation():
    t = Transform()
    assert np.all(np.ones(3) == t @ np.ones(3))
    p = np.random.randn(100, 3)
    assert np.all(p == t @ p)
