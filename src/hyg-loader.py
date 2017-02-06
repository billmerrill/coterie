import csv
import sqlite3

CONFIG = {
    'src_csv': "../data/HYG-Database/hygdata_v3.csv",
    'sqlite_db': "../data/sc_db/stars.db"
}

# load a selection of the HYG database into sqlite.
# csv columns:
#climb:src bill$ head ../data/HYG-Database/hygdata_v3.csv
#id,hip,hd,hr,gl,bf,proper,ra,dec,dist,pmra,pmdec,rv,mag,absmag,spect,
#ci,x,y,z,vx,vy,vz,rarad,decrad,pmrarad,pmdecrad,bayer,flam,con,
#comp,comp_primary,base,lum,var,var_min,var_max



def load_stars(config):

    star_table_sql = '''
        CREATE TABLE stars (
        id INT,
        hipparcos_id INT,
        henry_draper_id INT,
        harvard_revised_id INT,
        gliese_id INT,
        bayer_flamsteed_designation TEXT,
        proper_name TEXT,
        ra REAL,
        dec REAL,
        distance REAL,
        magnitude REAL,
        x REAL,
        y REAL,
        z REAL,
        constellation TEXT,
        companion_star_id INT,
        primary_star_id INT,
        multi_star_id TEXT,
        variable_star_designation TEXT)'''

    table_info = [('id', 'id'),
                  ('hip', 'hipparcos_id'),
                  ('hd', 'henry_draper_id'),
                  ('hr', 'harvard_revised_id'),
                  ('gl', 'gliese_id'),
                  ('bf', 'bayer_flamsteed_desig'),
                  ('proper', 'proper_name'),
                  ('ra', 'ra'),
                  ('dec', 'dec'),
                  ('dist', 'distance'),
                  ('mag', 'magnitude'),
                  ('x', 'x'),
                  ('y', 'y'),
                  ('z', 'z'),
                  ('con', 'constellation'),
                  ('comp', 'companion_star_id'),
                  ('comp_primary', 'primary_star_id'),
                  ('base', 'multi_star_id'),
                  ('var', 'variable_star_designation')]

    star_conn = sqlite3.connect(config['sqlite_db'])
    cur = star_conn.cursor()
    try:
        cur.execute('DROP TABLE stars')
    except sqlite3.OperationalError:
        print("No TABLE to DROP, continuing")
        pass

    cur.execute(star_table_sql)

    qs = ','.join(['?']*len(table_info))
    insert_sql = "INSERT INTO stars VALUES ({})".format(qs)
    datas = []

    with open(config['src_csv']) as src_fh:
        src_reader = csv.DictReader(src_fh)
        for s in src_reader:
            row_data = []
            for item in table_info:
                row_data.append(s[item[0]])
            datas.append(row_data)

    cur.executemany(insert_sql, datas)
    star_conn.commit()
    star_conn.close()

if __name__ == '__main__':
    load_stars(CONFIG)
