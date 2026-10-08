"""Independent literal eight-stream source/session/window/NoMatch guards."""
import unittest
from pg644_native_counter import code


class Binding(unittest.TestCase):
    def test_current_only_and_all_original_quality_guards(self):
        hashes = {str(i)+'.exec': str(i+1)*64 for i in range(8)}
        value = code(hashes); compile(value, '<fixed current collector>', 'exec')
        for item in ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', 'pg642-native-stop-v1',
                     'pg643-terminal-final-v2', 'pg630-retention-factory-six-host-v1',
                     'pg644-current-eight-native-v1', "tests']==3468", '104759573609', '103062293730',
                     "NativeSessions571", 'len(info)==1', "v['classByteMismatch']==0", "v['formal']is False",
                     'oldNativeStreamsNotImported', "git','diff','--name-only',SOURCE"):
            # Existing collector records historicalNativeNotImported (not a frozen host field).
            if item == 'oldNativeStreamsNotImported': item = 'historicalNativeNotImported'
            self.assertIn(item, value)
        for old in ('23b14a44', 'pg599', '3457', 'pg611-native', 'pg614-current-eight', 'a7e90f29'):
            self.assertNotIn(old, value)


if __name__ == '__main__': unittest.main()
