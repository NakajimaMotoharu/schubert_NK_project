import copy
import stat
import unittest
from pg3559_preservation_schema_contract import preservation_trees,COUNTS


def fixture():
    def tree(name,count):
        return {'/'+name+'/'+str(i):{'metadata':[1,i+1,0,0,stat.S_IFREG|0o600,1,0,1,1],'sha256':'a'*64}for i in range(count)}
    return {'originals':tree('original',112),'backup':tree('backup',47),
            'extraDurable':{'credentials':tree('credentials',19),'oldProofs':tree('oldProofs',51)}}


class PreservationSchema(unittest.TestCase):
    def test_exact_four_trees_and_all229_leafs(self):
        result=preservation_trees(fixture())
        self.assertEqual(list(COUNTS),[n for n,t in result])
        self.assertEqual(229,sum(len(t)for n,t in result))

    def test_missing_extra_relative_and_category_as_path_rejected(self):
        for mutation in ['missing','extra','relative','dotdot','metadata','digest','symlink','unknownField','wrongCount']:
            value=fixture()
            if mutation=='missing':del value['extraDurable']['oldProofs']
            elif mutation=='extra':value['extraDurable']['unknown']={}
            else:
                key=next(iter(value['originals']));item=value['originals'][key]
                if mutation=='relative':value['originals']['credentials']=value['originals'].pop(key)
                elif mutation=='dotdot':value['originals']['/data/../other']=value['originals'].pop(key)
                elif mutation=='metadata':item['metadata']=item['metadata'][:8]
                elif mutation=='digest':item['sha256']=None
                elif mutation=='symlink':item['metadata'][4]=stat.S_IFLNK|0o777
                elif mutation=='unknownField':item['other']=True
                else:value['originals'].pop(key)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):preservation_trees(value)

    def test_null_typed_shape_and_directory_contract(self):
        for value in [None,{},{'originals':{},'backup':{},'extraDurable':None}]:
            with self.assertRaises(ValueError):preservation_trees(value)
        value=fixture();item=next(iter(value['originals'].values()));item['metadata'][4]=stat.S_IFDIR|0o700;item['sha256']=None
        self.assertEqual(4,len(preservation_trees(value)))
        other=copy.deepcopy(value);next(iter(other['originals'].values()))['sha256']='a'*64
        with self.assertRaises(ValueError):preservation_trees(other)


if __name__=='__main__':unittest.main()
