# transform3d

Handy classes for working with trees of 3d transformations.

Uses `scipy.spatial.transform.Rotation` for stable conversions between rotation representations.

#### install

```
$ pip3 install transform3d
```

#### convention
`a_t_b` denotes *b* relative to *a*, such that a point 
in frame *b*, `p_b`, is transformed to frame *a* by: `p_a = a_t_b @ p_b`
(Note that `@` is the matmul operator in python.)
This provides easy to read series of transformations: 
`a_t_d = a_t_b @ b_t_c @ c_t_d`.

#### usage
```python
import numpy as np
from transform3d import Transform, SceneNode, SceneState

# basic Transform usage
a_t_b = Transform(p=(1, 0, 0), rotvec=(0, 0, 0))
b_t_c = Transform(p=(0, 0, 1), rpy=(0, 0, np.pi / 2))
a_t_c = a_t_b @ b_t_c
c_t_a = a_t_c.inv

# transform a point from a's frame to c's frame
p_a = (1, 0, 0)
p_c = c_t_a @ p_a
# or multiple points
p_a = np.random.randn(2, 3)  # two points (x, y, z)
p_c = c_t_a @ p_a

# rotate vectors
v_a = (1, 0, 0)
v_c = c_t_a.rotate(v_a)
# or screws (6d, eg. force-torque)
s_a = (1, 0, 0, 1, 0, 0)
s_c = c_t_a.rotate(v_a)

# using SceneNode to build a tree
root = SceneNode()
a = SceneNode(parent=root)
b = SceneNode(parent=root)
c = SceneNode(parent=b)
# or:
root, a, b, c = SceneNode.n(4)
root.adopt(
    a,
    b.adopt(c)
)

# set node transforms in relation to parents
state = SceneState()
state[a] = Transform(p=(1, 0, 0), rpy=(np.pi, 0, 0))
state[b] = Transform(rotvec=(0, 90, 0), degrees=True)
state[c] = Transform(quat=(0, 0, 0, 1))

# calculate transforms between nodes
c_t_a = c.p(a, state)  # type: Transform

# solve for transforms
c_t_a_desired = Transform(p=(1, 2, 3), R=np.eye(3))
state[b] = b.solve(c, a, c_t_a_desired, state)
assert c.p(a, state).equals(c_t_a_desired)
```

