"""Reuse independent literal negative fixtures, current protected progress=10."""
import unittest
from unittest.mock import patch
import pg2021_fresh_resume_terminal_receipt_test as terminal_fixture
import pg2023_fresh_resume_rows_oracle_test as rows_fixture
from pg2364_current_resume_terminal import bind,payload as terminal_payload
from pg2021_fresh_resume_terminal_receipt import classify as old_classify
from pg2366_current_resume_rows import qualify,payload as rows_payload
import inspect


class CurrentTerminal(terminal_fixture.Receipt):
    def setUp(self):
        ns={};exec(bind(inspect.getsource(old_classify)),ns)
        self.addCleanup(patch.stopall)
        patch.object(terminal_fixture,'classify',ns['classify']).start()
        patch.object(terminal_fixture,'payload',lambda b:terminal_payload({**b,'rootPid':104841})).start()


class CurrentRows(rows_fixture.Rows):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(rows_fixture,'qualify',qualify).start()
        patch.object(rows_fixture,'payload',rows_payload).start()

    def fixture(self):
        old,new=super().fixture()
        old['schubert.inbox_inspection_progress'][0]['protected_count']=10
        new['schubert.inbox_inspection_progress'][0]['protected_count']=10
        return old,new


if __name__=='__main__':unittest.main()
