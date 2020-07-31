import numpy as np

from .. import Transform, SceneNode, SceneState


def test_from_str():
    root, a, b, c, d, e = SceneNode.tree('root -> (a, b -> c, d), e')
    for node, parent in (root, None), (a, root), (b, root), (c, b), (d, root), (e, None):
        assert node.parent is parent


def test_t(atol=1e-13):
    state = SceneState()
    root = node = SceneNode()
    for _ in range(5):
        node = SceneNode(node)
        state[node] = Transform.random()

    child = node
    mat = np.eye(4)
    while node != root:
        mat = mat @ state[node].matrix
        node = node.parent
    assert np.abs(mat - child.t(root, state).matrix).max() < atol


def test_path_to_and_solve(atol=1e-13):
    root, base, a, c, b = SceneNode.tree('root -> base -> (a, c -> b)')
    assert a.path_to(root) == ([a, base, root], [root])
    assert a.path_to(b) == ([a, base], [base, c, b])
    assert c.path_to(b) == ([c], [c, b])

    state = SceneState()
    state[a, c, b] = [Transform.random() for _ in range(3)]

    desired_a_t_b = Transform.random()
    state[c] = c.solve(a, b, desired_a_t_b, state)
    err = np.abs(desired_a_t_b.matrix - a.t(b, state).matrix).max()
    assert err < atol, err
