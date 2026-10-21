import unittest
import finite_selected_profile as profile
import pg6582_api_jdbc_domain_selected as selected
from pg6580_api_mapper_correction import verify


class ApiDomainDefinitionTest(unittest.TestCase):
    def test_original_blobs_corrected_body_and_fixed_oracle(self):
        value=verify()
        self.assertEqual(19,len(value['files']))
        self.assertEqual(0,value['productionPtPassAdded'])

    def test_exact_inventory_and_compile_before_pt(self):
        _,counts=selected.inventory()
        self.assertEqual((256,39),(sum(counts.values()),len(counts)))
        raw=profile.runner(*selected.EXPECTED,selected.targets())
        self.assertIn('exits==[0,0,0]',raw)
        self.assertLess(raw.index("['-DskipTests'"),raw.index("['-Dtest='"))
        self.assertEqual(19,len(selected.targets()['api']))


if __name__=='__main__':unittest.main()
