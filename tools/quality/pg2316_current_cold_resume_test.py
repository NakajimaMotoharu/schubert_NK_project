import hashlib
import stat
import types
import unittest
from copy import deepcopy
from pg2316_current_cold_resume_sources import sources,CLASS


class ColdContract(unittest.TestCase):
    def test_whole_sources_and_exact_cold_profile_not_existing_directory(self):
        values=sources()
        self.assertEqual(20,len(values))
        self.assertIn('os.mkdir(UNIT,0o700,dir_fd=root)',values['pg2316_runtime_writer.py'])
        self.assertIn('os.listdir(root)==[UNIT]',values['pg2316_runtime_writer.py'])
        self.assertIn('State.ISSUED',values[CLASS+'.java'])
        self.assertIn('runtime_before[str(runtime_root)]',values['pg2316_native_refs.py'])
        self.assertNotIn('runtime_before[str(runtime_directory)]',values['pg2316_native_refs.py'])
        for name,body in values.items():self.assertFalse('pg2304'in body,name)

    def test_independent_full_runtime_vector_all_fields_and_extra_rejected(self):
        module=types.ModuleType('coldcontract');exec(sources()['pg2316_resume_contract.py'],module.__dict__)
        def row(values,digest=None):return {'metadata':values,'sha256':digest}
        data=b'[Service]\nExecStart=fixed\n'
        before={module.RUNTIME:row([28,101,0,0,stat.S_IFDIR|0o755,2,40,50,50])}
        actual={module.RUNTIME:row([28,101,0,0,stat.S_IFDIR|0o755,3,60,110,110]),module.DIRECTORY:row([28,102,0,0,stat.S_IFDIR|0o755,2,60,115,115]),module.TARGET:row([28,103,0,0,stat.S_IFREG|0o644,1,len(data),115,115],hashlib.sha256(data).hexdigest())}
        self.assertTrue(module.runtime_tree(before,actual,data,100,120))
        cases=[]
        for name in actual:
            for index in [0,1,2,3,4,5,7,8]:
                changed=deepcopy(actual);changed[name]['metadata'][index]=1 if index in [2,3]else 0;cases.append(changed)
        for key in actual:
            changed=deepcopy(actual);changed[key]['sha256']='foreign';cases.append(changed)
        changed=deepcopy(actual);changed['extra']=row([28,104,0,0,stat.S_IFREG|0o644,1,0,115,115]);cases.append(changed)
        for changed in cases:self.assertFalse(module.runtime_tree(before,changed,data,100,120))
        self.assertFalse(module.runtime_tree(None,actual,data,100,120))
        self.assertFalse(module.runtime_tree(before,actual,None,100,120))
        self.assertFalse(module.runtime_tree(before,actual,data,121,120))


if __name__=='__main__':unittest.main()
