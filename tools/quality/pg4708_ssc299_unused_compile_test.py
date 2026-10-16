"""Current not candidate ABI, fixture generation only, no guest action."""
import unittest
from unittest.mock import patch
from pyflakes.api import checkPath
import pg4708_ssc299_unused_compile as tool


class CompileNormalUnused(unittest.TestCase):
    def test_closed_names_current_jar_and_six_actual_negative_phases(self):
        with patch.object(tool.role,'candidate_bom',return_value='f'*64):raw=tool.compiler()
        for value in ['pg4702-candidate-build-v1.safe.json','pg4702-release-v1','pg4702-manifest-v1.sig',
                      'pg4704-current-preservation-readonly-v1','pg4654-frozen-v1.safe.json',
                      'pg4652-current-owned-tools-v1',"old = W / 'pg4432-release-v1'",'Pg4706UnusedStage',
                      'Pg4706NativeArgumentTest','Pg4706OriginalTupleTest','Pg4706CurrentIdentityTest','Pg4706InputBoundaryTest']:
            if value=='Pg4706UnusedStage':continue # class is selected from all emitted .java, not hard-coded
            self.assertIn(value,raw)
        for wrong in ['pg3982','pg3976','pg3878','pg3876','systemctl','daemon-reload']:
            self.assertNotIn(wrong,raw)
        self.assertIn("'-Xlint:all', '-Werror'",raw)
        self.assertIn("'argument'",raw);self.assertIn("'label'",raw)
        self.assertEqual(0,checkPath(tool.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
