"""Independent exact replacement/retained bytes/unknown paths and source safety."""
import copy
import unittest
from pg1622_retired_backup_readonly_preservation import selected_retired,SERVER

class RetiredBackupScopeTest(unittest.TestCase):
    def test_exact_seven_to_seven_only_one_old_folder_four_files(self):
        root='/srv/schubert-nk/backup';names=['MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age']
        original={'metadata':[72,13,992,977,16832,9,4096,10,10],'sha256':None}
        before={root:copy.deepcopy(original)};folders=[]
        for i in range(7):
            p=root+'/20261011-12000'+str(i)+'-fixture'+str(i);folders.append(p);before[p]=copy.deepcopy(original)
            for n in names:before[p+'/'+n]={'metadata':[72,100+i,0,0,33152,1,20,10,10],'sha256':'a'*64}
        after={p:copy.deepcopy(v)for p,v in before.items()if p!=folders[0]and not p.startswith(folders[0]+'/')}
        new=root+'/20261012-152322-0be226b1-bbb7-43d3-aa9e-59d0bda70f9a';after[new]=copy.deepcopy(original)
        for n in names:after[new+'/'+n]={'metadata':[72,200,0,0,33152,1,20,20,20],'sha256':'b'*64}
        value=selected_retired(before,after);self.assertEqual(value['folder'],folders[0]);self.assertEqual(len(value['entries']),5);self.assertEqual(len(value['retainedCompleteFolders']),7)
        for changed in [None,{},dict(after,unknown={}),{p:v for p,v in after.items()if not p.endswith('config.tar')},dict(after,**{folders[1]+'/MANIFEST.json':{'changed':True}}),dict(after,**{root:{'metadata':[72,13,0,977,16832,9,4096,10,10],'sha256':None}})]:
            with self.assertRaises(ValueError):selected_retired(before,changed)
        wrong_before=copy.deepcopy(before);wrong_before[root]['metadata'][5]=10
        with self.assertRaises(ValueError):selected_retired(wrong_before,after)
        for literal in ["image.fh.mode=='rb'","metadata==wanted['metadata'][1:]","h.hexdigest()==wanted['sha256']","retainedSevenAndOldestRetiredVerified","'schubert_nk.dump','config.tar','credentials.tar.age'",'finally:image.fh.close()']:
            self.assertIn(literal,SERVER)
        self.assertNotIn('active.qcow2',SERVER);self.assertNotIn('systemctl',SERVER);self.assertNotIn('server.info',SERVER)

if __name__=='__main__':unittest.main()
