import unittest
from rekisterihaku import calculate_tax, base_tax_from_mass

# calculate_tax(weight_kg, first_registration_year, fuel_type, co2_method=None, co2=None)
# for reference see traficom calculator:
# https://eservices.traficom.fi/AutoilijanPalvelut/Ajoneuvoverolaskuri?langId=fi

class TestVehicleTaxCalculator(unittest.TestCase):
    def test_base_tax_from_mass(self):
        self.assertEqual(base_tax_from_mass(0), 170.82)
        self.assertEqual(base_tax_from_mass(1337), 181.77)
        self.assertEqual(base_tax_from_mass(1500), 193.45)
        self.assertEqual(base_tax_from_mass(2100), 278.86)
        self.assertEqual(base_tax_from_mass(4000), 580.35)
        self.assertEqual(base_tax_from_mass(7000), 580.35)

    def test_calculate_old_gasoline_nedc_tax(self):
        tax = calculate_tax(2100, 2000, "bensiini")
        self.assertEqual(tax['base'], 330.69)

    def test_calculate_fresh_diesel_tax(self):
        tax = calculate_tax(1940, 2008, "diesel", nedc_co2=153)
        self.assertEqual(tax['base'], 208.05)
        self.assertEqual(tax['fuel'], 401.50)

    def test_calculate_fresh_gasoline_nedc_tax(self):
        tax = calculate_tax(1820, 2004, "bensiini", nedc_co2=171)
        self.assertEqual(tax['base'], 246.010)

    def test_calculate_super_high_nedc(self):
        tax = calculate_tax(1820, 2004, "bensiini", nedc_co2=3000)
        self.assertEqual(tax['base'], 654.440)

    def test_calculate_super_high_weight(self):
        tax = calculate_tax(18200, 2000, "bensiini")
        self.assertEqual(tax['base'], 632.180)

    def test_calculate_zero_weight(self):
        self.assertEqual(calculate_tax(0, 2000, "bensiini")['base'], 222.65)
        self.assertEqual(calculate_tax(0, 2002, "bensiini")['base'], 222.65)


if __name__ == '__main__':
    unittest.main()
