import unittest
from pathlib import Path
import pg6064_local_map_expiry_review as t


class SpecificPremiseNotBlanketWaiverTest(unittest.TestCase):
    def test_exact_current_local_builders_and_missing_copy_rejected(self):
        rows = t.json.loads((t.W/'pg6054-expiry-read-qualification-v1/findings.safe.json').read_bytes())
        selected = [r for r in rows if Path(r['sourcePath']).stem in t.MAP_LINES
                    and r['rule'] == 'UseConcurrentHashMap' and int(r['beginline']) in t.MAP_LINES[Path(r['sourcePath']).stem]]
        self.assertEqual(11, len(selected))
        for row in selected:
            name = Path(row['sourcePath']).stem; text = (t.ROOT/row['sourcePath']).read_text()
            token = t.fragment(text, row).strip()
            self.assertTrue(t.map_premise(name, text, token))
            with self.assertRaises(ValueError):
                t.map_premise(name, text.replace('Map.copyOf', 'differentCopy'), token)
            with self.assertRaises(ValueError):
                t.map_premise('UnreviewedClass', text, token)

    def test_new_read_identity_helper_is_explicit_and_wrong_call_rejected(self):
        helper = 'private static <T> T presentRead(@Nullable T value) throws SQLDataException { if(value==null) throw new SQLDataException("fixed"); return value; }'
        body = '{ var values = presentRead(rows); use(values); }'
        scope = dict(body=body, variable='rows')
        self.assertEqual('values', t.alias_binding(helper+' void f()'+body, scope, 'presentRead')['alias'])
        for name in ('present', 'unreviewed'):
            with self.assertRaises(ValueError):
                t.alias_binding(helper+' void f()'+body, scope, name)


if __name__ == '__main__':
    unittest.main()
