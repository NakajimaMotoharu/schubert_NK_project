"""Complete new-only targets retain old successful a9 capsule and reject failed2918 input."""
import unittest
import pg2932_format_fixed_full_qualified as full
import pg2934_format_fixed_same_native as native


class CorrectedSource(unittest.TestCase):
    def test_corrected_full_and_native_targets(self):
        a=full.server();b=native.server();c=native.source()
        for text in [a,b]:
            self.assertIn('PG2930',text);self.assertNotIn('PG2918',text);self.assertIn('3684',text)
        self.assertIn('source-full-PG2798',b)
        self.assertIn('member_counts(oldmembers,newmembers)',b)
        self.assertIn('PG2934-native-v1',b)
        self.assertIn('pg2932-format-fixed-full-qualified-v1',c)
        self.assertIn('pg2934-format-fixed-same-native-qualified-v1',c)
        self.assertIn('pg2908-network-current-native-qualified-v2',c)
        self.assertNotIn('subprocess.run(SSH',c)


if __name__=='__main__':unittest.main()
