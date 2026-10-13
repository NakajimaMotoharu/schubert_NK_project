"""Independent normal receipt vectors and whole actual source/run closure checks."""
import ast
import json
import unittest
from pyflakes.api import check
from pg2021_fresh_resume_terminal_receipt_test import Receipt
from pg1446_current_cold_stage import W
import pg2452_question_current_terminal as terminal
import pg2454_question_current_rows as rows
import pg2456_question_current_full_seal as seal


class CurrentAcceptance(unittest.TestCase):
    def test_normal_success_warning_and_prior_null_receipts(self):
        for code in [0,10]:
            b,s,r,d=Receipt().fixture(code)
            raw=terminal.payload(dict(b,rootPid=194154))
            nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name in {'classify','_normal_classify'}]
            ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<independent receipt fixed vectors>','exec'),ns)
            self.assertEqual(code,ns['classify'](b,s,r,d)['completionCode'])
            for key,value in [('run','91f5484b-9702-4c7c-97f3-dd5110a853f9'),('activation','e1429ac8-f3dd-4e8c-83d2-1926c4ba8440')]:
                with self.assertRaises(ValueError):ns['classify'](dict(b,**{key:value}),s,r,d)
            with self.assertRaises(ValueError):ns['classify'](None,None,None,None)
            with self.assertRaises(ValueError):ns['classify'](b,dict(s,Result='exit-code'),r,d)
            self.assertEqual(0,check(raw,'<whole current terminal fixture>'))

    def test_literal_actual_new_before_and_same_day_independent_sql(self):
        raw=rows.payload()
        for literal in [rows.BEFORE,'pg2448-question-current-noargs-once-v1',
            '06236d14-a6f8-4d05-a6ff-49c713cc2647','2026-10-13T21:16:10.125382Z',
            'b2d6f605-61cf-425f-8fbd-12d606f6ee66','repeatable read read only',
            'BACKUP_DB','BACKUP_CONFIG','ALREADY_SUCCESSFUL','PROTECTED_RECORDS']:
            self.assertIn(literal,raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertNotIn('systemctl start',raw)
        self.assertEqual(0,check(raw,'<whole all24 fixture>'))

    def test_whole_actual_fullseal_current_bytes_owners_terminal_and_db(self):
        live=json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())
        raw=seal.payload({**live['binding'],'rootPid':live['rootPid']})
        for literal in ['cdbc07cdf77370d521e64de8b327da7f6752139b',
            '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf',
            'PG2428','pg2428-manifest.sig',rows.BEFORE,'before_shape(before)',
            '06236d14-a6f8-4d05-a6ff-49c713cc2647','c347b14a-2e59-41e6-993c-a07e537cbd00']:
            self.assertIn(literal,raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertNotIn('pg2178-newsource-noargs-once-v1',raw)
        self.assertEqual(0,check(raw,'<whole current seal fixture>'))
        for m in [terminal,rows,seal]:self.assertEqual(m.entry().__globals__['SOURCE'],'cdbc07cdf77370d521e64de8b327da7f6752139b')


if __name__=='__main__':unittest.main()
