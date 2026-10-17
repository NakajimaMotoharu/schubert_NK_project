import ast
from collections import Counter
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import assignments
import pg4864_ssc301_302_unused_sources as role


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PROTECTED for t in n.targets))


class Unused(unittest.TestCase):
    def test_all_eighteen_roles_preserve_actual_completed_data_and_full_namespace(self):
        values=role.sources();self.assertEqual(18,len(values))
        for suffix in ('parent_receipt','warning_parent_projection'):
            self.assertEqual(capsules(role.pinned(role.LATEST,'pg4772_'+suffix+'.py')),capsules(values['pg4864_'+suffix+'.py']))
        parser=role.previous.previous.previous.previous.binding
        self.assertEqual(role.current_tuple()[0],parser(values['pg4864_parent_receipt.py']))
        self.assertIn("'native': tree(pathlib.Path('/run/schubert-nk/pt-coverage'))",values['pg4864_native_refs.py'])
        self.assertIn("pathlib.Path('/proc/860231')",values['pg4864_native_refs.py'])
        self.assertNotIn('/proc/225062',values['pg4864_native_refs.py'])
        for name,raw in values.items():
            if not name.endswith('.py'): continue
            prelude="BUNDLE_HASH='"+'b'*64+"'\n" if name in ('pg4864_native_refs.py','pg4864_input_preflight.py') else ''
            self.assertEqual(0,check(prelude+raw,'<full new role '+name+'>'))
            if prelude:self.assertEqual([],assignments(raw)[1])

    def test_strict_current_data_not_candidate_runtime_authority(self):
        original=json.loads(role.VIEW_LOCAL.read_bytes())
        for key,value in [('productionSource',role.SOURCE),('nativePhysicalFiles',False),('allResources0',False),('capturedNormal20VerifiedBeforeCurrent',False),('nativeCandidateCredit',True),('privateBeforeSha256','0'*64)]:
            bad=json.loads(json.dumps(original));bad['result'][key]=value
            with self.subTest(key=key),patch.object(role,'candidate_bom',return_value='f'*64),patch.object(role.json,'loads',return_value=bad),self.assertRaises(ValueError):role.qualify()
        with self.assertRaises(ValueError):role.sources(before='0'*64)

    def test_one_pass_roles_do_not_rewrite_hash_substrings_or_negative_uuid(self):
        old=role.previous
        self.assertEqual(role.CURRENT+' '+role.SOURCE,role.normalized_text(old.CURRENT+' '+old.SOURCE))
        value='f'+old.SOURCE+'a'*23
        self.assertEqual(value,role.normalized_text(value))
        negative="negative='323bc9ad-1528-449a-8067-19228ee1e046'"
        self.assertEqual(negative,role.normalized_text(negative))


if __name__ == '__main__':unittest.main()
