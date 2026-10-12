"""Independent seven-to-seven retention / exact original inode-byte authority."""
import copy
import unittest
from pg1712_new_source_retired_backup_preservation import selected_retired,guest,server


class RetentionTest(unittest.TestCase):
    def test_exact_oldest_retained_identity_and_unknown_difference_rejected(self):
        root='/srv/schubert-nk/backup';files=['MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age']
        folder={'metadata':[28,13,992,977,16832,9,4096,10,10],'sha256':None}
        before={root:copy.deepcopy(folder)};names=[]
        for i in range(7):
            name=root+'/20261011-12000'+str(i)+'-fixed'+str(i);names.append(name);before[name]=copy.deepcopy(folder)
            for f in files:before[name+'/'+f]={'metadata':[28,100+i,0,0,33152,1,20,10,10],'sha256':'a'*64}
        after={p:copy.deepcopy(v)for p,v in before.items()if p!=names[0]and not p.startswith(names[0]+'/')}
        new=root+'/20261012-231938-02e941b9-1c52-4018-a193-63dd00b269af';after[new]=copy.deepcopy(folder)
        for f in files:after[new+'/'+f]={'metadata':[28,200,0,0,33152,1,20,20,20],'sha256':'b'*64}
        result=selected_retired(before,after)
        self.assertEqual(names[0],result['folder']);self.assertEqual(5,len(result['entries']));self.assertEqual(7,len(result['retainedCompleteFolders']))
        for bad in [None,{},dict(after,foreign={}),{p:v for p,v in after.items()if not p.endswith('config.tar')},
                    dict(after,**{names[1]+'/MANIFEST.json':{'changed':True}})]:
            with self.subTest(after=bad),self.assertRaises(ValueError):selected_retired(before,bad)
        self.assertIn('pg1699-new-current-ordinary-once-v1',guest());self.assertIn('pg1703-native-stop-v1',guest())
        for expected in ["image.fh.mode=='rb'","metadata==wanted['metadata'][1:]", "h.hexdigest()==wanted['sha256']", 'finally:image.fh.close()']:
            self.assertIn(expected,server())
        self.assertNotIn('active.qcow2',server());self.assertNotIn('systemctl',server())


if __name__=='__main__':unittest.main()
