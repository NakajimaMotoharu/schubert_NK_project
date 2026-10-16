"""Literal ZIP vectors independent of the container contract under test."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile
from pg4426_relocated_jar_contract import records, verify_relocated_container


class RelocatedContainer(unittest.TestCase):
    def make(self, path, entries):
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, payload in entries:
                archive.writestr(name, payload)
        return path

    def test_exact_relocation_and_new_enum_keeps_resource_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            before = self.make(base / 'before.jar', [('old/', b''), ('old/Reader.class', b'literal old'), ('same.txt', b'fixed')])
            after = self.make(base / 'after.jar', [('new/', b''), ('new/Reader.class', b'literal new'), ('new/Reader$Service.class', b'enum'), ('same.txt', b'fixed')])
            old = {'old/Reader.class': hashlib.sha256(b'literal old').hexdigest()}
            new = {'new/Reader.class': hashlib.sha256(b'literal new').hexdigest(), 'new/Reader$Service.class': hashlib.sha256(b'enum').hexdigest()}
            result = verify_relocated_container(before, after, old, new)
            self.assertEqual(['new/', 'new/Reader$Service.class', 'new/Reader.class'], result['added'])
            self.assertEqual(['old/', 'old/Reader.class'], result['removed'])
            self.assertEqual(2, result['physicalClasses'])
            changed = self.make(base / 'changed.jar', [('new/', b''), ('new/Reader.class', b'literal new'), ('new/Reader$Service.class', b'enum'), ('same.txt', b'changed')])
            with self.assertRaises(ValueError): verify_relocated_container(before, changed, old, new)
            with self.assertRaises(ValueError): verify_relocated_container(before, after, old, {'new/Reader.class': '0' * 64})

    def test_prefix_trailer_duplicate_foreign_metadata_and_unregistered_directory_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); normal = self.make(base / 'normal.jar', [('one.class', b'fixed')])
            raw = normal.read_bytes()
            for index, bad in enumerate([b'foreign' + raw, raw + b'foreign', raw.replace(b'PK\x03\x04', b'BK\x03\x04', 1)]):
                path = base / ('bad' + str(index)); path.write_bytes(bad)
                with self.assertRaises((ValueError, zipfile.BadZipFile)): records(path)
            extra = self.make(base / 'extra.jar', [('unused/', b''), ('one.class', b'fixed')])
            classes = {'one.class': hashlib.sha256(b'fixed').hexdigest()}
            with self.assertRaises(ValueError): verify_relocated_container(normal, extra, classes, classes)
            foreign = base / 'foreign.jar'
            with zipfile.ZipFile(foreign, 'w') as archive:
                info = zipfile.ZipInfo('one.class'); info.extra = b'\x01\x00\x00\x00'; archive.writestr(info, b'fixed')
            with self.assertRaises(ValueError): records(foreign)


if __name__ == '__main__':
    unittest.main()
