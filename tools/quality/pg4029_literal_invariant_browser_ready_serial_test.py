import inspect
from pathlib import Path
import tempfile
import unittest
from pg1674_critical_management_gate import management_gate
import pg4029_literal_invariant_browser_ready_serial as ready
import pg4012_literal_invariant_current_observer as observer
import pg4016_literal_invariant_current_noargs_once as once


class SerialManagement(unittest.TestCase):
    def test_actual_gate_conflict_has_no_mutation_and_releases_for_next_owner(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-serial-gate-test-') as folder:
            path = Path(folder) / 'private.lock'
            with management_gate(path):
                before = path.stat(); body = path.read_bytes()
                with self.assertRaises(BlockingIOError):
                    with management_gate(path): self.fail('second operation entered held gate')
                after = path.stat()
                self.assertEqual((before.st_dev, before.st_ino, before.st_mode, before.st_size), (after.st_dev, after.st_ino, after.st_mode, after.st_size))
                self.assertEqual(body, path.read_bytes())
            with management_gate(path): self.assertEqual(before.st_ino, path.stat().st_ino)

    def test_indirect_gate_is_classified_and_new_slot_not_old_partial(self):
        raw = inspect.getsource(ready.previous.previous.previous.main)
        self.assertIn("if i==len(commands):", raw); self.assertIn('management_gate', raw)
        self.assertIn("if sys.argv[1:] == ['stage']", inspect.getsource(observer.main))
        self.assertIn('management_gate', inspect.getsource(once.previous.transport.main))
        self.assertNotEqual(ready.SLOT, ready.previous.SLOT)
        self.assertIn('tools/quality/pg4029_literal_invariant_browser_ready_serial.py', ready.PINNED)
        self.assertNotIn('tools/quality/pg4014_literal_invariant_browser_ready.py', ready.PINNED)
        self.assertIs(once.require_ready, ready.require_ready)


if __name__ == '__main__': unittest.main()
