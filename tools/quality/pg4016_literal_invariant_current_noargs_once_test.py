import json
import unittest
from pyflakes.api import check
import pg4012_literal_invariant_current_observer as observer
import pg4016_literal_invariant_current_noargs_once as once
import pg4018_literal_invariant_current_live_binding as live
import pg4020_literal_invariant_admission_before as before
import pg4022_literal_invariant_acceptance as acceptance


class NewOrdinaryAdmission(unittest.TestCase):
    def test_actual_whole_once_namespace_all_ten_refs_native46_and_no_prelude_change(self):
        raw = once.payload({}); self.assertEqual(0, check(raw, '<new actual once namespace>')); compile(raw, '<new actual once namespace>', 'exec')
        for value in [once.SOURCE, once.BOM, 'pg4012', once.SLOT, 'require(len(records)==46)', 'manager.RefUnit(unit)', 'manager.UnrefUnit(unit)', 'genuineParentDone']:
            self.assertIn(value, raw)
        self.assertNotIn('require(len(records)==34)', raw)
        self.assertIn('pg4008-literal-invariant-publication-independent-post-v1', observer.source())
        self.assertIn('0.1.0-PG3976', observer.source())
        prior = once.post.role.ro.unused.current_tuple()[0]
        self.assertIn('fields[1]!=' + repr(prior['run']), live.body())
        self.assertIn('fields[3]!=' + repr(prior['activation']), live.body())

    def test_new_phase_factory_ids_not_old_runtime_authority(self):
        values = acceptance.namespace()
        self.assertEqual(acceptance.TERM, values['TERM']); self.assertEqual(acceptance.ROWS, values['ROWS']); self.assertEqual(acceptance.SEAL, values['SEAL'])
        raw = values['bind']('PG2654 pg2654-manifest.sig pg2682-parent-watch-v1')
        self.assertEqual('PG3976 pg3976-manifest.sig pg4012-parent-watch-v1', raw)
        actual = json.loads((once.W / once.post.SLOT / 'manifest.safe.json').read_bytes())
        self.assertEqual(before.AFTER, actual['result']['postSha256'])
        for phase in ['other', '', None]:
            with self.assertRaises(ValueError): values['entry'](phase)


if __name__ == '__main__': unittest.main()
