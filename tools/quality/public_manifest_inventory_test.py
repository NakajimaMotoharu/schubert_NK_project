"""PT-TOOLMAN001..009: independent fixed vectors and original early-open regression."""
import json
from pathlib import Path
import tempfile
import unittest

from public_manifest_inventory import inventory, validate

ABC = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


class FileManifestContract(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='pgpt-public-manifest-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'abc.txt').write_bytes(b'abc')

    def test_inventory_hashes_fixed_abc_without_future_manifest(self):
        self.assertEqual({'abc.txt': ABC}, inventory(self.root))

    def test_open_empty_manifest_is_never_its_own_artifact(self):
        with (self.root / 'manifest.json').open('x'):
            self.assertEqual({'abc.txt': ABC}, inventory(self.root))

    def test_written_manifest_keeps_fixed_file_inventory_valid(self):
        (self.root / 'manifest.json').write_text(json.dumps({'files': {'abc.txt': ABC}}))
        self.assertTrue(validate(self.root, {'abc.txt': ABC}))
        self.assertEqual({'abc.txt': ABC}, inventory(self.root))

    def test_self_reference_rejected_even_if_current_empty_hash_matches(self):
        (self.root / 'manifest.json').write_bytes(b'')
        with self.assertRaises(ValueError):
            validate(self.root, {'manifest.json': EMPTY})

    def test_missing_file_is_not_accepted(self):
        with self.assertRaises(ValueError):
            validate(self.root, {'missing.txt': ABC})

    def test_changed_file_is_not_accepted(self):
        (self.root / 'abc.txt').write_bytes(b'abd')
        with self.assertRaises(ValueError):
            validate(self.root, {'abc.txt': ABC})

    def test_malformed_hash_is_not_accepted(self):
        for bad in ['0', ABC.upper(), None]:
            with self.subTest(value=bad), self.assertRaises(ValueError):
                validate(self.root, {'abc.txt': bad})

    def test_absolute_parent_and_noncanonical_paths_are_rejected(self):
        for bad in [str(self.root / 'abc.txt'), '../abc.txt', './abc.txt']:
            with self.subTest(value=bad), self.assertRaises(ValueError):
                validate(self.root, {bad: ABC})

    def test_symlink_cannot_substitute_fixed_public_artifact(self):
        (self.root / 'alias.txt').symlink_to(self.root / 'abc.txt')
        with self.assertRaises(ValueError):
            inventory(self.root)
        with self.assertRaises(ValueError):
            validate(self.root, {'alias.txt': ABC})


if __name__ == '__main__':
    unittest.main()
