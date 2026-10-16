import copy
import stat
import unittest
from current_after_native_schema import expand,KEYS,PREFIX


class NativeSchema(unittest.TestCase):
    def test_exact_provenance_missing_extra_foreign_metadata_and_schema(self):
        after={key:{}for key in KEYS}
        directory={'metadata':[1,2,0,0,stat.S_IFDIR|0o700,2,128,1,1],'sha256':None}
        old={'metadata':[1,3,0,0,stat.S_IFREG|0o600,1,3,1,1],'sha256':'a'*64}
        new={'metadata':[1,4,0,0,stat.S_IFREG|0o600,1,4,2,2],'sha256':'b'*64}
        original={PREFIX[:-1]:directory,PREFIX+'old.exec':old}
        native={**original,PREFIX+'new.exec':new}
        selected=[{'relative':'new.exec','metadata':new['metadata'],'sha256':'b'*64,'bytes':4}]
        self.assertEqual({**after,'native':native},expand(after,native,original,selected,['old.exec'],2))
        bad_native=copy.deepcopy(native);bad_native[PREFIX+'new.exec']['sha256']='c'*64
        bad_mode=copy.deepcopy(native);bad_mode[PREFIX[:-1]]['metadata'][4]=stat.S_IFDIR|0o777
        cases=[({**after,'native':{}},native,selected,['old.exec']),({k:v for k,v in after.items()if k!='units'},native,selected,['old.exec']),(after,bad_native,selected,['old.exec']),(after,bad_mode,selected,['old.exec']),(after,{**native,PREFIX+'unknown.exec':old},selected,['old.exec']),(after,native,selected,[]),(after,native,selected,['../old.exec']),(after,native,selected+selected,['old.exec'])]
        for a,n,s,e in cases:
            with self.assertRaises(ValueError):expand(a,n,original,s,e,2)
        for metadata in [None,[],[1]*6]:
            bad=[{**selected[0],'metadata':metadata}]
            with self.assertRaises(ValueError):expand(after,native,original,bad,['old.exec'],2)
        self.assertNotIn('native',after)


if __name__=='__main__':unittest.main()
