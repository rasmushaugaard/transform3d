import re
from typing import Union, Dict, List, Sequence

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

    def T(self, a: 'SceneNode', b: 'SceneNode'):
        return a.t(b, self)

    def copy(self):
        return SceneState(self.transforms.copy())


class SceneNode:
    def __init__(self, parent: 'SceneNode' = None, name='SceneNode'):
        self.parent = parent
        self.name = name

    @classmethod
    def tree(cls, s: str):
        """
        Example:
            root, a, b, c = SceneNode.from_str('root -> (a, b -> c)')
        """
        s = re.sub(r'\s', '', s) + ','
        nodes = []
        last_b = 0
        stack = [None]
        p_stack = [None]
        for match in re.finditer(r'(->|[,()])', s):
            a, b = match.span()
            m = s[a:b]
            if m in ('->', ',', ')') and a - last_b:
                name = s[last_b:a]
                assert name
                nodes.append(cls(parent=stack[-1], name=name))
            if m == '->':
                stack.append(nodes[-1])
            if m == '(':
                p_stack.append(stack[-1])
            if m == ')':
                p_stack.pop()
                m = ','
            if m == ',':
                while stack[-1] != p_stack[-1]:
                    stack.pop()
            last_b = b
        return tuple(nodes)

    def path_to_root(self):
        nodes = [self]
        while nodes[-1].parent:
            nodes.append(nodes[-1].parent)
        return nodes

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
        Returns other in self's frame
        """
        self_to_common, common_to_other = self.path_to(other)
        t = Transform()
        for node in self_to_common[:-1]:
            t = t @ state[node]
        for node in common_to_other[1:]:
            t = t @ state[node].inv
        return t

    def solve(self, a: 'SceneNode', b: 'SceneNode', a_t_b: Transform, state: SceneState):
        """
        Returns the transform that should be applied to self to achieve a_T_b.
        """
        a_to_common, common_to_b = a.path_to(b)
        b_t_a = a_t_b.inv
        if self in a_to_common[:-1]:
            return self.t(a, state) @ a_t_b @ b.t(self.parent, state)
        elif self in common_to_b[1:]:
            return self.t(b, state) @ b_t_a @ a.t(self.parent, state)
        else:
            ValueError('self.parent must be in the path from a to b')

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
