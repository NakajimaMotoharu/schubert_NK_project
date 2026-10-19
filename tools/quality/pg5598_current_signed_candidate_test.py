import copy
import hashlib
import json
from pathlib import Path
import symtable
import struct
import tempfile
import unittest
import zipfile
from pyflakes.api import checkPath
import pg5598_current_signed_candidate as entry


class CurrentHostCandidate(unittest.TestCase):
    def maps(self):
        old=json.loads((entry.W/'pg5416-ownership-whole-qualified-v2/manifest.safe.json').read_bytes())['result']['allPhysicalMainSha256']
        new=json.loads((entry.W/'pg5566-private-monitor-green-v3/manifest.safe.json').read_bytes())['physicalMain']['sha256']
        return old,new

    def test_exact12_raw_changes_include_all_five_debug_changes(self):
        old,new=self.maps();value=entry.delta(entry.grouped(old),entry.grouped(new),old,new)
        self.assertEqual((len(value['modified']),value['unchangedOldClasses'],value['debugOnlyPhysicalChanges']),(12,1652,5))
        bad=dict(new);bad[next(k for k in bad if k not in entry.CHANGED)]='0'*64
        with self.assertRaises(ValueError):entry.delta(entry.grouped(old),entry.grouped(bad),old,bad)
        with self.assertRaises(ValueError):entry.delta(entry.grouped(old),entry.grouped(old),old,old)

    def test_complete_frozen_engine_namespace_and_new_only_release_names(self):
        raw=entry.main_source();compile(raw,'<current candidate>','exec')
        for text in('pg5598-candidate-build-v1.safe.json','0.1.0-PG5598',"data['release'] == '0.1.0-PG5430'",entry.SOURCE,
          'pg5574-monitor-whole-qualified-v1',"'addedClasses': 0","'removedClasses': 0","'oldPhysicalMain': 1664","'semanticChangedClasses': 7","'debugOnlyChangedClasses': 5","'deploymentAuthority': False"):
            self.assertIn(text,raw)
        self.assertIn('openssl',raw);self.assertNotIn('systemctl',raw);self.assertNotIn('stage-place',raw)
        needed={s.get_name()for s in symtable.symtable(raw,'<candidate>','exec').get_children()[0].get_symbols()if s.is_global()and s.is_referenced()}
        scope={**vars(entry.prior),**vars(entry),'PRODUCTION':entry.SOURCE,'SIGNED_DELTA':None}
        self.assertFalse(needed-set(scope)-set(dir(__import__('builtins'))))

    def test_all_six_actual_containers_only_exact_class_and_test_pom_differences(self):
        old,new=self.maps();a,b=entry.grouped(old),entry.grouped(new)
        jars={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar',**{m:'api/lib/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'for m in('protocol','storage','bootstrap')}}
        for module,path in jars.items():
            candidate=entry.W/'pg5566-private-monitor-green-v3/source'/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
            digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
            value=entry.verify_candidate_container(entry.OLD/path,candidate,a[module],b[module],module,digest)
            self.assertTrue(value['allMembersValidated'])
            if module=='batch':
                with self.assertRaises(ValueError):entry.verify_candidate_container(entry.OLD/path,candidate,a[module],b[module],'api',digest)
            with self.assertRaises(ValueError):entry.verify_candidate_container(entry.OLD/path,candidate,a[module],b[module],module,'0'*64)
            with tempfile.TemporaryDirectory(prefix='pgpt-current-jar-negative-')as folder:
                foreign=Path(folder)/'foreign.jar';foreign.write_bytes(candidate.read_bytes()+b'FOREIGN')
                with self.assertRaises(ValueError):entry.verify_candidate_container(entry.OLD/path,foreign,a[module],b[module],module,digest)
                with self.assertRaises(ValueError):entry.verify_candidate_container(entry.OLD/path,foreign,a[module],b[module],module,hashlib.sha256(foreign.read_bytes()).hexdigest())
                raw=bytearray(candidate.read_bytes())
                with zipfile.ZipFile(candidate)as archive:
                    cursor=archive.start_dir
                    for item in archive.infolist():
                        if not item.is_dir():
                            struct.pack_into('<I',raw,cursor+38,0o100755<<16);break
                        n,e,c=struct.unpack_from('<HHH',raw,cursor+28);cursor+=46+n+e+c
                foreign.write_bytes(raw)
                with self.assertRaises(ValueError):entry.verify_candidate_container(entry.OLD/path,foreign,a[module],b[module],module,hashlib.sha256(raw).hexdigest())
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_unqualified_or_wrong_source_gate_refused(self):
        with self.assertRaises(ValueError):entry.validate_gate({'actualExit':1},entry.SOURCE)
        outer=json.loads((entry.W/'pg5416-ownership-whole-qualified-v2/manifest.safe.json').read_bytes())
        with self.assertRaises(ValueError):entry.validate_gate(copy.deepcopy(outer),entry.SOURCE)


if __name__=='__main__':unittest.main()
