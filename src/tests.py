import unittest

from constellation import Constellation, ConstellationPoint


class ConstellationTests(unittest.TestCase):

    def test_midpoint(self):
        test_con = Constellation('Ori', {})
        test_con.add_star(ConstellationPoint(0, '', 'll', 1, 1, '', ''))
        test_con.add_star(ConstellationPoint(1, '', 'ul', 1, 2, '', ''))
        test_con.add_star(ConstellationPoint(2, '', 'ur', 2, 2, '', ''))
        test_con.add_star(ConstellationPoint(3, '', 'lr', 2, 1, '', ''))
        mid_ra, mid_dec = test_con.find_center()
        self.assertEqual(mid_ra, 1.5)
        self.assertEqual(mid_dec, 1.5)

    def test_starfield_range(self):
        test_con = Constellation('Ori', {})
        test_con.add_star(ConstellationPoint(0, '', 'll', 1, 1, 1, ''))
        test_con.add_star(ConstellationPoint(1, '', 'ul', 1, 2, 10, ''))
        test_con.add_star(ConstellationPoint(2, '', 'ur', 2, 2, 100, ''))
        test_con.add_star(ConstellationPoint(3, '', 'lr', 2, 1, 1000, ''))
        for star in test_con.stars.values():
            star.projected  = (star.ra, star.dec)
        star_range = test_con.get_range()
        self.assertEqual(star_range[0], (1,2))
        self.assertEqual(star_range[1], (1, 1000))
        self.assertEqual(star_range[2], (1,2))


if __name__ == '__main__':
    unittest.main()
