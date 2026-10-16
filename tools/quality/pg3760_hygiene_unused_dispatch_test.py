import ast
import copy
import json
import types
import unittest
import pg3760_hygiene_unused_dispatch as c


class Dispatch(unittest.TestCase):
    def test_correct_current_boot_release_and_first_stage_only(self):
        self.assertIn('0.1.0-PG3420',c.STAGE);self.assertNotIn('0.1.0-PG2802',c.STAGE);self.assertIn(c.role.TOOLS,c.STAGE)
        node=next(n for n in ast.parse(c.STAGE).body if isinstance(n,ast.Assert)and 'boot_id'in ast.unparse(n));code=compile(ast.Module(body=[node],type_ignores=[]),'<real fixed boot gate>','exec')
        for boot in [c.role.BOOT,'00000000-0000-0000-0000-000000000000']:
            ns={'pathlib':types.SimpleNamespace(Path=lambda _:types.SimpleNamespace(read_text=lambda:boot))}
            if boot==c.role.BOOT:exec(code,ns)
            else:
                with self.assertRaises(AssertionError):exec(code,ns)
        raw=c.source();self.assertIn('pg3760-stage-v1.exit',raw);self.assertNotIn('pg3760-stage-v2.exit',raw)
        line=next(x for x in raw.splitlines()if x.strip().startswith('current='));self.assertIn(str(c.role.VIEW_LOCAL.relative_to(c.W)),line);self.assertIn("['result']",line);self.assertNotIn('current-4856-before-view',line)
        for value in [c.role.SOURCE,'pg3758-frozen',c.role.ARCHIVE,'pg3748-manifest-v1.sig','reserved actual action must not be replayed','unusedPlacementOnly']:self.assertIn(value,raw)

    def test_current_before_and_candidate_cannot_be_forged_into_operation_authority(self):
        candidate=json.loads((c.W/'pg3748-candidate-build-v1.safe.json').read_bytes());before=c.before_record();ns=c.runtime_namespace(candidate,before);self.assertEqual(c.role.SOURCE,ns['SOURCE']);self.assertEqual(c.role.BOM,ns['DIGEST']);self.assertEqual(c.role.BEFORE,ns['BASELINE_SHA'])
        for key,value in [('genuineCompletion',None),('runtimeAlreadyRetired',False),('dataOnlyNotRuntimeAuthority',False),('allTenUnitsKernelEmpty',False),('privateBeforeSha256','a'*64)]:
            wrong=copy.deepcopy(before);wrong[key]=value
            with self.assertRaises(ValueError):c.runtime_namespace(candidate,wrong)
        with self.assertRaises(ValueError):c.runtime_namespace({**candidate,'signatureVerified':False},before)


if __name__=='__main__':unittest.main()
