import ast
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg3806_hygiene_admission_before as before
import pg3808_hygiene_acceptance as tool


class CurrentSameDay(unittest.TestCase):
    def test_before_immutable_not_live_and_actual_phases_source_roles(self):
        raw=before.payload();ast.parse(raw)
        self.assertEqual(0,check(raw,'<immutable new admission before>'))
        for marker in [before.AFTER,'raw==post',"'execEntries':34",'all(history.values())',tool.ONCE]:self.assertTrue(marker in raw,marker)
        self.assertNotIn('psql',raw)
        with patch.object(tool,'before',return_value=before.AFTER):
            rows=tool.rows_payload()
            live=json.loads((before.W/tool.LIVE/'manifest.safe.json').read_bytes())
            binding={**live['binding'],'rootPid':live['rootPid']}
            terminal=tool.terminal_payload(binding);seal=tool.seal_payload(binding)
        for raw in [rows,terminal,seal]:
            ast.parse(raw);self.assertEqual(0,check(raw,'<whole new same-day phases>'))
            self.assertIn(tool.SOURCE,raw);self.assertNotIn('PG2654',raw)
        for marker in ['ALREADY_SUCCESSFUL','newBackupSteps',tool.ONCE,tool.ROWS,before.AFTER]:self.assertTrue(marker in rows,marker)
        for marker in [tool.ONCE,tool.SEAL,tool.SOURCE,tool.BOM,before.AFTER,'ALREADY_SUCCESSFUL']:self.assertTrue(marker in seal,marker)
        with self.assertRaises(ValueError):tool.entry('start')


if __name__=='__main__':unittest.main()
