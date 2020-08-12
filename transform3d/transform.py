from typing import Union, Sequence
from functools import lru_cache

from werkzeug.utils import cached_property
import numpy as np
from scipy.spatial.transform import Rotation

L = Union[Sequence, np.ndarray]


def _immutable(a) -> np.ndarray:
    if isinstance(a, np.ndarray):
        if a.flags.writeable:
            a = a.copy()
            a.setflags(write=False)
    else:
        a = np.array(a)
        a.setflags(write=False)
    return a


_R_ident = _immutable(np.eye(3))
_r_ident = Rotation.identity()
_p_ident = _immutable(np.zeros(3))


class Transform:
    def __init__(self, matrix: L = None, R: L = None, p: L = None, r: Rotation = None,
                 quat: L = None, euler: L = None, rpy: L = None, rotvec: L = None, inv=None, degrees=False):
        self._r = None
        self._inv = inv  # type: Union[None, Transform]
        if matrix is not None:
            self.matrix = _immutable(matrix)
            self.R = matrix[:3, :3]
            self.p = matrix[:3, 3]
        else:
            if R is not None:
                self.R = _immutable(R)
            else:
                # if rotation is not provided as a matrix, convert using scipy.spatial.Rotation
                if quat is not None:
                    r = Rotation.from_quat(quat)
                elif rotvec is not None:
                    r = Rotation.from_rotvec(np.deg2rad(rotvec) if degrees else rotvec)
                elif euler is not None:
                    seq, angles = euler
                    r = Rotation.from_euler(seq, angles, degrees=degrees)
                elif rpy is not None:
                    r = Rotation.from_euler('xyz', rpy, degrees=degrees)

                self._r = r
                if r is None:  # no rotation provided
                    self.R = _R_ident
                else:
                    self.R = self._r.as_matrix()
                    self.R.setflags(write=False)
            self.p = _p_ident if p is None else _immutable(p)
            self.matrix = np.eye(4)
            self.matrix[:3, :3] = self.R
            self.matrix[:3, 3] = self.p
            self.matrix.setflags(write=False)

    @property
    def inv(self):
        if self._inv is None:
            self._inv = Transform(
                R=self.R.T,
                p=-self.p @ self.R,
                inv=self
            )
        return self._inv

    @property
    def r(self) -> Rotation:
        if self._r is None:
            self._r = Rotation.from_matrix(self.R)
        return self._r

    @cached_property
    def quat(self):
        return self.r.as_quat()

    @cached_property
    def rotvec(self):
        return self.r.as_rotvec()

    @lru_cache()
    def euler(self, seq):
        return self.r.as_euler(seq)

    @property
    def rpy(self):
        return self.euler('xyz')

    @property
    def xyz_rotvec(self):
        return (*self.p, *self.rotvec)

    def __len__(self):
        return 6

    def __getitem__(self, i: int):
        return self.xyz_rotvec[i]

    @classmethod
    def from_xyz_rotvec(cls, xyz_rotvec):
        return cls(p=xyz_rotvec[:3], rotvec=xyz_rotvec[3:])

    def __matmul__(self, other):
        if isinstance(other, Transform):
            matrix = self.matrix @ other.matrix
            matrix.setflags(write=False)
            return Transform(matrix=matrix)
        elif isinstance(other, (np.ndarray, Sequence)):
            return np.asarray(other) @ self.R.T + self.p
        else:
            raise NotImplementedError()

    def rotate(self, other):
        other = np.asarray(other)
        d = other.shape[-1]
        if d == 6:  # screw
            return np.concatenate((
                self.rotate(other[..., :3]),
                self.rotate(other[..., 3:])
            ))
        assert d == 3
        return other @ self.R.T

    def __mul__(self, scale):
        return Transform(
            p=self.p * scale,
            rotvec=self.rotvec * scale,
        )

    def lerp(self, other: 'Transform', s: float):
        self_t_other = self.inv @ other
        return self @ (self_t_other * s)

    def save(self, fp):
        np.savetxt(fp, self.xyz_rotvec)

    @classmethod
    def load(cls, fp):
        return cls.from_xyz_rotvec(np.loadtxt(fp))

    @classmethod
    def random(cls, random_state: np.random.RandomState = np.random):  # for testing
        return cls(p=random_state.randn(3), r=Rotation.random(random_state=random_state))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.xyz_rotvec)

    def equals(self, other, atol=1e-13):
        err = np.abs(self.matrix - other.matrix)
        return np.all(err < atol)
