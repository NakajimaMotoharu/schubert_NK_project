import copy
import json
import unittest
from unittest.mock import patch

import wbs_component_overlay as p


class ComponentOverlayTest(unittest.TestCase):
    def test_history_fallback_keeps_definitions_and_acceptance_exact(self):
        pmo=p.ROOT/'documents/400_PGPT/470_PMO'
        original_read=p.Path.read_bytes
        for name in ('485_WBS網羅性・受入対応.json','486_WBS現行実績.json'):
            path=pmo/name
            frozen=p.subprocess.check_output(['git','show',p.FROZEN+':'+str(path.relative_to(p.ROOT))],cwd=p.ROOT)
            expected=p.hashlib.sha256(frozen).hexdigest()
            self.assertTrue(p.historical_state_unchanged(pmo,{name:expected}))
            changed=json.loads(path.read_text());changed['unapprovedHistoryMutation']=True
            raw=json.dumps(changed).encode()
            def read(subject):
                return raw if subject==path else original_read(subject)
            with patch.object(p.Path,'read_bytes',read),self.assertRaises(ValueError):
                p.historical_state_unchanged(pmo,{name:expected})

    def test_history_cannot_use_wrong_saved_hash_or_rebase_logical_master(self):
        pmo=p.ROOT/'documents/400_PGPT/470_PMO'
        for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json'):
            with self.assertRaises(ValueError):p.historical_state_unchanged(pmo,{name:'0'*64})

    def test_exact_proof_source_shape_no_unknown_exemption(self):
        value=dict(componentOverlay=copy.deepcopy(p.DECLARATION))
        for key in ('source','component','bindingSha256','qualificationSha256'):
            changed=copy.deepcopy(value);changed['componentOverlay'][key]='unknown'
            with self.assertRaises(ValueError):p.verify(changed)
        changed=copy.deepcopy(value);changed['componentOverlay']['unknown']=True
        with self.assertRaises(ValueError):p.verify(changed)

    def test_declared_scope_cannot_hide_missing_added_owner_or_old_byte(self):
        inventory=json.loads((p.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text())
        original=inventory['currentPhysicalCandidate'];original['componentOverlay']=copy.deepcopy(p.DECLARATION)
        hashes,result=p.verify(original)
        self.assertEqual(4,len(hashes));self.assertEqual(1,result['changedPhysicalMain'])
        self.assertFalse(result['coverageUnion']);self.assertFalse(result['originalSixRunRelabelled'])
        for kind in ('missing','extra','owner','oldbyte'):
            value=copy.deepcopy(original)
            rows=[r for r in value['artifacts'] if r['owner']=='WBS-P020-01']
            if kind=='missing':value['artifacts'].remove(rows[0])
            elif kind=='extra':value['artifacts'].append(copy.deepcopy(rows[0]))
            elif kind=='owner':rows[0]['owner']='WBS-F03'
            else:rows[0]['sha256']='0'*64
            with self.assertRaises(ValueError):p.verify(value)


if __name__=='__main__':unittest.main()
