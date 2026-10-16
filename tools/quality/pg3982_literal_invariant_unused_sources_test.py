"""Pure fixture BOM only: complete graph, collision proof and historical payload preservation."""
import ast
import inspect
import unittest
from unittest.mock import patch
import pg3982_literal_invariant_unused_sources as role
import pg3984_literal_invariant_unused_compile as compiler
import pg3986_literal_invariant_unused_dispatch as dispatch
import pg3988_literal_invariant_unused_post as post
from immutable_payload_binding import PROTECTED


def protected(raw):
    return {t.id: ast.literal_eval(n.value) for n in ast.parse(raw).body if isinstance(n, ast.Assign)
            for t in n.targets if isinstance(t, ast.Name) and t.id in PROTECTED}


class NewUnusedRoles(unittest.TestCase):
    def test_simultaneous_old_current_and_new_candidate_never_hash_substring(self):
        with patch.object(role, 'candidate_bom', return_value='a' * 64):
            original = role.previous.previous
            self.assertEqual(role.CURRENT + ' ' + role.SOURCE, role.role_text(original.CURRENT + ' ' + original.SOURCE))
            self.assertEqual('PG3976 PG3748', role.role_text('PG3420 PG2802'))
            self.assertEqual(role.CURRENT + ' ' + role.SOURCE, role.normalized_text(role.previous.CURRENT + ' ' + role.previous.SOURCE))
            digest = 'a' + original.SOURCE + 'b' * 23
            self.assertEqual(digest, role.role_text(digest))
            wrong = "negative='323bc9ad-1528-449a-8067-19228ee1e046'"
            self.assertEqual(wrong, role.role_text(wrong))

    def test_complete18_current_root_data_and_protected_oracles_unchanged(self):
        with patch.object(role, 'candidate_bom', return_value='a' * 64), patch.object(role, 'qualify'):
            values = role.sources(); self.assertEqual(18, len(values))
            self.assertEqual(role.current_tuple()[0], role.previous.previous.binding(values['pg3982_parent_receipt.py']))
            for suffix in ['parent_receipt', 'warning_parent_projection']:
                old = role.pinned(role.LATEST, 'pg3876_' + suffix + '.py')
                self.assertEqual(protected(old), protected(values['pg3982_' + suffix + '.py']))
            emitted = compiler.compiler(); compile(emitted, '<pure fixture graph only>', 'exec')
            for value in ['pg3976-release-v1', 'pg3976-manifest-v1.sig', 'pg3980-current-before-view-v1', 'pg3878-frozen-v1', 'pg3876-current-resume-owned-tools-v1', 'pg3748-release-v1']:
                self.assertIn(value, emitted)
            for value in ['pg3152-frozen-v1', 'pg3420-release-v1', 'systemctl', 'daemon-reload']:
                self.assertNotIn(value, emitted)
            with self.assertRaises(ValueError): role.sources('b' * 64)

    def test_normalized_consumers_do_not_double_translate_candidate_into_current(self):
        with patch.object(role, 'candidate_bom', return_value='a' * 64):
            raw = dispatch.source(); compile(raw, '<new stage/place consumer only>', 'exec')
            self.assertIn('pg3976-candidate-build-v1', role.normalized_text(inspect.getsource(dispatch.previous.main)))
            self.assertIn('PG3986_IMMUTABLE_STAGE_V1', dispatch.stage_source())
            extra = post.extra_source()
            self.assertIn("candidate=Path('/opt/schubert-nk/releases/0.1.0-PG3976')", extra)
            self.assertIn("readlink())=='/opt/schubert-nk/releases/0.1.0-PG3748'", extra)
            self.assertIn('pg3980-current-7fff-before-view-v1', extra)
            self.assertIn('native46Preserved', extra)
            self.assertEqual(role.CURRENT, dispatch.before_record()['productionSource'])


if __name__ == '__main__': unittest.main()
