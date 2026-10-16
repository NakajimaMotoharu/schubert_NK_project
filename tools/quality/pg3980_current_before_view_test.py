import inspect
import unittest
from pyflakes.api import check
import pg3980_current_before_view as view


class CurrentDataOnlyView(unittest.TestCase):
    def test_complete_new_schema_and_no_runtime_authority(self):
        raw = 'PROOF={}\n' + view.GUEST; self.assertEqual(0, check(raw, '<current before data only>')); compile(raw, '<current before data only>', 'exec')
        for expected in ['pg3902-native-stop-v1', 'pg3980-current-7fff-before-view-v1', 'native46Preserved', "'nativePhysicalFilesPreserved':46", 'sealedImageFields', 'dataOnlyNotRuntimeAuthority', "if k!='native'"]:
            self.assertIn(expected, raw)
        for old in ['pg3662-native-stop-v1', 'native34Preserved', 'daemon-reload', 'PG3976']:
            self.assertNotIn(old, raw)
        self.assertIn('pg3978-current-preservation-readonly-v1', view.role_text(inspect.getsource(view.previous.main)))


if __name__ == '__main__': unittest.main()
