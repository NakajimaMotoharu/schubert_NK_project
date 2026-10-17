"""Frozen current read retains all actual validation and rejects stale/unsigned input."""
import ast
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4982_current_preservation_readonly as role


class CurrentPreservation(unittest.TestCase):
    def test_actual_namespace_and_new_no_mutation_scope(self):
        raw=role.payload();self.assertEqual(0,check(raw,'<complete fresh preservation>'));ast.parse(raw)
        self.assertEqual(1,raw.count('save=base/'+repr(role.SLOT)))
        self.assertIn("sum(p.endswith('.exec')for p in full11['native'])==80",raw)
        self.assertIn("'dataOnlyNotRuntimeAuthority':True",raw)
        self.assertIn("'candidateDeployed':False",raw);self.assertIn("'nativeCandidateCredit':False",raw)
        self.assertIn('current_normal_or_gc(terminal,current_bootstrap)',raw)
        self.assertIn("'capturedNormal20VerifiedBeforeCurrent':True",raw)
        for p in(role.__file__,__file__):self.assertEqual(0,checkPath(p))

    def test_all_original_functions_identical_no_profile_softening(self):
        old=(role.W/role.completed.SLOT/'payload.private.py').read_text();new=role.payload()
        functions=lambda text:{node.name:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
            for node in ast.parse(text).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        self.assertEqual(functions(old),functions(new))
        self.assertEqual(11,len(role.FIELDS));self.assertEqual(11,len(set(role.FIELDS)))

    def test_failed_or_unsigned_candidate_never_emits_vm_reader(self):
        path=role.W/'pg4980-candidate-build-v1.safe.json';actual=json.loads(path.read_bytes());original=Path.read_bytes
        for key,value in(('actualExit',1),('signatureVerified',False),('candidateSource',role.SOURCE),('manifestSha256','f'*64)):
            def read(p,key=key,value=value):return json.dumps({**actual,key:value}).encode()if p==path else original(p)
            with patch.object(Path,'read_bytes',read):
                with self.assertRaises(ValueError):role.payload()


if __name__=='__main__':unittest.main()
