import unittest
import pg6784_web_management_result_whole as p
import pg6786_original4197_web_artifacts as original


class WebWholeDefinitionTest(unittest.TestCase):
    def test_current4197_declarations_and_all1669_exact(self):
        self.assertEqual((4197,646),p.declared_inventory())
        raw=p.server_source('0'*40,'0'*64)
        for v in ('4197','646','1669','PG6784'):self.assertIn(v,raw)
        self.assertNotIn('1667',raw);self.assertNotIn('systemctl',raw)

    def test_main_uses_new_only_driver_and_server(self):
        scope=p.definitions()
        self.assertIs(p.server_source,scope['main'].__globals__['server_source'])
        self.assertIs(p.driver_source,scope['main'].__globals__['driver_source'])
        self.assertIs(p.prerequisites,scope['main'].__globals__['prerequisites'])

    def test_original_all_same_count_but_necessary_web_owner_change(self):
        before={'web:WebManagementServer.class':'old','other.class':'fixed'};after=dict(before,**{'web:WebManagementServer.class':'new'})
        self.assertEqual((['web:WebManagementServer.class'],[],1),original.reader.physical_difference(before,after,{'web:WebManagementServer.class'},(2,2),[]))
        with self.assertRaises(ValueError):original.reader.physical_difference(before,before,{'web:WebManagementServer.class'},(2,2),[])
        raw=original.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6786-original4197-web-v1')
        self.assertIn("('PG6784', (4197, 646, 1669), 1)",raw)


if __name__=='__main__':unittest.main()
