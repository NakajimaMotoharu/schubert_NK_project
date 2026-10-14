import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile
from pg2652_operation_resource_container import verify


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ExactAddedContainer(unittest.TestCase):
    def test_changed_added_and_rejected_foreign_payload_or_metadata(self):
        old = {'unchanged.txt': b'fixed', 'template.html': b'old'}
        new = {'unchanged.txt': b'fixed', 'template.html': b'new', 'script.js': b'added'}
        changed = {'template.html': (sha(b'old'), sha(b'new'))}; added = {'script.js': sha(b'added')}
        with tempfile.TemporaryDirectory(prefix='pg2652-container-fixture-') as directory:
            root=Path(directory)
            def write(name, rows, comment=b'', extra=False):
                p=root/name
                with zipfile.ZipFile(p,'w') as z:
                    z.comment=comment
                    for n,raw in rows.items():
                        info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                        if extra:info.extra=b'\xfe\xca\x00\x00'
                        z.writestr(info,raw)
                return p
            a=write('a.jar',old);b=write('b.jar',new)
            self.assertEqual({'changedResources':1,'addedResources':1,'MainChanged':0},verify(a,b,changed,added))
            for label,rows,comment,extra in [
                ('foreign', {**new,'unknown.txt':b'foreign'},b'',False),
                ('changed',{**new,'unchanged.txt':b'foreign'},b'',False),
                ('missing',{k:v for k,v in new.items()if k!='script.js'},b'',False),
                ('wire',{**new,'script.js':b'foreign'},b'',False),
                ('comment',new,b'foreign',False),('extra',new,b'',True),
                ('class',{**new,'Unexpected.class':b'foreign'},b'',False)]:
                with self.subTest(label=label):
                    with self.assertRaises(ValueError):verify(a,write(label+'.jar',rows,comment,extra),changed,added)


if __name__=='__main__':unittest.main()
