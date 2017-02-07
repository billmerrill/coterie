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

    def __str__(self):
        return "<ConstellationPoint {:10} ra:{:8} dec:{:10} projection:{}>" \
            .format(self.key, self.ra, self.dec, self.projected)


class Constellation(object):
    def __init__(self, abbreviation, config):
        self.config = config
        self.abbreviation = abbreviation
        self.stars = {}

    def __str__(self):
        stars = []
        for s in sorted(self.stars):
            stars.append(str(self.stars[s]))
        return "<Constellation {} \n\t{}>".format(self.abbreviation, "\n\t".join(stars))

    def add_star(self, star):
        self.stars[star.key] = star

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
        magnitude < 3
        ORDER BY id ASC'''

        for row in conn.execute(sql, {'con': self.abbreviation}):
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


def plot_stars(cons):
    star_x = []
    star_y = []
    for s in sorted(cons.stars):
        print(cons.stars[s].key)
        projected = cons.stars[s].projected
        if projected:
            star_x.append(projected[0])
            star_y.append(projected[1])

    from bokeh.plotting import figure, output_file, show

    output_file("stars.html")
    # p = figure(plot_width=400, plot_height=400, title='orion')
    p = figure(title='orion')
    p.circle(star_x, star_y, size=10)
    show(p)

if __name__ == '__main__':
    abr = 'Ori'
    # abr = 'UMa'
    orion = Constellation(abr, CONFIG)
    orion.load_from_sqlite(CONFIG['star_db'])
    ra, dec = orion.find_center()
    orion.project()
    # orion.project_plate_carre()
    print(orion)
    plot_stars(orion)
