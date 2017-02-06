import sqlite3

CONFIG = {
    'star_db': "../data/sc_db/stars.db"
}


class ConstellationPoint(object):

    def __init__(self, hyg_id, designation, proper_name, ra, dec, distance, magnitude):
        self.hyg_id = hyg_id
        self.designation = designation or ""
        self.proper_name = proper_name or ""
        self.ra = ra
        self.dec = dec
        self.distance = distance or ""
        self.magnitude = magnitude or ""

    def get_key(self):
        if self.proper_name:
            return self.proper_name
        if self.designation:
            return self.designation
        return self.hyg_id


class Constellation(object):
    def __init__(self, abbreviation, config):
        self.config = config
        self.abbreviation = abbreviation
        self.stars = {}

    def add_star(self, star):
        self.stars[star.get_key()] = star

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
        magnitude < 10'''

        for row in conn.execute(sql, {'con': self.abbreviation}):
            self.add_star(ConstellationPoint(row['id'], row['designation'],
                row['proper_name'], row['ra'], row['dec'], row['distance'],
                row['magnitude']))

    def find_center(self):
        min_ra = 500
        max_ra = -500
        min_dec = 100
        max_dec = -100
        for star in self.stars.values():
            print(star.ra, star.dec)
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

        return min_ra + mid_ra, min_dec + mid_dec


if __name__ == '__main__':
    abr = 'Ori'
    orion = Constellation(abr, CONFIG)
    orion.load_from_sqlite(CONFIG['star_db'])
    ra, dec = orion.find_center()
    print('mid')
    print(ra, dec)
