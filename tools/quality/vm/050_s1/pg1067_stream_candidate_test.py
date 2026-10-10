"""PT-DEP-1067001..003 independent exact class delta and signed-candidate source guard."""
import copy
import unittest
from pg1067_stream_candidate_contract import MODULES,verify_delta
from pg1068_stream_candidate_build import source


class StreamCandidate(unittest.TestCase):
    def fixture(self):
        before={m:{'fixed.class':'a'*64}for m in MODULES}
        name='dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader.class'
        before['batch'][name]='a'*64;after=copy.deepcopy(before);after['batch'][name]='b'*64
        return before,after

    def test_exact_closed_delta_and_each_extra_or_missing_change_refused(self):
        before,after=self.fixture();self.assertEqual(7,verify_delta(before,after))
        for change in ('other','add','remove','unchanged'):
            modified=copy.deepcopy(after)
            if change=='other':modified['web']['fixed.class']='b'*64
            elif change=='add':modified['batch']['extra.class']='b'*64
            elif change=='remove':del modified['api']['fixed.class']
            else:modified=copy.deepcopy(before)
            with self.assertRaises(ValueError):verify_delta(before,modified)

    def test_null_unknown_module_and_digest_refused(self):
        before,after=self.fixture()
        for value in (None,{}, {'unknown':{}}):
            with self.assertRaises(ValueError):verify_delta(value,after)
        changed=copy.deepcopy(after);changed['api']['fixed.class']=None
        with self.assertRaises(ValueError):verify_delta(before,changed)

    def test_frozen_correct_source_no_current_write_or_old_native_import(self):
        raw=source()
        self.assertIn("SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'",raw)
        self.assertIn("OLD = W / 'pg932-release-v1'",raw)
        self.assertIn("NEXT = W / 'pg1068-release-v1'",raw)
        self.assertIn("FROZEN = W / 'pg1018-stream-six-host-v2'",raw)
        self.assertIn("gate['tests'] == 3563",raw)
        self.assertIn("'changedClasses': 1",raw)
        self.assertIn('gate[\'oldNativeStreamsNotImported\']',raw)
        self.assertNotIn('pg926-body-six-host-v1',raw)


if __name__=='__main__':
    unittest.main()
