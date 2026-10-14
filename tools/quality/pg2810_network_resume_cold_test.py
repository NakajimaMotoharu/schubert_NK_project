"""Pure cold resume negative/ownership guards, not Production PT credit."""
import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import pg2810_network_resume_cold as p
import pg2200_outage_cold_preservation as old


class ColdResume(unittest.TestCase):
    def test_exact_isolation_and_only_new_overlay_writable(self):
        a=p.arguments();b=old.arguments()
        self.assertEqual(a[a.index('-append')+1],b[b.index('-append')+1])
        self.assertNotIn('-loadvm',a)
        self.assertEqual([a[i+1]for i,n in enumerate(a)if n=='-drive'],[f'file={p.OUT}/active.qcow2,if=virtio,format=qcow2',f'file={p.BASE}/tools/seed.iso,media=cdrom,readonly=on'])
        for path in p.CHAIN:self.assertNotIn(str(path),a)

    def test_three_layer_identity_dirty_corrupt_and_sizes(self):
        v=[{'filename':str(path),'format':'qcow2','virtual-size':size*1024**3,'dirty-flag':False,'format-specific':{'data':{'corrupt':False}}}for path,size in zip(p.CHAIN,[48,48,40],strict=True)]
        p.validate_chain(v)
        for key,value in [('filename','foreign'),('format','raw'),('dirty-flag',True),('snapshots',[{}]),('virtual-size',1)]:
            wrong=copy.deepcopy(v);wrong[0][key]=value
            with self.assertRaises(ValueError):p.validate_chain(wrong)
        wrong=copy.deepcopy(v);wrong[1]['format-specific']['data']['corrupt']=True
        with self.assertRaises(ValueError):p.validate_chain(wrong)
        with self.assertRaises(ValueError):p.validate_chain(v[:2])

    def test_before_exclusive_and_foreign_or_changed_chain_never_launches(self):
        with tempfile.TemporaryDirectory()as tmp,patch.object(p,'OUT',Path(tmp)),patch.object(p,'idle'),patch.object(p.subprocess,'run')as launch:
            p.save('manifest.safe.json',{'actualExit':0,'logicalCompareExit':0,'source':'foreign'})
            with self.assertRaises(ValueError):p.boot()
            launch.assert_not_called()
            with self.assertRaises(FileExistsError):p.save('manifest.safe.json',{})


if __name__=='__main__':unittest.main()
