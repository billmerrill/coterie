from math import sin, cos, sqrt, radians, degrees
import sqlite3
import subprocess

from vrml_model import Constellation3DModel

CONFIG = {
    'star_db': "../data/sc_db/stars.db"
}

class ConstellationModel(object):

    def __init__(self, constellation=None, featured_stars=None):
        self.constellation = constellation
        self.featured_stars = featured_stars

    def chart2D(self):
        # cons, stars, connections):
        star_x = []
        star_y = []
        for s in sorted(self.constellation.stars):
            projected = self.constellation.stars[s].projected
            if projected:
                star_x.append(projected[0])
                star_y.append(projected[1])

        from bokeh.plotting import figure, output_file, show
        from bokeh.models import Label, WheelZoomTool, Segment

        output_file("stars.html")
        p = figure(plot_width=800, plot_height=800, title='orion')
        p.toolbar.active_scroll = WheelZoomTool()
        for star in self.constellation.stars.values():
            if self.featured_stars and star.hyg_id in self.featured_stars:
                circle_color = "#000000"
            else:
                circle_color = "#cccccc"
            p.circle(star.projected[0], star.projected[1],
                     name=star.key, size=10, color=circle_color)
            p.add_layout(Label(x=star.projected[0], y=star.projected[1],
                               text="{}:{} {:.2f}".format(star.hyg_id, star.key,
                               star.magnitude), text_color="#999999"))
        for connection in self.constellation.connections:
            a = self.constellation.get_star(connection[0])
            b = self.constellation.get_star(connection[1])
            glyph = Segment(x0=a.projected[0], y0=a.projected[1], x1=b.projected[0],
                            y1=b.projected[1], line_color="#aaeeaa", line_width=4)
            p.add_glyph(glyph)

        show(p, browser="safari", new="window")


class ConstellationPoint(object):

    def __init__(self, hyg_id, designation, proper_name, ra, dec,
                 distance, magnitude):
        self.hyg_id = hyg_id
        self.designation = designation or ""
        self.proper_name = proper_name or ""
        self.ra = ra
        self.dec = dec
        self.distance = distance or ""
        self.magnitude = magnitude or ""
        self.projected = None

    @property
    def key(self):
        if self.proper_name:
            return self.proper_name
        if self.designation:
            return self.designation
        return self.hyg_id

    @property
    def index(self):
        return self.hyg_id

    def __str__(self):
        return "<ConstellationPoint {:10} ra:{:8} dec:{:10} projection:{}>" \
            .format(self.key, self.ra, self.dec, self.projected)


