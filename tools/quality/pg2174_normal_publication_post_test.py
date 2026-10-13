import unittest
from pg2174_normal_publication_post import payload


class Post(unittest.TestCase):
    def test_all_actual_public_phases_new_source_and_no_unit_delta(self):
        raw=payload()
        for text in ['for stamp,phase,observed in phases:','pg2173-normal-publication-v1','genuineParentNormalWarningOriginal=true','currentManagerGc=true','finiteOrdinaryPublication=true','0.1.0-PG2126','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','unitBytesInodesConfigurationUnchanged','oldNativeNotAppliedToNewSource']:self.assertIn(text,raw)
        self.assertIn("after['unitFilesActual']==old_after['unitFilesActual']",raw)
        self.assertIn("'unitExchangeAndReload':False",raw)
        self.assertIn("not(publication/'daemon-reload-reserved.private').exists()",raw)
        self.assertNotIn('pidfd_send_signal',raw)


if __name__=='__main__':unittest.main()
