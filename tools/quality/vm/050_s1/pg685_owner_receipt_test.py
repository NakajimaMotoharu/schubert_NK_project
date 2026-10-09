"""Actual sealed owner and literal current PID1 receipt, host-only tests."""
import types
import unittest
from pathlib import Path
import pg685_sources as profile

R = Path(__file__).parent


def suite():
    owner = profile.bind((R/'pg624_owner_namespace_test.py').read_text())
    receipt = profile.bind((R/'pg611_parent_receipt_test.py').read_text())
    receipt = receipt.replace('from pg611_parent_receipt import completed',
                              'from pg685_parent_receipt import completed')
    receipt = receipt.replace('1791475059000000', '1791496991000000')
    receipt = receipt.replace("b'3a53b979',b'4a53b979'", "b'601297d0',b'701297d0'")
    receipt = receipt.replace("'86264628080','88064628082'", "'107901545406','109701545408'")
    result = unittest.TestSuite()
    for name, raw, cls in (('current_owner', owner, 'Test'), ('current_receipt', receipt, 'ReceiptTest')):
        mod = types.ModuleType(name); mod.__file__ = str(R/(name+'.py'))
        exec(compile(raw, '<literal current owner/receipt oracle>', 'exec'), mod.__dict__)
        result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(mod, cls)))
    return result


if __name__ == '__main__':
    actual = unittest.TextTestRunner().run(suite())
    assert actual.testsRun == 4
    raise SystemExit(0 if actual.wasSuccessful() else 1)
