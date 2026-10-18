import re
import unittest
import pg5348_manager_session_selected as entry
import pg5352_manager_session_public as public


class ManagerInventory(unittest.TestCase):
    def test_existing_seven_and_exact_new_two_are_not_nine_old(self):
        root=entry.selected.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/SystemManagerObservationTest.java'
        raw=root.read_text();names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(names),9);self.assertEqual(raw.count('@Test'),9)
        self.assertEqual(tuple(n for n in names if n.startswith('managerown')),public.NAMES)
        self.assertEqual(len([n for n in names if not n.startswith('managerown')]),7)

    def test_all_current_ports_suites_repetitions_and_new_credit_are_explicit(self):
        entry.configure()
        self.assertEqual(len(entry.selected.EXTRA_CHANGED),57)
        self.assertEqual(len(entry.selected.EXTRA_DEBUG),175)
        self.assertEqual(len(entry.extra_suites()),101)
        values=public.revalidated_case_ids(owner_new=True)
        self.assertEqual(sum(v['newInThisChange'] for v in values.values()),2)
        self.assertEqual(sum(v['newInThisChange'] for v in public.revalidated_case_ids().values()),0)
        self.assertEqual(len({v['testId'] for v in values.values()}),len(values))
        self.assertEqual(entry.repetitions(),entry.previous.repetitions())


if __name__=='__main__':unittest.main()
