"""New-source XML gap binding, frozen host/hash/counter exclusions unchanged."""
import unittest
from pg645_native_gap import code


class Binding(unittest.TestCase):
    def test_new_gap_source(self):
        value = code(); compile(value, '<current XML>', 'exec')
        for literal in ('pg644-current-eight-native-v1', 'pg645-current-native-gap-v1',
                        '36fe7a0b938489d61d17d49c1c30a6fbbef699d5', 'pg630-retention-factory-six-host-v1',
                        'NativeCoverageXml471', 'len(data) == 14', "record['hostExecHashes']"):
            self.assertIn(literal, value)
        self.assertNotIn('23b14a44', value)


if __name__ == '__main__': unittest.main()
