import copy
import unittest
from pyflakes.api import checkPath
import pg6446_morning_sequence_capacity as subject


class Definition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        jar = subject.W/'pg6440-morning-diagnostic-green-v1/source/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
        raw = subject.subprocess.check_output([str(subject.TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), subject.CLS], text=True)
        cls.blocks = subject.methods(raw)

    def test_actual_old_gap_and_pinned_jdk_preallocation_semantics(self):
        value = subject.analyze(self.blocks, False)
        self.assertEqual(0, value['capacity'])
        self.assertEqual(2, value['maximumAdds'])
        self.assertTrue(value['registeredOnlyAfterFirstGrowRisk'])
        self.assertFalse(value['nativeOwnershipProven'])
        self.assertEqual(0, subject.jdk_proof()['defaultArrayLength'])
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_noarg_or_added_launch_or_external_alias_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, 'capacity2'):
            subject.analyze(self.blocks, True)
        key = next(k for k in self.blocks if ' void sequence(' in k)
        bad = copy.deepcopy(self.blocks); bad[key] = bad[key].replace('ArrayList.add:', 'ArrayList.addSkipped:', 1)
        with self.assertRaises(ValueError):
            subject.analyze(bad, False)
        bad = copy.deepcopy(self.blocks); bad[key] += '\n  120: putstatic #CP // Field escaped:Ljava/lang/Object;\n'
        with self.assertRaisesRegex(ValueError, 'external alias'):
            subject.analyze(bad, False)


if __name__ == '__main__':
    unittest.main()
