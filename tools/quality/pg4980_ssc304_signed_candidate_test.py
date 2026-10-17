"""Synthetic gate mutations only; not an original whole/static receipt or signature authority."""
import copy
import json
import unittest
from pyflakes.api import checkPath
import pg4980_ssc304_signed_candidate as role


class Candidate(unittest.TestCase):
    def test_synthetic_shape_and_independent_main_bytes(self):
        prior,candidate=role.qualified.candidate_main();gate=copy.deepcopy(prior)
        rows,same=role.qualified.physical_difference(prior['allPhysicalMainSha256'],candidate,candidate)
        gate.update(productionSource=role.SOURCE,tests=3791,suites=553,mainClasses=1650,
            newCases=[list(v)for v in role.qualified.added_cases()],allPhysicalMainSha256=candidate,changedClasses=rows)
        gate['modules']['batch']['tests']+=30;gate['modules']['batch']['suites']+=2;gate['modules']['batch']['mainClasses']+=3
        outer={'actualExit':0,'result':gate};role.validate_gate(outer,role.SOURCE)
        self.assertEqual(1646,same)
        previous=role.GATE
        try:
            role.GATE=gate
            self.assertEqual(1650,role.verify_delta(role.grouped(prior['allPhysicalMainSha256']),role.grouped(candidate)))
            bad={**candidate,next(iter(role.qualified.MODIFIED)):'f'*64}
            with self.assertRaises(ValueError):role.verify_delta(role.grouped(prior['allPhysicalMainSha256']),role.grouped(bad))
        finally:role.GATE=previous
        for key,value in(('tests',3761),('suites',551),('mainClasses',1647),('FESFlakyNotRun',False),
                        ('allSixFormatBeforeAnyPt',False),('productionSource',role.OLD_SOURCE),('formalAccepted',True)):
            bad=copy.deepcopy(outer);bad['result'][key]=value
            with self.assertRaises(ValueError):role.validate_gate(bad,role.SOURCE)
        self.assertNotIn('payloadSha256',outer);self.assertNotIn('signature',json.dumps(outer))

    def test_fixed_host_only_new_paths_and_counts(self):
        raw=role.main_source()
        for literal in("'tests': 3791","'suites': 553","'mainClasses': 1650","'addedClasses': 3",
            "'0.1.0-PG4860'","'0.1.0-PG4980'","{'VERSION', 'operations/batch.jar'} <= changed",
            'pg4970-ssc304-whole-qualified-v1'):
            self.assertIn(literal,raw)
        self.assertNotIn("{'VERSION', 'api/api.jar', 'operations/batch.jar'} <= changed",raw)
        for p in(role.__file__,__file__):self.assertEqual(0,checkPath(p))


if __name__=='__main__':unittest.main()
