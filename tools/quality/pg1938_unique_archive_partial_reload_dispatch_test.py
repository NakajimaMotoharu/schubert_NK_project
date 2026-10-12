"""Actual producer reservation filename and consumer archive literal are identical."""
import ast
import unittest
import pg1938_unique_archive_partial_reload_dispatch as d


class Archive(unittest.TestCase):
    def test_actual_archive_remote_current_toolroot_and_gate_do_not_mix_old_slots(self):
        source=d.source();tree=ast.parse(source)
        n=[n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='archive'for t in n.targets)]
        self.assertEqual(1,len(n));self.assertEqual("'pg1938-qualified-tools-v1.tar'",ast.unparse(n[0].value.right))
        self.assertIn(d.REMOTE+'/'+d.ARCHIVE,d.STAGE)
        self.assertIn('pg1938-stage-v1.exit',source)
        self.assertNotIn('pg1932-',source);self.assertNotIn('pg1927-',source)
        self.assertIn('0.1.0-PG1846',d.STAGE);self.assertNotIn('0.1.0-PG1638',d.STAGE)
        self.assertIn('pg1925-partial-reload-tools-v1',d.STAGE)


if __name__=='__main__':unittest.main()
