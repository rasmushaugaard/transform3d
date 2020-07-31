# transform3d

Handy classes to express transformations 
and build tree structures of frames.
  
Uses `scipy.spatial.transform.Rotation` for stable conversions between rotation representations.

#### install

```
$ pip install transform3d
```

#### convention
`a_t_b` denotes *b* relative to *a*, such that a point 
in frame *b*, `p_b`, is transformed to frame *a* by `p_a = a_t_b @ p_b`. 
This provides easy to read series of transformations: 
`a_t_d = a_t_b @ b_t_c @ c_t_d`.
Note that `@` is the matmul operator in python.

#### usage
```python
import numpy as np
from transform3d import Transform, SceneNode, SceneState

# basic Transform usage
a_t_b = Transform(t=(1, 0, 0), rotvec=(0, 0, 0))
b_t_c = Transform(t=(0, 0, 1), rpy=(0, 0, np.pi / 2))
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
root, a, b, c = SceneNode.tree('root -> (a, b -> c)')
# set node transforms in relation to parents
state = SceneState()
state[a] = Transform(t=(1, 0, 0), rpy=(np.pi, 0, 0))
state[b] = Transform(rotvec=(0, 90, 0), degrees=True)
state[c] = Transform(quat=np.random.randn(4))

# calculate transforms between nodes
c_t_a = c.t(a, state)  # type: Transform

# solve for transforms
c_t_a_desired = Transform(t=(1, 2, 3), R=np.eye(3))
root_t_b = b.solve(c, a, c_t_a_desired, state)
state[b] = root_t_b
assert c.t(a, state).equals(c_t_a_desired)
```
