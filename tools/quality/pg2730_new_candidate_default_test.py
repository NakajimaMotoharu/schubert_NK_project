"""Independent signed literal default-BOM vectors; no old dependency fallback."""
import json
import unittest
from unittest.mock import patch
from pg1446_current_cold_stage import W
import pg2682_operation_current_observer as observer
import pg2684_operation_current_noargs_once as admission
import pg2700_operation_current_terminal as terminal
import pg2704_operation_current_full_seal as seal
import pg2706_operation_current_parent_projection as parent

NEW='552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37'
OLD='2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f'


class DefaultDependencies(unittest.TestCase):
    def binding(self):
        v=json.loads((W/'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        return {**v['binding'],'rootPid':v['rootPid'],'run':'00000000-0000-0000-0000-000000000001','activation':'00000000-0000-0000-0000-000000000002'}

    def test_all_five_default_producers_match_explicit_new_bom(self):
        vector=self.binding()
        cases=[(observer,'source',()),(admission,'body',()),(terminal,'payload',(vector,)),(seal,'payload',(vector,)),(parent,'payload',('a'*64,))]
        with patch.object(seal,'before',return_value='b'*64):
            for module,name,args in cases:
                with self.subTest(module=module.__name__),patch.object(module,'candidate_bom',return_value=NEW),patch.object(module.previous,'candidate_bom',side_effect=AssertionError('old default producer refused')):
                    default=getattr(module,name)(*args);explicit=getattr(module,name)(*args,NEW)
                self.assertEqual(default,explicit);self.assertIn(NEW,default);self.assertNotIn(OLD,default)


if __name__=='__main__':unittest.main()
