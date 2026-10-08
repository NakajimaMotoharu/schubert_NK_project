"""Independent literal new-source post bindings; old fixed content not imported."""
import unittest
from pg642_stop_binding_test import fixture
from pg643_terminal_final import payload


class Binding(unittest.TestCase):
    def test_complete_fresh_post_scope(self):
        seals = {name: str(i+1)*64 for i, name in enumerate(
            ('before.private.json', 'after.private.json', 'complete.private', 'parent.private.jsonl'))}
        source = payload(fixture(), seals); compile(source, '<fixed current post>', 'exec')
        for text in ('pg642-native-stop-v1', 'pg642-native-tools-v1', 'pg643-terminal-final-v1',
                     'pg631-manifest.sig', "summary=e['completed'](receipt_rows,strict(done_path,0o600,141))", "native==snapshot()", 'manager.UnrefUnit(u)',
                     'bus.close()', "rows==after['rows']and len(rows)==24", "show(u,configuration_fields())==after['configuration'][u]",
                     "'startsStopsReloadsSqlWrites':0"):
            self.assertIn(text, source)
        for old in ('pg611', 'PG600', '23b14a44', '1207482', '87761979588', '19b7e618'):
            self.assertNotIn(old, source)


if __name__ == '__main__': unittest.main()
