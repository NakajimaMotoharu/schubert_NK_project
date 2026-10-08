"""Exact approved-only rebinding, preserve driver/oracle and baseline guards."""
import unittest
from pg641_a01_current import code, guard


class Binding(unittest.TestCase):
    def test_current_source_and_same_parent_guard(self):
        source = code(); compile(source, '<fixed capture>', 'exec')
        for text in ('0.1.0-PG631', 'pg637-fresh-resume-v2', 'pg638-watch-private-v1',
                     'pg638-observer-v1', 'pg641-chr-a01-native-v1', 'PG641-native-a01-v1',
                     'NativeNkA01Capture', "baseline_sha=hashlib.sha256(baseline.read_bytes()).hexdigest()",
                     "'approvedDIF001TitleOnly':True", "hashlib.sha256(baseline.read_bytes()).hexdigest()==baseline_sha"):
            self.assertIn(text, source)
        self.assertIn('1800000000', guard())
        self.assertIn('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', source)
        self.assertNotIn('23b14a44', source)
        self.assertNotIn("'systemctl','start'", source)


if __name__ == '__main__': unittest.main()
