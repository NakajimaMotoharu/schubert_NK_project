import subprocess
import unittest
import pg5122_root_elf_public as public
import pg5296_handoff_selected as entry
import pg5300_handoff_public as role


class HandoffPublication(unittest.TestCase):
    def test_original_twelve_ids_and_every_old_definition_retained(self):
        old=subprocess.check_output(['git','show','6f8d42065ce19f79edc8e54dd99f991eda1a06a4:tools/quality/pg5122_root_elf_public.py'],
            cwd=entry.selected.ROOT,text=True)
        first=old.index('FACTORY_NAMES = (');last=old.index('\nDIRECTORY_NAMES =',first)
        namespace={};exec(old[first:last],{},namespace)
        self.assertEqual(public.FACTORY_NAMES[:12],namespace['FACTORY_NAMES'])
        self.assertEqual(public.FACTORY_NAMES[12:],tuple(role.METHODS))

    def test_only_new_six_receive_new_credit_and_all21_override_ids_unique(self):
        values=role.revalidated_case_ids(handoff_new=True)
        self.assertEqual(len(values),21)
        self.assertEqual(sum(v['newInThisChange'] for v in values.values()),6)
        self.assertEqual(len({v['testId'] for v in values.values()}),21)
        future=role.revalidated_case_ids()
        self.assertTrue(all(v['newIndependentCase'] and not v['newInThisChange'] for v in future.values()))


if __name__=='__main__':unittest.main()
