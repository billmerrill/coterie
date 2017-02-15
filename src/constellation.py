
from math import sin, cos, sqrt, radians, degrees
import sqlite3

import numpy as np

from indicies import *

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

    def get_xyz_ish(self):
        '''
        For Constellation Models:
        x = projected x
        y = distance from earth in parsecs
        z = projected y
        Using distance as Y like ElevationGrid uses Y
        '''
        if not self.projected:
            return False

        return np.array([self.projected[PX], self.distance, self.projected[PY]])

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

    def get_range(self):
        positions = np.array([x.get_xyz_ish() for x in self.stars.values()])
        return [(np.min(positions[:, PX]), np.max(positions[:, PX])),
                (np.min(positions[:, PY]), np.max(positions[:, PY])),
                (np.min(positions[:, PZ]), np.max(positions[:, PZ]))]

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

    def get_connection_positions(self, connection):
        return self.stars[connection[0]].projected, self.stars[connection[1]].projected

    def get_connection_stars(self, connection):
        return self.stars[connection[0]], self.stars[connection[1]]

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
        '''
        find the middle ra and ec for the starfield_range
        return mid_ra, mid_dec
        '''

        angles = np.array([[x.ra, x.dec] for x in self.stars.values()])
        stats = np.ndarray(shape=(2, 2))
        stats[0] = np.amin(angles, 0)
        stats[1] = np.amax(angles, 0)
        mids = np.average(stats, axis=0)
        return mids[0], mids[1]

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
