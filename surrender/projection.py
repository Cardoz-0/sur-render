import numpy as np
from copy import deepcopy
from numbers import Number
from surrender.vector import *
from surrender.math_transforms import *


def _alignment_matrix(uv, nv):
    rx = nv.x_angle()
    nv.rotate_x(rx)
    uv.rotate_x(rx)

    ry = nv.y_angle() - np.pi / 2
    nv.rotate_y(ry)
    uv.rotate_y(ry)

    rz = uv.z_angle()

    mx = rotation_matrix_x(rx)
    my = rotation_matrix_y(ry)
    mz = rotation_matrix_z(rz)

    return mx @ my @ mz

def viewport_transform(vector, source, target):
    x = vector.x - source.min().x
    x /= source.max().x - source.min().x
    x *= target.max().x - target.min().x

    y = vector.y - source.min().y
    y /= source.max().y - source.min().y
    y = 1 - y
    y *= target.max().y - target.min().y

    vector.x = x
    vector.y = y
    return vector

def parallel_projection(shapes, window):
    wc = window.center()
    alignment_matrix = _alignment_matrix(window.up_vector(), window.normal_vector())

    for shape in shapes:
        shape = deepcopy(shape)
        shape.move(-wc)
        shape.apply_transform(alignment_matrix)
        yield shape

def perspective_projection(shapes, window):
    cop = window.center_of_projection()
    d = window.projection_distance
    alignment_matrix = _alignment_matrix(window.up_vector(), window.normal_vector())

    for shape in shapes:
        shape = deepcopy(shape)
        shape.move(-cop)
        shape.apply_transform(alignment_matrix)

        for p in shape.points():
            x = (d * p.x) / p.z
            y = (d * p.y) / p.z

            p.x = x 
            p.y = y
            p.z = 0 

        yield shape
