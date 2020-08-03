import numpy as np

from .. import Transform, SceneNode, SceneState


def test_scene_node_structure():
    a, b, c, d, e = SceneNode.n(5)
    a.adopt(
        b,
        c.adopt(d, e)
    )
    assert b.parent is a and c.parent is a and d.parent is c and e.parent is c


def test_t():
    state = SceneState()
    root = node = SceneNode()
    for _ in range(5):
        node = SceneNode(node)
        state[node] = Transform.random()

    child = node
    node_m_child = np.eye(4)
    while node != root:
        node_m_child = state[node].matrix @ node_m_child
        node = node.parent
    assert Transform(node_m_child).equals(root.t(child, state))


def test_path_to_and_solve():
    root, base, a, c, b = SceneNode.n(5)
    root.adopt(
        base.adopt(
            a,
            c.adopt(b)
        )
    )
    assert a.path_to(root) == ([a, base, root], [root])
    assert a.path_to(b) == ([a, base], [base, c, b])
    assert c.path_to(b) == ([c], [c, b])

    state = SceneState()
    state[a, c, b] = [Transform.random() for _ in range(3)]

    desired_a_t_b = Transform.random()
    state[c] = c.solve(a, b, desired_a_t_b, state)
    assert a.t(b, state).equals(desired_a_t_b)
