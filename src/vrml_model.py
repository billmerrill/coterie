from string import Template
# from util import DotDict


from vrml_canvas import VRMLCanvas
import vrml_templates


class VRMLStar(object):

    def __init__(self, star):
        self.star = star

    def get_vrml(self):
        star_vrml = Template(vrml_templates.StarSphere).substitute(
            x=self.star.projected[0] * 20,
            y=1,
            z=self.star.projected[1] * 20,
            radius=.2)

        return star_vrml


class Constellation3DModel(object):

    def __init__(self, constellation, config):
        self.output_filename = "stars.wrl"
        self.constellation = constellation

    def build_vrml(self):
        canvas = VRMLCanvas()
        for star in self.constellation.stars.values():
            canvas.add_element(VRMLStar(star))

        canvas.write_vrml(self.output_filename, show_axes=False)
