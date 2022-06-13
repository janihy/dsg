import unittest
import rekisterihaku


class TestVehicleTaxCalculator(unittest.TestCase):

    def test_calculate_old_gasoline_nedc_tax(self):
        tax = rekisterihaku.calculate_tax(2100, 2000, "bensiini")
        self.assertEqual(tax['base'], 330.69)

    def test_calculate_fresh_diesel_tax(self):
        tax = rekisterihaku.calculate_tax(1940, 2008, "diesel", nedc_co2=153)
        self.assertEqual(tax['base'], 208.05)
        self.assertEqual(tax['fuel'], 401.50)

    def test_calculate_fresh_gasoline_nedc_tax(self):
        tax = rekisterihaku.calculate_tax(1820, 2004, "bensiini", nedc_co2=171)
        self.assertEqual(tax['base'], 246.010)

    def test_calculate_super_high_nedc(self):
        tax = rekisterihaku.calculate_tax(1820, 2004, "bensiini", nedc_co2=3000)
        self.assertEqual(tax['base'], 654.440)

    def test_calculate_super_high_weight(self):
        tax = rekisterihaku.calculate_tax(18200, 2000, "bensiini")
        self.assertEqual(tax['base'], 632.180)

    def test_calculate_zero_weight(self):
        self.assertEqual(rekisterihaku.calculate_tax(0, 2000, "bensiini")['base'], 222.65)
        self.assertEqual(rekisterihaku.calculate_tax(0, 2002, "bensiini")['base'], 222.65)


if __name__ == '__main__':
    unittest.main()
