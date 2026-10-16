"""Pure fixture signature only: no current authorization, no guest mutation."""
import ast
from collections import Counter
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
from immutable_payload_binding import PROTECTED
from bundle_hash_contract import assignments, require_bound
import pg4706_ssc299_unused_sources as role


def capsules(raw):
    return Counter(ast.get_source_segment(raw,n) for n in ast.walk(ast.parse(raw))
                   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in PROTECTED for t in n.targets))


class NormalUnused(unittest.TestCase):
    def test_complete_eighteen_all_globals_and_exact_latest_immutable_data(self):
        with patch.object(role,'candidate_bom',return_value='f'*64): values=role.sources()
        self.assertEqual(18,len(values))
        for name,raw in values.items():
            if not name.endswith('.py'): continue
            bound="BUNDLE_HASH='"+'b'*64+"'\n"+raw if name in ['pg4706_native_refs.py','pg4706_input_preflight.py'] else raw
            self.assertEqual(0,check(bound,'<actual normal18 '+name+'>'))
        for suffix in ['parent_receipt','warning_parent_projection']:
            self.assertEqual(capsules(role.pinned(role.LATEST,'pg4652_'+suffix+'.py')), capsules(values['pg4706_'+suffix+'.py']))
        self.assertEqual(role.current_tuple()[0],role.previous.previous.previous.binding(values['pg4706_parent_receipt.py']))
        for name in ['pg4706_native_refs.py','pg4706_input_preflight.py']:
            self.assertEqual([],assignments(values[name])[1])
            self.assertTrue(require_bound("BUNDLE_HASH='"+'b'*64+"'\n"+values[name],'b'*64))
        self.assertIn('genuineParentNormalWarningOriginal=true',values['Pg4706UnusedStage.java'])

    def test_foreign_current_missing_normal_and_bool_are_not_old_root_authority(self):
        original=json.loads(role.VIEW_LOCAL.read_bytes())
        for key,value in [('productionSource',role.SOURCE),('nativePhysicalFiles',False),
                          ('currentNormalWarningParentProof',False),('dataOnlyNotRuntimeAuthority',False),
                          ('runtimeConfigFilesToRetire',1),('privateBeforeSha256','0'*64)]:
            bad=json.loads(json.dumps(original));bad['result'][key]=value
            with self.subTest(key=key),patch.object(role,'candidate_bom',return_value='f'*64),patch.object(role.json,'loads',return_value=bad):
                with self.assertRaises(ValueError):role.qualify()

    def test_simultaneous_roles_hash_substrings_and_negative_uuid_preserved(self):
        with patch.object(role,'candidate_bom',return_value='f'*64):
            self.assertEqual(role.CURRENT+' '+role.SOURCE,role.normalized_text(role.previous.CURRENT+' '+role.previous.SOURCE))
            original=role.previous.previous.previous
            self.assertEqual(role.CURRENT+' '+role.SOURCE,role.role_text(original.CURRENT+' '+original.SOURCE))
            digest='a'+original.SOURCE+'b'*23
            self.assertEqual(digest,role.role_text(digest))
            negative="negative='323bc9ad-1528-449a-8067-19228ee1e046'"
            self.assertEqual(negative,role.role_text(negative))
            with self.assertRaises(ValueError):role.sources('0'*64)


if __name__=='__main__':unittest.main()
