"""Current readonly full19/source/row/Ref/seal guards, literal oracle."""
import unittest
from pg646_completed_baseline import PAYLOAD


class Binding(unittest.TestCase):
    def test_readonly_current_completed_capture(self):
        compile(PAYLOAD, '<current completed capture>', 'exec')
        for text in ('011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c',
                     '293d218b06454bd1a8ff350bb93de2d5', 'pg635-once-resume.conf', 'pg646-completed-baseline-v1',
                     'len(v)==19', 'len(set(paths))==19', "len(rows['schubert.batch_runs'])==504",
                     'before==capture()', 'manager.RefUnit(u)', 'manager.UnrefUnit(u)', 'bus.close()',
                     "'operationAuthority':False", 'repeatable read read only'):
            self.assertIn(text, PAYLOAD)
        for text in ("['systemctl','start'", "['systemctl','stop'", 'daemon-reload', '.unlink(', '.rename(', 'update schubert'):
            self.assertNotIn(text, PAYLOAD)


if __name__ == '__main__': unittest.main()
