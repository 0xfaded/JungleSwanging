#!/usr/bin/python
#
# C++ version Copyright (c) 2006-2007 Erin Catto http://www.gphysics.com
# Python version Copyright (c) 2008 kne / sirkne at gmail dot com
# 
# Implemented using the pybox2d SWIG interface for Box2D (pybox2d.googlecode.com)
# 
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.



# This code has been modified for the purposes of Monkey Swanging Debug Drawing


import OpenGL.GL as gl
import pyglet
from pyglet import gl
import Box2D as box2d

import math


class grBlended (pyglet.graphics.Group):
    """
    This pyglet rendering group enables blending.
    """
    def set_state(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    def unset_state(self):
        gl.glDisable(gl.GL_BLEND)

class glDebugDraw(box2d.b2DebugDraw):
    """
    This debug draw class accepts callbacks from Box2D (which specifies what to draw)
    and handles all of the rendering.

    If you are writing your own game, you likely will not want to use debug drawing.
    Debug drawing, as its name implies, is for debugging.
    """
    blended = grBlended()
    circle_segments = 16
    circle_cache_tf = {} # triangle fan (inside)
    circle_cache_ll = {} # line loop (border)
    def __init__(self): super(glDebugDraw, self).__init__()

    def init_draw(self):
      self.batch = pyglet.graphics.Batch()

    def draw(self):
      self.batch.draw()

    def triangle_fan(self, vertices):
        """
        in: vertices arranged for gl_triangle_fan ((x,y),(x,y)...)
        out: vertices arranged for gl_triangles (x,y,x,y,x,y...)
        """
        out = []
        for i in range(1, len(vertices)-1):
            # 0,1,2   0,2,3  0,3,4 ..
            out.extend( vertices[0  ] )
            out.extend( vertices[i  ] )
            out.extend( vertices[i+1] )
        return len(out) / 2, out

    def line_loop(self, vertices):
        """
        in: vertices arranged for gl_line_loop ((x,y),(x,y)...)
        out: vertices arranged for gl_lines (x,y,x,y,x,y...)
        """
        out = []
        for i in range(0, len(vertices)-1):
            # 0,1  1,2  2,3 ... len-1,len  len,0
            out.extend( vertices[i  ] )
            out.extend( vertices[i+1] )
        
        out.extend( vertices[len(vertices)-1] )
        out.extend( vertices[0] )

        return len(out)/2, out

    def _getLLCircleVertices(self, radius, points):
        """
        Get the line loop-style vertices for a given circle.
        Drawn as lines.

        "Line Loop" is used as that's how the C++ code draws the
        vertices, with lines going around the circumference of the
        circle (GL_LINE_LOOP).

        This returns 'points' amount of lines approximating the 
        border of a circle.

        (x1, y1, x2, y2, x3, y3, ...)
        """
        ret = []
        step = 2*math.pi/points
        n = 0
        for i in range(0, points):
            ret.append( (math.cos(n) * radius, math.sin(n) * radius ) )
            n += step
            ret.append( (math.cos(n) * radius, math.sin(n) * radius ) )
        return ret

    def _getTFCircleVertices(self, radius, points):
        """
        Get the triangle fan-style vertices for a given circle.
        Drawn as triangles.

        "Triangle Fan" is used as that's how the C++ code draws the
        vertices, with triangles originating at the center of the
        circle, extending around to approximate a filled circle
        (GL_TRIANGLE_FAN).

        This returns 'points' amount of lines approximating the 
        circle.

        (a1, b1, c1, a2, b2, c2, ...)
        """
        ret = []
        step = 2*math.pi/points
        n = 0
        for i in range(0, points):
            ret.append( (0.0, 0.0) )
            ret.append( (math.cos(n) * radius, math.sin(n) * radius ) )
            n += step
            ret.append( (math.cos(n) * radius, math.sin(n) * radius ) )
        return ret

    def getCircleVertices(self, center, radius, points):
        """
        Returns the triangles that approximate the circle and
        the lines that border the circles edges, given
        (center, radius, points).

        Caches the calculated LL/TF vertices, but recalculates
        based on the center passed in.

        TODO: As of this point, there's only one point amount,
        so the circle cache ignores it when storing. Could cause 
        some confusion if you're using multiple point counts as
        only the first stored point-count for that radius will
        show up.

        Returns: (tf_vertices, ll_vertices)
        """
        if radius not in self.circle_cache_tf.keys():
            self.circle_cache_tf[radius]=self._getTFCircleVertices(radius,points)
            self.circle_cache_ll[radius]=self._getLLCircleVertices(radius,points)

        ret_tf, ret_ll = [], []

        for x, y in self.circle_cache_tf[radius]:
            ret_tf.extend( (x+center.x, y+center.y) )
        for x, y in self.circle_cache_ll[radius]:
            ret_ll.extend( (x+center.x, y+center.y) )
        return ret_tf, ret_ll

    def DrawCircle(self, center, radius, color):
        """
        Draw an unfilled circle given center, radius and color.
        """
        unused, ll_vertices = self.getCircleVertices( center, radius, self.circle_segments)
        ll_count = len(ll_vertices)/2

        self.batch.add(ll_count, gl.GL_LINES, None,
            ('v2f', ll_vertices),
            ('c4f', [color.r, color.g, color.b, 1.0] * (ll_count)))

    def DrawSolidCircle(self, center, radius, axis, color):
        """
        Draw an filled circle given center, radius, axis (of orientation) and color.
        """
        tf_vertices, ll_vertices = self.getCircleVertices( center, radius, self.circle_segments)
        tf_count, ll_count = len(tf_vertices) / 2, len(ll_vertices) / 2


        self.batch.add(tf_count, gl.GL_TRIANGLES, self.blended,
            ('v2f', tf_vertices),
            ('c4f', [0.5 * color.r, 0.5 * color.g, 0.5 * color.b, 0.5] * (tf_count)))

        self.batch.add(ll_count, gl.GL_LINES, None,
            ('v2f', ll_vertices),
            ('c4f', [color.r, color.g, color.b, 1.0] * (ll_count)))

        p = center + radius * axis
        self.batch.add(2, gl.GL_LINES, None,
            ('v2f', (center.x, center.y, p.x, p.y)),
            ('c3f', [1.0, 0.0, 0.0] * 2))

    def DrawPolygon(self, vertices, vertexCount, color):
        """
        Draw a wireframe polygon given the world vertices (tuples) with the specified color.
        """
        ll_count, ll_vertices = self.line_loop(vertices)

        self.batch.add(ll_count, gl.GL_LINES, None,
            ('v2f', ll_vertices),
            ('c4f', [color.r, color.g, color.b, 1.0] * (ll_count)))

    def DrawSolidPolygon(self, vertices, vertexCount, color):
        """
        Draw a wireframe polygon given the world vertices (tuples) with the specified color.
        """
        tf_count, tf_vertices = self.triangle_fan(vertices)

        self.batch.add(tf_count, gl.GL_TRIANGLES, self.blended,
            ('v2f', tf_vertices),
            ('c4f', [0.5 * color.r, 0.5 * color.g, 0.5 * color.b, 0.5] * (tf_count)))

        ll_count, ll_vertices = self.line_loop(vertices)

        self.batch.add(ll_count, gl.GL_LINES, None,
            ('v2f', ll_vertices),
            ('c4f', [color.r, color.g, color.b, 1.0] * (ll_count)))

    def DrawSegment(self, p1, p2, color):
        """
        Draw the line segment from p1-p2 with the specified color.
        """
        self.batch.add(2, gl.GL_LINES, None,
            ('v2f', (p1.x, p1.y, p2.x, p2.y)),
            ('c3f', [color.r, color.g, color.b]*2))

    def DrawXForm(self, xf):
        """
        Draw the transform xf on the screen
        """
        p1 = xf.position
        k_axisScale = 0.4
        p2 = p1 + k_axisScale * xf.R.col1
        p3 = p1 + k_axisScale * xf.R.col2

        self.batch.add(4, gl.GL_LINES, None,
            ('v2f', (p1.x, p1.y, p2.x, p2.y, p1.x, p1.y, p3.x, p3.y)),
            ('c3f', [1.0, 0.0, 0.0] * 2 + [0.0, 1.0, 0.0] * 2))

    def DrawPoint(self, p, size, color):
        """
        Draw a single point at point p given a point size and color.
        """
        self.batch.add(1, gl.GL_POINTS, grPointSize(size),
            ('v2f', (p.x, p.y)),
            ('c3f', [color.r, color.g, color.b]))
        
    def DrawAABB(self, aabb, color):
        """
        Draw a wireframe around the AABB with the given color.
        """
        self.debugDraw.batch.add(8, gl.GL_LINES, None,
            ('v2f', (aabb.lowerBound.x, aabb.lowerBound.y, abb.upperBound.x, aabb.lowerBound.y, 
                abb.upperBound.x, aabb.lowerBound.y, aabb.upperBound.x, aabb.upperBound.y,
                aabb.upperBound.x, aabb.upperBound.y, aabb.lowerBound.x, aabb.upperBound.y,
                aabb.lowerBound.x, aabb.upperBound.y, aabb.lowerBound.x, aabb.lowerBound.y)),
            ('c3f', [color.r, color.g, color.b] * 8))

