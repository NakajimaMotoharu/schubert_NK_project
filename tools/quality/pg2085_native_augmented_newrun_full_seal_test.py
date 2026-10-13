"""Exact native augmentation and actual terminal/row guard composition, no unknown schema."""
import unittest
from pg2085_native_augmented_newrun_full_seal import before_shape,payload,entry,SLOT


class Schema(unittest.TestCase):
    def test_exact_eleven_fields_and_finite_native(self):
        fields=['backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'];before={k:{}for k in fields};before['native']={'independent':{'sha':'literal'}}
        self.assertTrue(before_shape(before))
        for bad in [None,{},dict(before,native={}),dict(before,native=None),dict(before,unknown={}),{k:v for k,v in before.items()if k!='rows'}]:self.assertFalse(before_shape(bad))

    def test_actual_whole_entry_and_guards(self):
        binding={'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'2c37fef2a2ff48e7b6a05cfc23f84c19','job':'204748','start':113070840714,'run':'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','cutoff':'2026-10-13T03:08:18.452473Z','activation':'9026b2ab-bb42-49cd-a2bd-4c661049dce3','rootPid':588342}
        raw=payload(binding)
        for marker in ['require(before_shape(before))','796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05','manager.UnrefUnit(unit)','current==capture()','newBackupSteps']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(SLOT,entry().__globals__['SLOT']);self.assertIs(payload,entry().__globals__['payload'])


if __name__=='__main__':unittest.main()
