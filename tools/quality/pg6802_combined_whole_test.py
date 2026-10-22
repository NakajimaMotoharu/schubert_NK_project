import unittest
import pg6802_web_correlation_whole as p
import pg6804_original4202_artifacts as original
import pg6806_correlation_positive_selected as selected


class CombinedWholeDefinitionTest(unittest.TestCase):
    def test_all_current4202_and_independent_five_additions(self):
        self.assertEqual((4202,649),p.declared_inventory())
        self.assertEqual(5,len(original.added_cases('HEAD')))
        cases,counts=selected.inventory()
        self.assertEqual((48,16),(sum(counts.values()),len(counts)))

    def test_server_count_and_real_main_namespace(self):
        raw=p.server_source('0'*40,'0'*64)
        for value in ('4202','649','1669','PG6802'):self.assertIn(value,raw)
        self.assertNotIn('4197',raw);self.assertNotIn('1667',raw)
        scope=p.definitions()
        self.assertIs(p.server_source,scope['main'].__globals__['server_source'])
        self.assertIs(p.driver_source,scope['main'].__globals__['driver_source'])
        self.assertIs(p.prerequisites,scope['main'].__globals__['prerequisites'])

    def test_original_exact_tuple_and_no_arbitrary_physical_change(self):
        raw=original.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6804-original4202-v1')
        self.assertIn("('PG6802', (4202, 649, 1669), 1)",raw)
        before={'web:Web.class':'old','other.class':'fixed'};after=dict(before,**{'web:Web.class':'new'})
        self.assertEqual((['web:Web.class'],[],1),original.reader.physical_difference(before,after,{'web:Web.class'},(2,2),[]))
        with self.assertRaises(ValueError):original.reader.physical_difference(before,dict(after,**{'other.class':'changed'}),{'web:Web.class'},(2,2),[])


if __name__=='__main__':unittest.main()
