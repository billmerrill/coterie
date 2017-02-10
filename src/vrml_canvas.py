from string import Template


import vrml_templates
import tempfile


class VRMLCanvas(object):

    def __init__(self):
        self.elements = []

    def add_element(self, new_element):
        self.elements.append(new_element)

    def write_vrml(self, outfile, show_axes=False, header_values={}):
        print ("Writing %s elements" % len(self.elements))
        with open(outfile, 'w') as dest_file:
            dest_file.write(Template(vrml_templates.Header).substitute(
                             viewpoint_y=header_values['viewpoint_y']))
            for e in self.elements:
                dest_file.write(e.get_vrml())
            if show_axes:
                print("writing axes")
                dest_file.write(vrml_templates.DisplayAxes)
