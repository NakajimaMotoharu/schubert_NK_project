"""PT-DEP-1062001..002 new generated slots and corrected source/phase/null contracts."""
import ast
import unittest
from pg1062_cold_preparation_sources_v2 import files


class Fresh(unittest.TestCase):
    def test_exact_new_sources_no_old_reservation_reuse(self):
        generated=files()
        self.assertEqual({'Pg1062ColdOwnedPreparation.java','Pg1062ColdOwnedPreparationTest.java','pg1062_cold_refs.py'},set(generated))
        for source in generated.values():
            self.assertNotIn('pg1037-cold-prepared-v1',source)
            self.assertNotIn('pg1037-cold-tools-v1',source)
            self.assertNotIn('Pg1037ColdOwnedPreparation',source)
        self.assertIn('"pg1062_cold_refs.py"',generated['Pg1062ColdOwnedPreparation.java'])

    def test_corrected_sql_maintenance_and_exact_phase_order(self):
        generated=files();java=generated['Pg1062ColdOwnedPreparation.java'];py=generated['pg1062_cold_refs.py']
        ast.parse(py)
        phases=['ORIGINAL_BEFORE_REFERENCES','REFERENCES_PREPARE','ORIGINAL_AFTER_REFERENCES','OWNED_HOST_RO','IMMUTABLE_FULL_VERIFIER','FINITE_EMPTY_NAMESPACES']
        points=[java.index('phase="'+p+'"')for p in phases]
        self.assertEqual(sorted(points),points)
        self.assertIn("'/run/schubert-nk/maintenance'",py)
        self.assertIn("'maintenance':metadata(root/'maintenance')",py)
        self.assertIn('str(backend)+" and "',py)
        self.assertNotIn('str(backend)+"and "',py)
        self.assertIn('args!=null',java)
        self.assertIn('ownershipNotInferred=true',java)


if __name__=='__main__':
    unittest.main()
