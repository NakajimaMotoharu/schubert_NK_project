import ast
import unittest
import pg4844_ssc301_302_full as full
import pg4846_ssc301_302_whole_qualification as qualified


class ExactWhole(unittest.TestCase):
    def test_complete_result_and_actual_format_order(self):
        raw=full.server_source(full.SOURCE,'b'*64);ns={'__name__':'pure_completeness'}
        exec(compile(raw,'<pure only>','exec'),ns)
        good=[0,True,[],3761,551,1647]
        self.assertTrue(ns['complete_result'](*good))
        for at,values in {0:[1,143,True,None],1:[False,None],2:[['error'],None],3:[3739,3760,3762],4:[549,550,552],5:[1646,1648]}.items():
            for value in values:
                args=good.copy();args[at]=value;self.assertFalse(ns['complete_result'](*args))
        self.assertLess(raw.index('    format_preflight(args,'),raw.index("with (OUT / 'maven.private.log')"))
        self.assertIn('format-before-pt.safe.json',raw)
        self.assertIn("'allSixFormatBeforeAnyPt': True",qualified.qualifier_source().replace(':True',': True'))
        ast.parse(qualified.qualifier_source())
        self.assertEqual(22,len(qualified.NEW_CASES));self.assertEqual(22,len(set(qualified.NEW_CASES)))

    def test_two_exact_main_deltas_and_no_hidden_add_remove(self):
        old={**{f'x:{i}.class':'a'*64 for i in range(1644)},**{n:'a'*64 for n in qualified.MODIFIED}}
        new={**old,**{n:'b'*64 for n in qualified.MODIFIED},**{n:'c'*64 for n in qualified.INTERFACES}}
        differences,same=qualified.physical_difference(old,new,new)
        self.assertEqual(3,len(differences));self.assertEqual(1644,same)
        for bad in [{**new,'x:extra.class':'a'*64},{**new,'x:1.class':'b'*64},{k:v for k,v in new.items()if k!='x:1.class'}]:
            with self.assertRaises(ValueError):qualified.physical_difference(old,bad,bad)


if __name__=='__main__':unittest.main()
