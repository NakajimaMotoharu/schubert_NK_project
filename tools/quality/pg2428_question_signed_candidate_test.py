import tempfile
import unittest
import zipfile
from pathlib import Path
from pg2428_question_signed_candidate import verify_container,main_source,W


class Container(unittest.TestCase):
    def test_actual_partial_qualified_jars_all_six_metadata_and_payload_contract(self):
        from pg2406_question_signed_candidate import OLD,FROZEN,RESOURCE
        paths={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar',
               'protocol':'api/lib/schubert-nk-protocol-0.1.0-SNAPSHOT.jar',
               'storage':'api/lib/schubert-nk-storage-0.1.0-SNAPSHOT.jar',
               'bootstrap':'api/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'}
        for m,p in paths.items():
            new=next(FROZEN.rglob('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'))
            verify_container(OLD/p,new,{RESOURCE} if m=='web' else set())
        with self.assertRaises(ValueError):
            verify_container(OLD/'web/web.jar',next(FROZEN.rglob('schubert-nk-web-0.1.0-SNAPSHOT.jar')))

    def test_independent_timestamps_foreign_metadata_payload_and_trailing_bytes(self):
        with tempfile.TemporaryDirectory(prefix='pg2428-zip-') as temp:
            root=Path(temp);paths=[]
            for index in range(5):
                p=root/str(index);paths.append(p)
                info=zipfile.ZipInfo('literal',(2020+index,1,1,0,0,0));info.external_attr=0o600<<16
                if index==2:info.comment=b'foreign'
                with zipfile.ZipFile(p,'w') as z:z.writestr(info,b'changed' if index==3 else b'fixed')
            paths[4].write_bytes(paths[4].read_bytes()+b'foreign')
            verify_container(paths[0],paths[1])
            for p in paths[2:]:
                with self.assertRaises(ValueError):verify_container(paths[0],p)
            verify_container(paths[0],paths[3],{'literal'})

    def test_new_only_failed_namespace_untouched_and_bounded_artifact_guard(self):
        raw=main_source()
        self.assertIn('PG2428',raw);self.assertIn('pg2428-candidate-build-v1',raw)
        self.assertNotIn('pg2406-candidate-build-v1',raw)
        self.assertIn('changed <= allowed',raw)
        self.assertIn("{'VERSION', 'web/web.jar'} <= changed",raw)
        self.assertTrue((W/'pg2406-release-v1').is_dir())


if __name__=='__main__':unittest.main()
