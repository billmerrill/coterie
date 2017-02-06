import unittest

from build_orion import Constellation, ConstellationPoint


class ConstellationTests(unittest.TestCase):

    def test_midpoint(self):
        test_con = Constellation('Ori', {})
        test_con.add_star(ConstellationPoint(0, '', 'll', 1, 1, '', ''))
        test_con.add_star(ConstellationPoint(0, '', 'ul', 1, 2, '', ''))
        test_con.add_star(ConstellationPoint(0, '', 'ur', 2, 2, '', ''))
        test_con.add_star(ConstellationPoint(0, '', 'lr', 2, 1, '', ''))
        mid_ra, mid_dec = test_con.find_center()
        self.assertEqual(mid_ra, 1.5)
        self.assertEqual(mid_dec, 1.5)


if __name__ == '__main__':
    unittest.main()
