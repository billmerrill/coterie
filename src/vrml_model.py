import math
from string import Template
# from util import DotDict

import numpy as np

from indicies import *
from vrml_canvas import VRMLCanvas
import vrml_templates


class ModelConfig(object):

    def __init__(self):
        self.size_mm = [100, 100, 100]
        self.preserve_aspect_ratio = True
        self.min_thickness_mm = [3, 3, 3]
        self.connection_thickness = 10


class VRMLStar(object):

    def __init__(self, star, scalar=[1, 1, 1], radius=1):
        self.star = star
        self.scalar = scalar
        self.radius = radius
        self.overridden = [False, False, False]
        self.override = [0, 0, 0]

    def override_y(self, pos):
        self.overridden[PY] = True
        self.override[PY] = pos

    def get_vrml(self):
        x = self.star.projected[PX] * self.scalar[PX]
        if self.overridden[PY]:
            y = self.override[PY]
        else:
            y = self.star.distance * self.scalar[PY]
        z = self.star.projected[PY] * self.scalar[PZ]
        star_vrml = Template(vrml_templates.StarSphere).substitute(
            x=x, y=y, z=z, radius=self.radius)

        return star_vrml


class ConstellationStarfieldModel(object):

    def __init__(self, constellation, model_config):
        self.model_config = model_config
        self.output_filename = "stars.wrl"
        self.constellation = constellation

    def get_star_scalar(self):
        starfield_range = self.constellation.get_range()
        spans = [x[1] - x[0] for x in starfield_range]

        distance_scalar = self.model_config.size_mm[PY] / spans[PY]

        x_scalar = self.model_config.size_mm[PX] / spans[PX]
        z_scalar = self.model_config.size_mm[PZ] / spans[PZ]

        # lock aspect ratio
        if self.model_config.preserve_aspect_ratio:
            x_scalar = z_scalar = min(x_scalar, z_scalar)

        return [x_scalar, distance_scalar, z_scalar]

    def build_vrml(self):
        canvas = VRMLCanvas()
        star_scalar = self.get_star_scalar()
        for star in self.constellation.stars.values():
            canvas.add_element(VRMLStar(star, star_scalar))

        canvas.write_vrml(self.output_filename, show_axes=False,
                          header_values={'viewpoint_y': 2 * self.model_config.size_mm[PY]})


class VRMLStarPillar(VRMLStar):

    def __init__(self, star, scalar=[1, 1, 1], radius=1, backplane=1):
        super().__init__(star, scalar, radius)
        self.backplane = backplane

    def get_vrml(self):
        star_spot = self.star.get_xyz_ish()
        height = self.backplane - (star_spot[PY] * self.scalar[PY])
        radius = 1
        pillar_vrml = Template(vrml_templates.StarPillar).substitute(
            x=star_spot[PX] * self.scalar[PX],
            y=star_spot[PY] * self.scalar[PY] + height / 2.0,

            z=star_spot[PZ] * self.scalar[PX],
            radius=self.radius, height=height)
        return pillar_vrml


class VRMLConstellationConnection(object):

    def __init__(self, p1, p2, radius=1):
        '''
        p1, p2, the model coordinates of the endpints for the connection
        '''
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.radius = radius

    def _get_full_rot_quad(self, height):
        xr = (self.p2[PX] - self.p1[PX]) / height
        yr = 1 + (self.p2[PY] - self.p1[PY]) / height
        zr = (self.p2[PZ] - self.p1[PZ]) / height
        ar = 3.1415
        quad = "{} {} {} {}".format(xr, yr, zr, ar)
        return quad

    def get_vrml(self):
        midpoint = (self.p1 + self.p2) / 2
        height = np.linalg.norm(self.p1 - self.p2)
        rot_quad = self._get_full_rot_quad(height)
        connection_vrml = Template(vrml_templates.StarConnection).substitute(
            height=height, radius=self.radius, tx=midpoint[PX], ty=midpoint[PY], tz=midpoint[PZ], rot_quad=rot_quad)
        return connection_vrml
        # return connection_vrml


