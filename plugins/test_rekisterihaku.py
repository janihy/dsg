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

    def test_calculate_old_gasoline_tax(self):
        tax = calculate_tax(2100, 2000, "bensiini")
        self.assertEqual(tax["base"], 278.86)
        self.assertEqual(tax.get("fuel", 0), 0)

    def test_calculate_fresh_diesel_tax(self):
        tax = calculate_tax(1940, 2008, "diesel", co2_method="nedc", co2=153)
        self.assertEqual(tax["base"], 180.67)
        self.assertEqual(tax.get("fuel", 0), 401.50)

    def test_calculate_fresh_gasoline_nedc_tax(self):
        tax = calculate_tax(1820, 2004, "bensiini", co2_method="nedc", co2=171)
        self.assertEqual(tax["base"], 198.92)

    def test_calculate_illegally_high_nedc(self):
        tax = calculate_tax(1820, 2004, "bensiini", co2_method="nedc", co2=3000)
        self.assertEqual(tax["base"], 654.445)

    def test_calculate_illegally_high_weight(self):
        tax = calculate_tax(18200, 2000, "bensiini")
        self.assertEqual(tax["base"], 580.350)

    def test_calculate_zero_weight(self):
        self.assertEqual(calculate_tax(0, 2000, "bensiini")["base"], 170.820)
        self.assertEqual(calculate_tax(0, 2002, "bensiini")["base"], 170.820)

    def test_calculate_old_electric_vehicle_tax(self):
        tax = calculate_tax(1500, 2020, "sähkö")
        self.assertEqual(tax["base"], 106.215)
        self.assertEqual(tax["fuel"], 104.025)

    def test_calculate_fresh_electric_vehicle_tax(self):
        tax = calculate_tax(1500, 2024, "sähkö")
        self.assertEqual(tax["base"], 171.185)
        self.assertEqual(tax["fuel"], 104.025)

if __name__ == "__main__":
    unittest.main()
