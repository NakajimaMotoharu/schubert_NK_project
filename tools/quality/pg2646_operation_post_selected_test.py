import unittest
from pyflakes.api import check
from pg2646_operation_post_web_selected import SERVER, CLASSES, ROOT


class OperationSelected(unittest.TestCase):
    def test_required_existing_consumer_classes_and_namespace(self):
        self.assertEqual(5, len(set(CLASSES)))
        for name in CLASSES:
            self.assertEqual(1, len(list((ROOT / 'src/schubert-nk-web/src/test/java').rglob(name + '.java'))))
        self.assertEqual(0, check('INPUT={}\n' + SERVER, '<whole candidate Web namespace>'))
        for marker in ['observed==set(INPUT[\'classes\'])', "'# tests 6'", 'NodeThreeCounters100', 'nativeNotAccepted', 'wholeRegressionNotAccepted']:
            self.assertIn(marker, SERVER)


if __name__ == '__main__':
    unittest.main()
