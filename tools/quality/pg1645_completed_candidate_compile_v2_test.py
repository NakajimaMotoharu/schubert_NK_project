"""Independent nested/same-name/flat inventory and canonical path vectors."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import pg1645_completed_candidate_compile_v2 as p


class NestedCompilerTest(unittest.TestCase):
    def test_literal_nested_paths_and_same_name_are_not_collapsed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for n, b in [('one/Same.class', b'A'), ('two/Same.class', b'B'), ('Flat.class', b'C')]:
                path = root / n
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b)
            self.assertEqual({'one/Same.class': hashlib.sha256(b'A').hexdigest(), 'two/Same.class': hashlib.sha256(b'B').hexdigest(), 'Flat.class': hashlib.sha256(b'C').hexdigest()}, p.inventory(root))
        for n in ['one/Same.class', 'Flat.class']:
            self.assertEqual(n, p.canonical_relative(n))
        for n in ['', '../x', '/x', 'one/../x', 'one//x', 'one/./x', 'one\\x', None, True]:
            with self.assertRaises(ValueError):
                p.canonical_relative(n)


if __name__ == '__main__':
    unittest.main()