class Constellation(object):

    def __init__(self, abbreviation, config, mag=4):
        self.config = config
        self.abbreviation = abbreviation
        self.stars = {}
        self.magnitude_filter = mag
        self.connections = []

    def __str__(self):
        stars = []
        for s in sorted(self.stars):
            stars.append(str(self.stars[s]))
        return "<Constellation {} \n\t{}>".format(self.abbreviation, "\n\t".join(stars))

    def add_star(self, star):
        self.stars[star.index] = star

    def get_star(self, index):
        return self.stars[index]

    def generate_select_in_parts(self, selection_ids):
        sql_keys = []
        sql_data = {}
        for i, s in enumerate(selection_ids):
            key = 'i{}'.format(i)
            sql_keys.append(':{}'.format(key))
            sql_data[key] = s

        sql_str = "id in ({})".format(",".join(sql_keys))

        return sql_str, sql_data

    def selection_sql(self, selection=None):
        sql_str = None
        sql_data = None
        if selection:
            sql_str, sql_data = self.generate_select_in_parts(selection)
        else:
            sql_str = '''
            constellation = :con AND
            bayer_flamsteed_designation != "" AND
            magnitude < :mag'''
            sql_data = {'con': self.abbreviation,
                        'mag': self.magnitude_filter}

        return sql_str, sql_data

    def set_connections(self, connections):
        '''
        Accept a list of tuples defining lines between
        stars in a representation of the constellation
        '''
        self.connections = connections

    def load_stars_from_sqlite(self, star_db_file, selection=None):
        '''
        load star data via one of two modes:
        * Constellation
        Use the abbreviate and magnitfude to filter stars from the
        constellation area.
        * Selection
        Load star data based on the 'selection' list containing
        ids of stars selected for a models.
        '''
        conn = sqlite3.connect(star_db_file)
        conn.row_factory = sqlite3.Row

        # we are either grabbing all the stars of a certain character
        # or just the stars in a list

        selection_sql, selection_data = self.selection_sql(selection)

        sql = '''
        SELECT
        id,
        magnitude,
        proper_name,
        bayer_flamsteed_designation as designation,
        ra,
        dec,
        distance
        FROM stars WHERE
        {selection_sql}
        ORDER BY id ASC'''

        sql = sql.format(selection_sql=selection_sql)

        for row in conn.execute(sql, selection_data):
            self.add_star(ConstellationPoint(row['id'], row['designation'],
                                             row['proper_name'], row['ra'],
                                             row['dec'], row['distance'],
                                             row['magnitude']))

    def find_center(self):
        min_ra = 500
        max_ra = -500
        min_dec = 100
        max_dec = -100
        for star in self.stars.values():
            if star.ra < min_ra:
                min_ra = star.ra
            if star.ra > max_ra:
                max_ra = star.ra
            if star.dec < min_dec:
                min_dec = star.dec
            if star.dec > max_dec:
                max_dec = star.dec

        mid_ra = (max_ra - min_ra) / 2
        mid_dec = (max_dec - min_dec) / 2

        # return max_ra + mid_ra, max_dec + mid_dec
        return min_ra + mid_ra, min_dec + mid_dec

    def project(self):
        '''
        http://www.projectpluto.com/project.htm

        step 1 orthographic projection
        delta_ra = ra - ra0;          /* determine difference in RA */

        /* wlm added a -1 in code for looking out rather than down */
        x1 = cos( dec) * sin( delta_ra);
        y1 = sin( dec) * cos( dec0) - cos( dec) * cos( delta_ra) * sin( dec0);
        '''
        raC, decC = self.find_center()
        raC = radians(raC * 15)
        decC = radians(decC)

        for star in self.stars.values():
            ra = radians(star.ra * 15)
            dec = radians(star.dec)
            delta_ra = ra - raC
            x1 = -1 * cos(dec) * sin(delta_ra)
            y1 = sin(dec) * cos(decC) - cos(dec) * cos(delta_ra) * sin(decC)
            z1 = sin(dec) * sin(decC) + cos(dec) * cos(decC) * cos(delta_ra)
            if (z1 < -.9):
                d = 20. * sqrt((1. - .81) / (1.00001 - z1 * z1))
            else:
                d = 2. / (z1 + 1.)
            x = x1 * d
            y = y1 * d
            star.projected = (x, y)

    def project_plate_carre(self):
        raC, decC = self.find_center()
        # raC, dec0 = 0,0
        for s in sorted(self.stars):
            ra = self.stars[s].ra
            dec = self.stars[s].dec
            delta_ra = ra - raC
            x = delta_ra / sin(decC)
            y = dec - decC
            self.stars[s].projected = (x, y)

def chart_pictogram(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'], selection=orion_points)
    orion.set_connections(orion_lines)
    orion.project()
    orion_model = ConstellationModel(constellation=orion, featured_stars=orion_points)
    orion_model.chart2D()

def chart_with_starfield(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'])
    orion.set_connections(orion_lines)
    orion.project()
    orion_model = ConstellationModel(constellation=orion, featured_stars=orion_points)
    orion_model.chart2D()

def build_vrml_model(abr, orion_points, orion_lines):
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_stars_from_sqlite(CONFIG['star_db'], selection=orion_points)
    orion.set_connections(orion_lines)
    orion.project()
    orion_3d_model = Constellation3DModel(orion, CONFIG)
    orion_3d_model.build_vrml()
    subprocess.call( ["/usr/bin/open", "stars.wrl"] )


if __name__ == '__main__':

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
