from string import Template
# from util import DotDict

from indicies import *
from vrml_canvas import VRMLCanvas
import vrml_templates


class ModelConfig(object):

    def __init__(self):
        self.size_mm = [100, 100, 100]
        self.min_thickness_mm = [3, 3, 3]


class VRMLStar(object):

    def __init__(self, star, scalar=[1, 1, 1], radius=1):
        self.star = star
        self.scalar = scalar
        self.radius = radius

    def get_vrml(self):
        x = self.star.projected[PX] * self.scalar[PX]
        y = self.star.distance * self.scalar[PY]
        z = self.star.projected[PY] * self.scalar[PZ]
        star_vrml = Template(vrml_templates.StarSphere).substitute(
            x=x, y=y, z=z, radius=self.radius)

        return star_vrml


class Constellation3DModel(object):

    def __init__(self, constellation, model_config):
        self.model_config = model_config
        self.output_filename = "stars.wrl"
        self.constellation = constellation

    def get_star_scalar(self):
        # base is x and z



        star_span = self.constellation.max_distance - \
            self.constellation.min_distance
        distance_scalar = self.model_config.size_mm[PY] / star_span
        x_scalar = 20.0
        z_scalar = 20.0
        return [x_scalar, distance_scalar, z_scalar]

    def build_vrml(self):
        canvas = VRMLCanvas()
        star_scalar = self.get_star_scalar()
        for star in self.constellation.stars.values():
            canvas.add_element(VRMLStar(star, star_scalar))

        canvas.write_vrml(self.output_filename, show_axes=False)
