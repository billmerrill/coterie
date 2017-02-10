
import subprocess

from constellation import Constellation
from constellation_chart import ConstellationChart
from vrml_model import Constellation3DModel, ModelConfig

CONFIG = {
    'star_db': "../data/sc_db/stars.db"
}


def chart_pictogram(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'], selection=orion_points)
    orion.set_connections(orion_lines)
    orion.project()
    orion_model = ConstellationChart(constellation=orion, featured_stars=orion_points)
    orion_model.chart2D()


def chart_with_starfield(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'])
    orion.set_connections(orion_lines)
    orion.project()
    orion_model = ConstellationChart(constellation=orion, featured_stars=orion_points)
    orion_model.chart2D()


def build_vrml_model(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'], selection=orion_points)
    orion.set_connections(orion_lines)
    orion.project()
    orion_3d_model = Constellation3DModel(orion, ModelConfig())
    orion_3d_model.build_vrml()
    subprocess.call(["/usr/bin/open", "stars.wrl"])


def build_orion():
    abr = 'Ori'
    orion_points = [27298, 24378, 27919, 25273, 26662, 26246, 25865, 26142, 26176,
                    22396, 22496, 22744, 23069, 22456, 22792, 22904, 23552, 28543,
                    29353, 28966, 28645, 27844]
    orion_lines = [(27298, 26662), (24378, 25865), (25865, 26246), (26246, 26662),
                   (26246, 26176), (26662, 27919), (27919, 26142), (26142, 25273),
                   (25273, 27919), (25273, 22396), (22396, 22496), (22744, 22496),
                   (23069, 22744), (22396, 22456), (22456, 22792), (22792, 22904),
                   (22904, 23552), (27919, 28543), (28543, 29353), (28543, 28966),
                   (29353, 28966), (29353, 28645), (28966, 27844), (28645, 27844),
                   (25273, 25865)]

    displays = {
        'starfield': chart_with_starfield,
        'pictograph': chart_pictogram,
        'vrml': build_vrml_model
    }

    build = 'vrml'
    displays[build](abr, orion_points, orion_lines)


if __name__ == '__main__':
    build_orion()
