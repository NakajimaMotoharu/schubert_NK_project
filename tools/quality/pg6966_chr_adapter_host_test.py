import io
import tarfile
import tempfile
import unittest
from pathlib import Path

import pg6966_chr_adapter_host as p
import pg6968_chr_adapter_host_v2 as v2


class ChrHostRunGuardTest(unittest.TestCase):
    def test_v2_exact_common_scope_no_native_format(self):
        v2.validate()
        expected = [f'src/main/java/dev/codex/schubert/characterization/{s}.java'
                    for s in ('ArtifactComparator','GateCli','GateContractValidator','TargetAdapter')]
        expected += [f'tests/java/dev/codex/schubert/characterization/{s}.java'
                     for s in ('ArtifactComparatorTest','GateCliTest','GateContractTest',
                               'GateContractValidatorNegativeTest','TargetAdapterTest')]
        self.assertEqual(expected,list(v2.FILES))

    def test_fixed_five_host_suites_no_current_or_native(self):
        self.assertEqual(('ArtifactComparatorTest','GateCliTest','GateContractTest',
                          'GateContractValidatorNegativeTest','TargetAdapterTest'),p.SELECTED)

    def test_extract_refuses_traversal_symlink_and_absolute_before_any_write(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for index,name in enumerate(('../escape','/absolute','link')):
                archive = root/f'{index}.tar'
                with tarfile.open(archive,'w') as stream:
                    member = tarfile.TarInfo(name)
                    if name == 'link':member.type=tarfile.SYMTYPE;member.linkname='outside'
                    else:member.size=1
                    stream.addfile(member,io.BytesIO(b'x'))
                target = root/f'out{index}';target.mkdir()
                with self.assertRaises(ValueError):p.safe_extract(archive,target)
                self.assertEqual([],list(target.iterdir()))


if __name__ == '__main__':
    unittest.main()
