"""Actual sealed original/no prior day plus independent selector namespace contracts."""
import ast
import datetime
import unittest
from pyflakes.api import check
import pg2876_network_admission_original as p


class AdmissionOriginal(unittest.TestCase):
    def test_literal_utc_dependency_null_contract_and_unknown_date_rejected(self):
        raw=p.payload();tree=ast.parse(raw)
        nodes=[n for n in tree.body if isinstance(n,ast.Import)and any(a.name=='datetime'for a in n.names)
            or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='UTC'for t in n.targets)
            or isinstance(n,ast.FunctionDef)and n.name=='instant']
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent date vector>','exec'),env)
        self.assertEqual(datetime.datetime(2026,10,14,19,12,28,842213,tzinfo=datetime.timezone.utc),env['instant']('2026-10-14T19:12:28.842213Z'))
        self.assertIsNone(env['instant'](None))
        for v in ['','unknown']:
            with self.assertRaises((ValueError,TypeError,AttributeError)):env['instant'](v)
        self.assertTrue('pg2876-network-admission-original-v2'in raw)
        self.assertFalse('pg2876-network-admission-original-v1'in raw)

    def test_real_original_not_actual_database_as_oracle(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<whole literal original selectors>'))
        for v in ['external-before.private.json',"set(before)=={'immutable','runtime','trees','observer'}",
            "day=='2026-10-15'",'not any(row[\'business_date\']==day','classify_inbox(',
            "'actualDbRowsRead':0", "'productionCalls':0"]:self.assertTrue(v in raw,v)
        for v in ['psql','systemctl','clock_settime','2026-10-13\'']:
            self.assertFalse(v in raw,v)


if __name__=='__main__':unittest.main()
