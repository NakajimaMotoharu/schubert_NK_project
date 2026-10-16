"""Independent closed activation/observer/preservation checks, no guest dispatch."""
import ast
import unittest
from pg3844_current_resume_sources import SOURCE,BOM,RUN
import pg3852_current_resume_observer as observer
import pg3854_current_completed_resume_once as once
import pg3856_current_resume_live_binding as live
from pg3800_hygiene_browser_ready import require_ready


class AdmissionTest(unittest.TestCase):
    def test_readonly_new_observer(self):
        raw=observer.source();ast.parse(raw)
        self.assertIn('pg3850-current-resume-independent-post-v1',raw)
        self.assertIn("post['result']['independentResumeOnlyDeltaVerified']",raw)
        self.assertIn("stem=W/('pg3852-'+mode+'-v1')",raw)
        self.assertIn(SOURCE,raw);self.assertIn(BOM,raw)
        self.assertNotIn('pg3798',raw)

    def test_once_and_preservation(self):
        raw=once.payload({'pg3852_watch_parent.py':'0'*64});ast.parse(raw)
        self.assertEqual(1,raw.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"))
        for text in [RUN,SOURCE,BOM,'require(len(records)==40)',"'replayAllowed':False",'originalBudgetSeconds',"accepted_before=after","native==after['native']","manager.UnrefUnit(unit)"]:
            self.assertIn(text,raw)
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("['/usr/bin/systemctl','start'"))
        self.assertNotIn("save=base/'pg3850",raw)
        self.assertIn('--resume '+RUN,raw)

    def test_unchanged_browser_ready(self):
        proof=require_ready();self.assertEqual(12,proof['plannedCases']);self.assertEqual(SOURCE,proof['productionSource'])

    def test_same_cutoff_new_activation(self):
        raw=live.body();ast.parse(raw)
        self.assertIn('PG3748',raw);self.assertNotIn('PG3420',raw)
        self.assertIn("fields[1]=='"+RUN+"'",raw)
        self.assertIn("fields[2]=='2026-10-16T00:42:20.585755Z'",raw)
        self.assertIn("fields[3]!='e7584da8-7f80-4f8e-a46c-f46b2388e773'",raw)


if __name__=='__main__':unittest.main()
