import ast
import unittest
from pg1150_native_five_compile_v2 import source,helper_input


class InputOutputTest(unittest.TestCase):
    def test_immutable_inputs_disjoint_fresh_fixture_family(self):
        for name in ['BackupPublicationFixture','BackupArtifactFixture','BackupManifestFixture']:
            for suffix in ['.class','$1.class','$1$1.class','$Nested.class']:
                self.assertFalse(helper_input('dev/codex/schubert/nk/batch/file/'+name+suffix))
        for name in ['Pg387TrustedDeployment.class','dev/codex/schubert/nk/batch/file/Pg1144SingleApiIntent.class']:
            self.assertTrue(helper_input(name))
        self.assertFalse(helper_input('BackupArtifactFixture.java'))
        text=source();ast.parse(text)
        self.assertTrue('pg1150-native-five-frozen-v2'in text)
        self.assertTrue("text.replace('pg1148-native-five-tools-v1','pg1148-native-five-tools-v2')"in text)


if __name__=='__main__':unittest.main()
