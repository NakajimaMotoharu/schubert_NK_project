"""Actual nested archive policy and reserved generation paths, no VM calls."""
import ast
import unittest
import pg1646_completed_unused_dispatch as p


class CompletedDispatchTest(unittest.TestCase):
    def test_actual_nested_archive_and_closed_generation(self):
        ast.parse(p.STAGE)
        env = {}
        exec(p.STAGE[:p.STAGE.index('import pathlib,hashlib,json,os,tarfile,stat')], env)
        gate = env['archive_members']
        gate([('one', 'dir'), ('one/A.class', 'file'), ('two', 'dir'), ('two/A.class', 'file')], {'one/A.class', 'two/A.class'})
        for bad in [[('../a', 'file')], [('a', 'link')], [('one/A.class', 'file')], [('a', 'file'), ('a', 'file')]]:
            with self.assertRaises(ValueError):
                gate(bad, {'one/A.class'})
        self.assertIn('pg1645-completed-unused-tools-v2.tar', p.STAGE)
        self.assertIn('3d69f5af-6bac-46b1-a540-7591c4a79a0d', p.STAGE)
        self.assertIn('0.1.0-PG1544', p.STAGE)
        raw = p.source()
        for literal in ['pg1645-frozen-v1.safe.json', 'pg1641-completed-current-before-v2/manifest.safe.json', 'pg1646-release-v2.tar', 'pg1638-manifest-v1.sig', 'Pg1640UnusedStage place', '1683dd9f6de00e71d2317d9af3cd50400a37bf4e']:
            self.assertIn(literal, raw)
        for operation in ['systemctl start', 'systemctl stop', 'daemon-reload', 'StartUnit', 'StopUnit']:
            self.assertNotIn(operation, p.STAGE + raw)


if __name__ == '__main__':
    unittest.main()
