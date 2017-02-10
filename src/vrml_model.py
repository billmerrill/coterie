from string import Template
# from util import DotDict

from indicies import *
from vrml_canvas import VRMLCanvas
import vrml_templates


class ModelConfig(object):

    def __init__(self):
        self.size_mm = [100, 100, 100]
        self.preserve_aspect_ratio = True
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
        starfield_range = self.constellation.get_range()
        spans = [x[1]-x[0] for x in starfield_range]

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
                          header_values={'viewpoint_y': 2*self.model_config.size_mm[PY]})
