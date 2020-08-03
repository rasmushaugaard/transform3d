from typing import Union, Dict, Sequence

from .transform import Transform

T = Union[Transform, str]


class SceneState:
    def __init__(self, transforms=None):
        if transforms is None:
            transforms = dict()  # type: Dict[SceneNode, Transform]
        self.transforms = transforms

    def __getitem__(self, node: 'SceneNode'):
        return self.transforms[node]

    def __setitem__(self, node: Union['SceneNode', Sequence['SceneNode']],
                    transform: Union[T, Sequence[T]]):
        nodes = node if isinstance(node, Sequence) else [node]
        transforms = transform if isinstance(transform, Sequence) else [transform]
        transforms = [Transform.load(t) if isinstance(t, str) else t for t in transforms]
        if len(transforms) == 1:
            transforms *= len(nodes)
        assert len(transforms) == len(nodes)
        for n, t in zip(nodes, transforms):
            self.transforms[n] = t

    def copy(self):
        return SceneState(self.transforms.copy())


class SceneNode:
    def __init__(self, parent: 'SceneNode' = None, name='SceneNode'):
        self._parent = parent
        self.name = name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, SceneNode):
            raise TypeError()
        if parent.root() is self:
            raise RuntimeError('assignment would create cycle')
        self._parent = parent

    def adopt(self, *children: 'SceneNode'):
        for child in children:
            child.parent = self
        return self

    @classmethod
    def n(cls, n: int):
        return tuple((cls() for _ in range(n)))

    def path_to_root(self):
        nodes = [self]
        while nodes[-1].parent:
            nodes.append(nodes[-1].parent)
        return nodes

    def root(self):
        return self.path_to_root()[-1]

    def path_to(self, other: 'SceneNode'):
        root_to_self = self.path_to_root()[::-1]
        root_to_other = other.path_to_root()[::-1]
        idx = ([a is b for a, b in zip(root_to_self, root_to_other)] + [False]).index(False) - 1
        assert idx >= 0
        self_to_common_parent = root_to_self[idx:][::-1]
        common_parent_to_other = root_to_other[idx:]
        return self_to_common_parent, common_parent_to_other

    def common_parent(self, other):
        return self.path_to(other)[0][-1]

    def t(self, other: 'SceneNode', state: SceneState):
        """
        Returns self in other's frame, self_t_other
        """
        path_self_to_common, path_common_to_other = self.path_to(other)
        common_t_self = Transform()
        for node in reversed(path_self_to_common[:-1]):
            common_t_self = common_t_self @ state[node]
        common_t_other = Transform()
        for node in path_common_to_other[1:]:
            common_t_other = common_t_other @ state[node]
        return common_t_self.inv @ common_t_other

    def solve(self, a: 'SceneNode', b: 'SceneNode', a_t_b: Transform, state: SceneState):
        """
        Returns the transform that should be applied to self to achieve a_T_b.
        """
        path_a_to_common, path_common_to_b = a.path_to(b)
        if self in path_a_to_common[:-1]:
            b_t_a = a_t_b.inv
            return self.parent.t(b, state) @ b_t_a @ a.t(self, state)
        elif self in path_common_to_b[1:]:
            return self.parent.t(a, state) @ a_t_b @ b.t(self, state)
        else:
            ValueError('self.parent must be in the path from a to b')

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
