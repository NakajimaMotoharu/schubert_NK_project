"""Independent literal archive fixture; no extraction/guest writes/PT credit."""
import copy
import tarfile
import unittest
from pg601_stage_contract import check_members


class ArchiveContract(unittest.TestCase):
    def fixture(self):
        rows = []
        for name, kind in (('VERSION', tarfile.REGTYPE), ('api', tarfile.DIRTYPE),
                           ('api/api.jar', tarfile.REGTYPE)):
            row = tarfile.TarInfo(name); row.type = kind; rows.append(row)
        return rows

    def test_exact_regular_files_and_directories(self):
        check_members(self.fixture(), {'VERSION', 'api/api.jar'})

    def test_malformed_duplicate_foreign_missing_and_link_types(self):
        for name in ('', '/etc/key', '../key', 'api/../key', 'api//key', './VERSION',
                     'api\\key', 'foreign', 'api/api.jar'):
            rows = self.fixture(); rows[0].name = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                check_members(rows, {'VERSION', 'api/api.jar'})
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE):
            rows = self.fixture(); rows[0].type = kind
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                check_members(rows, {'VERSION', 'api/api.jar'})
        for rows in (self.fixture()[:-1], self.fixture() + [copy.copy(self.fixture()[0])]):
            with self.assertRaises(ValueError): check_members(rows, {'VERSION', 'api/api.jar'})
        for value in (None, [], set()):
            with self.assertRaises(ValueError): check_members([], value)


if __name__ == '__main__': unittest.main()
