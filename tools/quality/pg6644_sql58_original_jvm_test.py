import unittest
import pg6644_sql58_original_jvm as p


class OriginalGuardBindingTest(unittest.TestCase):
    def test_resolves_import_static_and_same_package_not_suffix_only(self):
        self.assertEqual('a/b/Temp',p.target_owner('import a.b.Temp;\nTemp.preserveFatal(x);',2,'x'))
        self.assertEqual('a/b/Temp',p.target_owner('import static a.b.Temp.preserveFatal;\npreserveFatal(x);',2,'x'))
        self.assertEqual('a/b/Temp',p.target_owner('package a.b;\nTemp.preserveFatal(x);',2,'x'))
        with self.assertRaises(ValueError):p.target_owner('preserveFatal(x);',1,'x')
        with self.assertRaises(ValueError):p.target_owner('package a;\nTemp.preserveFatal(y);',2,'x')

    def test_exact_receiver_and_distinct_original_finally_paths(self):
        row=dict(siteId='s',sourcePath='p',sourceSha256='h',guardLine=2,catchVariable='x',aggregateGuardLineCounter=dict(ci=1,mi=0,cb=0,mb=0))
        text='package a;\nTemp.preserveFatal(x);'
        call=dict(line=2,method='preserveFatal',owner='a/Temp',physicalClass='original',member='m',bci=1)
        self.assertEqual(2,len(p.match_guard(row,text,[call,dict(call,bci=4)])['actualJvmPaths']))
        for calls in ([],[dict(call,owner='b/Temp')],[call,call]):
            with self.assertRaises(ValueError):p.match_guard(row,text,calls)
        with self.assertRaises(ValueError):p.match_guard(dict(row,aggregateGuardLineCounter=dict(ci=0)),text,[call])


if __name__=='__main__':unittest.main()
