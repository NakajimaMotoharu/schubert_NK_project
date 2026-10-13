import unittest
import pg2184_newsource_same_day_rows as p


class Rows(unittest.TestCase):
    def test_actual_current_before_and_run_binding_without_sql_write(self):
        raw=p.payload()
        for text in ['pg2178-newsource-noargs-once-v1',p.BEFORE,'02bddddf-9cd3-4668-9d67-7561232fc4e4','2026-10-13T06:29:34.698736Z','begin isolation level repeatable read read only','BACKUP_DB','ALREADY_SUCCESSFUL','PROTECTED_RECORDS']:self.assertIn(text,raw)
        self.assertNotIn('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',raw)
        self.assertEqual(p.entry().__globals__['SOURCE'],'3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8')
        self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
