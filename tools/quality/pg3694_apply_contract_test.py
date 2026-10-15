"""No derived source patch may silently change one of the seventy generated members."""
import unittest
from pg3694_hygiene_candidate_apply import verify_generated


class Generated(unittest.TestCase):
    def test_whole_relative_paths_missing_or_changed_generated_member_refused(self):
        names={'PayloadTypeCatalog.java',*[f'admin/Record{i:02d}.java'for i in range(69)]}
        prefix='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/'
        originals={prefix+n:'fixed'for n in names}
        verify_generated(names,{prefix+'LayoutFieldCatalog.java':{}},originals)
        with self.assertRaises(ValueError):verify_generated(names,{prefix+'admin/Record00.java':{}},originals)
        with self.assertRaises(ValueError):verify_generated(names,{},dict(list(originals.items())[:-1]))
        with self.assertRaises(ValueError):verify_generated(names-{'PayloadTypeCatalog.java'},{},originals)


if __name__=='__main__':unittest.main()
