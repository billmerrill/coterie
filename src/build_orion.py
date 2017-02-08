from math import sin, cos, sqrt, radians, degrees
import sqlite3

CONFIG = {
    'star_db': "../data/sc_db/stars.db"
}


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

    def __str__(self):
        stars = []
        for s in sorted(self.stars):
            stars.append(str(self.stars[s]))
        return "<Constellation {} \n\t{}>".format(self.abbreviation, "\n\t".join(stars))

    def add_star(self, star):
        self.stars[star.index] = star

    def get_star(self, index):
        return self.stars[index]

    def load_from_sqlite(self, star_db_file):
        conn = sqlite3.connect(star_db_file)
        conn.row_factory = sqlite3.Row

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
        constellation = :con AND
        bayer_flamsteed_designation != "" AND
        magnitude < :mag
        ORDER BY id ASC'''

        for row in conn.execute(sql, {'con': self.abbreviation,
                                      'mag': self.magnitude_filter}):
            print(row['ra'], row['dec'])
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

        print("print center", raC, decC)
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


def plot_stars(cons, stars, connections):
    star_x = []
    star_y = []
    for s in sorted(cons.stars):
        print(cons.stars[s].key)
        projected = cons.stars[s].projected
        if projected:
            star_x.append(projected[0])
            star_y.append(projected[1])

    from bokeh.plotting import figure, output_file, show
    from bokeh.models import Label, WheelZoomTool, Segment


    output_file("stars.html")
    # p = figure(plot_width=400, plot_height=400, title='orion')
    p = figure(plot_width=800, plot_height=800,title='orion')
    p.toolbar.active_scroll = WheelZoomTool()
    for star in cons.stars.values():
        if star.hyg_id in stars:
            circle_color="#000000"
        else:
            circle_color="#cccccc"
        p.circle(star.projected[0], star.projected[1], name=star.key, size=10, color=circle_color)
        p.add_layout(Label(x=star.projected[0], y=star.projected[1], text="{}:{} {:.2f}".format(star.hyg_id, star.key, star.magnitude), text_color="#999999"))
    for connection in connections:
        a = cons.get_star(connection[0])
        b = cons.get_star(connection[1])
        glyph = Segment(x0=a.projected[0], y0=a.projected[1], x1=b.projected[0],
                        y1=b.projected[1], line_color="#aaeeaa", line_width=4)
        p.add_glyph(glyph)

    # p.circle(star_x, star_y, size=10)
    show(p, browser="safari", new="window")

if __name__ == '__main__':
    abr = 'Ori'
    # abr = 'UMa'
    orion = Constellation(abr, CONFIG, mag=5)
    orion.load_from_sqlite(CONFIG['star_db'])
    ra, dec = orion.find_center()
    orion.project()
    # orion.project_plate_carre()
    print(orion)
    orion_points = [27298, 24378, 27919, 25273, 26662, 26246, 25865, 26142, 26176,
                    22396, 22496, 22744, 23069, 22456, 22792, 22904, 23552, 28543,
                    29353, 28966, 28645, 27844]
    orion_lines = [(27298, 26662), (24378, 25865), (25865, 26246), (26246, 26662),
                    (26246, 26176), (26662, 27919), (27919, 26142), (26142,25273),
                    (25273, 27919),(25273, 22396), (22396, 22496), (22744, 22496),
                    (23069, 22744), (22396, 22456), (22456, 22792), (22792, 22904),
                    (22904, 23552), (27919, 28543), (28543, 29353), (28543, 28966),
                    (29353, 28966), (29353, 28645), (28966, 27844), (28645, 27844),
                    (25273, 25865)]
    plot_stars(orion, orion_points, orion_lines)
