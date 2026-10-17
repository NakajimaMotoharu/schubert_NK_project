"""All18 exact namespaces/real retired tuple and immutable history capsules."""
import ast
from collections import Counter
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import assignments
import pg4986_ssc304_unused_sources as role


def capsules(raw):return Counter(ast.get_source_segment(raw,n)for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))


class Unused(unittest.TestCase):
    def test_all_eighteen_complete_and_immutable_actual_current_tuple(self):
        values=role.sources();self.assertEqual(18,len(values))
        for suffix in('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(role.pinned(role.LATEST,'pg4916_'+suffix+'.py')),capsules(values['pg4986_'+suffix+'.py']))
        parser=role.previous.previous.previous.previous.previous.binding
        self.assertEqual(role.current_tuple()[0],parser(values['pg4986_parent_receipt.py']))
        self.assertIn("pathlib.Path('/proc/882496')",values['pg4986_native_refs.py'])
        self.assertNotIn('/proc/225062',values['pg4986_native_refs.py'])
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",values['pg4986_native_refs.py'])
        for name,raw in values.items():
            if not name.endswith('.py'):continue
            prefix="BUNDLE_HASH='"+'b'*64+"'\n"if name in('pg4986_native_refs.py','pg4986_input_preflight.py')else''
            self.assertEqual(0,check(prefix+raw,'<complete new role '+name+'>'))
            if prefix:self.assertEqual([],assignments(raw)[1])

    def test_strict_current_all80_and_hash_bound_no_candidate_authority(self):
        actual=json.loads(role.VIEW_LOCAL.read_bytes())
        for key,value in(('productionSource',role.SOURCE),('nativePhysicalFiles',72),('allResources0',False),
                          ('candidateDeployed',True),('nativeCandidateCredit',True),('privateBeforeSha256','0'*64)):
            bad=json.loads(json.dumps(actual));bad['result'][key]=value
            with patch.object(role,'candidate_bom',return_value='f'*64),patch.object(role.json,'loads',return_value=bad):
                with self.assertRaises(ValueError):role.qualify()
        with self.assertRaises(ValueError):role.sources(before='0'*64)

    def test_one_pass_hash_boundary_and_static(self):
        self.assertEqual(role.CURRENT+' '+role.SOURCE,role.normalized_text(role.previous.CURRENT+' '+role.previous.SOURCE))
        value='f'+role.previous.SOURCE+'a'*23;self.assertEqual(value,role.normalized_text(value))
        for p in(role.__file__,__file__):self.assertEqual(0,checkPath(p))


if __name__=='__main__':unittest.main()
