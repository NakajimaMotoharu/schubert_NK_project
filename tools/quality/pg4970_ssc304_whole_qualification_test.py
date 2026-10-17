"""Strict actual physical differences and original same-source XML scope; no job actions."""
import ast
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg4970_ssc304_whole_qualification as role


class WholeQualification(unittest.TestCase):
    def test_actual_selected_and_all_prior_main_composition(self):
        prior,candidate=role.candidate_main()
        rows,unchanged=role.physical_difference(prior['allPhysicalMainSha256'],candidate,candidate)
        self.assertEqual(4,len(rows));self.assertEqual(1646,unchanged);self.assertEqual(1650,len(candidate))
        cases=role.added_cases();self.assertEqual(30,len(cases));self.assertEqual(30,len(set(cases)))
        for bad in({**candidate,'x:extra.class':'a'*64},
                   {k:v for k,v in candidate.items()if k!=next(iter(role.INTERFACES))},
                   {**candidate,'batch:dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$Stage.class':'a'*64}):
            with self.assertRaises(ValueError):role.physical_difference(prior['allPhysicalMainSha256'],bad,bad)

    def test_complete_server_namespace_and_freshness_order(self):
        raw='import json\nMODIFIED=set()\nINTERFACES=set()\n'+inspect.getsource(role.physical_difference)+'\n'+role.qualifier_source()+'\nprint(json.dumps(qualify({})))\n'
        self.assertEqual(0,check(raw,'<complete full qualification namespace>'))
        self.assertIn('format-before-pt.safe.json',raw);self.assertIn("'allSixFormatBeforeAnyPt': True",raw)
        self.assertIn('ptStartEpochNs',raw);self.assertIn('len(oldcases) == 3761',raw)
        self.assertIn('len(cases) == 3791',raw);self.assertIn('len(additions) == 30',raw)
        self.assertIn('PG4844-six-v1',raw);self.assertIn('PG4968-six-v1',raw)
        ast.parse(raw)
        for path in(role.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
