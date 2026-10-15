"""Current admitted final closure, independent golden resume and old identity rejection."""
import unittest
import pg3574_current_browser_resume_once as once
import pg3576_current_browser_live_binding as live


class CurrentOnce(unittest.TestCase):
    def test_final_full11_actual_admission(self):
        raw=once.payload({'pg3572_watch_parent.py':'a'*64})
        self.assertEqual(1,raw.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"))
        self.assertIn('require(len(records)==28)',raw)
        self.assertIn("accepted_before=after",raw)
        self.assertIn("'selectedRun':'e1ee096d-370b-4ab9-915a-7c124207e854'",raw)
        self.assertIn('47ece6dcbeea49f23b6dc2a2bfca4fdfe4dcc02d8b846f7992a6c590b5dea0cd',raw)
        self.assertIn("native==after['native']",raw)
        self.assertNotIn('pg2982',raw)
        self.assertNotIn('PG2802',raw)

    def test_actual_new_activation(self):
        raw=live.body()
        self.assertIn('225691a3-e748-42c4-8972-5ffda5de893d',raw)
        self.assertIn('e1ee096d-370b-4ab9-915a-7c124207e854',raw)
        self.assertIn('2026-10-15T16:49:02.160964Z',raw)
        self.assertNotIn('PG2802',raw)


if __name__=='__main__':unittest.main()
