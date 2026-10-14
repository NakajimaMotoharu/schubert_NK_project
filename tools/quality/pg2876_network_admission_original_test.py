"""Actual sealed original/no prior day plus independent selector namespace contracts."""
import unittest
from pyflakes.api import check
import pg2876_network_admission_original as p


class AdmissionOriginal(unittest.TestCase):
    def test_real_original_not_actual_database_as_oracle(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<whole literal original selectors>'))
        for v in ['external-before.private.json',"set(before)=={'immutable','runtime','trees','observer'}",
            "day=='2026-10-15'",'not any(row[\'business_date\']==day','classify_inbox(',
            "'actualDbRowsRead':0", "'productionCalls':0"]:self.assertTrue(v in raw,v)
        for v in ['psql','systemctl','clock_settime','2026-10-13\'']:
            self.assertFalse(v in raw,v)


if __name__=='__main__':unittest.main()
