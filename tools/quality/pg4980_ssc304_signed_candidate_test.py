"""Synthetic gate mutations only; not an original whole/static receipt or signature authority."""
import copy
import builtins
import dis
import json
import types
import unittest
from pyflakes.api import checkPath
import pg4980_ssc304_signed_candidate as role


class Candidate(unittest.TestCase):
    def test_generated_main_globals_complete_without_executing_signer(self):
        ns={**vars(role.prior),'__name__':'pure_generated_definition','__file__':role.__file__,
            'PRODUCTION':role.SOURCE,'OLD_SOURCE':role.OLD_SOURCE,'OLD_BOM':role.OLD_BOM,
            'OLD':role.OLD,'NEXT':role.NEXT,'FROZEN':role.FROZEN,'SIG':role.SIG,
            'validate_gate':role.validate_gate,'verify_delta':role.verify_delta,'receive':role.receive,
            'qualification_matches':role.qualification_matches}
        exec(compile(role.main_source(),'<definitions only, no signing>','exec'),ns)
        pending=[ns['main'].__code__];globals_used=set()
        while pending:
            code=pending.pop();globals_used.update(i.argval for i in dis.get_instructions(code)if i.opname=='LOAD_GLOBAL')
            pending.extend(v for v in code.co_consts if isinstance(v,types.CodeType))
        self.assertFalse(globals_used-set(ns)-set(vars(builtins)))

    def test_synthetic_shape_and_independent_main_bytes(self):
        prior,candidate=role.qualified.candidate_main();gate=copy.deepcopy(prior)
        rows,same=role.qualified.physical_difference(prior['allPhysicalMainSha256'],candidate,candidate)
        gate.update(productionSource=role.SOURCE,tests=3791,suites=553,mainClasses=1650,
            newCases=[list(v)for v in role.qualified.added_cases()],allPhysicalMainSha256=candidate,changedClasses=rows,
            unchangedPhysicalClasses=1646)
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
                        ('allSixFormatBeforeAnyPt',False),('productionSource',role.OLD_SOURCE),('formalAccepted',True),
                        ('unchangedPhysicalClasses',1644),('unchangedPhysicalClasses',True)):
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