class ConstellationPillarModel(ConstellationStarfieldModel):

    def build_vrml(self):
        canvas = VRMLCanvas()
        star_scalar = self.get_star_scalar()
        # star_scalar = [20,20,20]
        field_range = self.constellation.get_range()
        depth = field_range[PY][1] * star_scalar[PY] - \
            (.5 * self.model_config.connection_thickness)
        print('depth', depth)

        x = 0
        for star in self.constellation.stars.values():
            canvas.add_element(VRMLStar(star, star_scalar, radius=1))
            canvas.add_element(
                VRMLStarPillar(star, star_scalar, radius=1, backplane=depth))
            x += 1

        canvas.write_vrml(self.output_filename, show_axes=True,
                          header_values={'viewpoint_y': 2 * self.model_config.size_mm[PY]})


class ConstellationStackedModel(ConstellationStarfieldModel):

    '''
    Definiting Y Axis Distance to Model MM

    Side View, Model Distance
    |-----------------------max Y size mm ------------------|
    |(  *  )                                (  *  )  (  *  )|
     top star                              low star    base
        |---------star field range mm----------|

    '''

    def get_star_scalar(self):
        starfield_range = self.constellation.get_range()
        spans = [x[1] - x[0] for x in starfield_range]

        # distance_scalar = self.model_config.size_mm[PY] / spans[PY]
        usable_Y = self.model_config.size_mm[PY] - (2 * self.model_config.star_radius) -\
            (2 * self.model_config.base_star_radius) - \
            self.model_config.base_star_sep

        distance_scalar = usable_Y / spans[PY]

        x_scalar = self.model_config.size_mm[PX] / spans[PX]
        z_scalar = self.model_config.size_mm[PZ] / spans[PZ]

        # lock aspect ratio
        if self.model_config.preserve_aspect_ratio:
            x_scalar = z_scalar = min(x_scalar, z_scalar)

        return np.array([x_scalar, distance_scalar, z_scalar])

    def build_vrml(self):
        self.model_config.size_mm = [100, 60, 100]
        self.model_config.base_star_radius = 3
        self.model_config.base_connection_radius = 3
        self.model_config.star_radius = 3
        self.model_config.star_connection_radius = 1
        self.model_config.pillar_radius = 1
        self.model_config.base_star_sep = 3

        canvas = VRMLCanvas()
        star_scalar = self.get_star_scalar()
        field_range = self.constellation.get_range()
        base_depth = self.model_config.size_mm[
            PY] - self.model_config.base_star_radius

        x = 0
        for star in self.constellation.stars.values():
            canvas.add_element(
                VRMLStar(star, star_scalar, radius=self.model_config.star_radius, ))
            base_star = VRMLStar(
                star, star_scalar, radius=self.model_config.base_star_radius)
            base_star.override_y(base_depth)
            canvas.add_element(base_star)
            canvas.add_element(
                VRMLStarPillar(star, star_scalar, radius=self.model_config.pillar_radius,
                backplane=base_depth))

        for connection in self.constellation.connections:
            s1, s2 = self.constellation.get_connection_stars(connection)
            sp1 = s1.get_xyz_ish() * star_scalar
            sp2 = s2.get_xyz_ish() * star_scalar
            canvas.add_element(VRMLConstellationConnection(
                sp1, sp2, self.model_config.star_connection_radius))

            p1, p2 = self.constellation.get_connection_positions(connection)

            p1 = [p1[0] * star_scalar[PX],
                  base_depth,
                  p1[1] * star_scalar[PZ]
                  ]
            p2 = [p2[0] * star_scalar[PX],
                  base_depth,
                  p2[1] * star_scalar[PZ]
                  ]
            canvas.add_element(VRMLConstellationConnection(
                p1, p2, self.model_config.base_connection_radius))

        canvas.write_vrml(self.output_filename, show_axes=False,
                          header_values={'viewpoint_y': 2 * self.model_config.size_mm[PY]})
