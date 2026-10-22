import unittest
import pg6828_api_management_result_whole as p
import pg6830_original4203_artifacts as original


class ApiWholeDefinitionTest(unittest.TestCase):
    def test_all4203_declarations_and_one_new_literal_test(self):
        self.assertEqual((4203,650),p.declared_inventory())
        self.assertEqual(1,len(original.added_cases('HEAD')))

    def test_exact_counts_and_runtime_function_namespace(self):
        raw=p.server_source('0'*40,'0'*64)
        for value in ('4203','650','1669','PG6828'):self.assertIn(value,raw)
        self.assertNotIn('4202',raw);self.assertNotIn('1667',raw)
        scope=p.definitions()
        self.assertIs(p.server_source,scope['main'].__globals__['server_source'])
        self.assertIs(p.driver_source,scope['main'].__globals__['driver_source'])

    def test_only_declared_original_tuple_exported(self):
        raw=original.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6830-original4203-v1')
        self.assertIn("('PG6828', (4203, 650, 1669), 1)",raw)


if __name__=='__main__':unittest.main()
