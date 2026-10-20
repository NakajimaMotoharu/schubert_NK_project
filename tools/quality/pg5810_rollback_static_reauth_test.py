import unittest
from pg5810_rollback_static_reauth import bind_identity


class FullUnchangedMainIdentityTest(unittest.TestCase):
    def test_one_missing_changed_or_extra_byte_rejects_static_reuse(self):
        sources={str(i):'a'*64 for i in range(850)};classes={str(i):'b'*64 for i in range(1665)}
        bind_identity(sources,dict(sources),classes,dict(classes))
        for bad in({**sources,'0':'c'*64},{k:v for k,v in sources.items()if k!='0'}):
            with self.assertRaises(ValueError):bind_identity(sources,bad,classes,classes)
        with self.assertRaises(ValueError):bind_identity(sources,sources,classes,{**classes,'extra':'b'*64})


if __name__=='__main__':unittest.main()
