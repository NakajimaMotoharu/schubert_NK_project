import unittest
import pg6768_transfer_io_whole as p
import pg6770_original4197_transfer_artifacts as original


class TransferWholeDefinitionTest(unittest.TestCase):
    def test_all_current_declarations_including_unchanged_old_cases(self):
        self.assertEqual((4197,646),p.declared_inventory())
        self.assertEqual(8,len(original.added_cases('HEAD')))

    def test_server_counts_exactly_include_two_declared_types(self):
        raw=p.server_source('0'*40,'0'*64)
        self.assertIn('4197',raw);self.assertIn('646',raw);self.assertIn('1669',raw)
        self.assertNotIn('1667',raw);self.assertNotIn('systemctl',raw)

    def test_original_physical_scope_rejects_any_undeclared_class(self):
        before={'batch:Transfer.class':'old','other.class':'same'}
        after={'batch:Transfer.class':'new','other.class':'same','batch:Transfer$Io.class':'a','batch:Transfer$NioIo.class':'b'}
        added={'batch:Transfer$Io.class','batch:Transfer$NioIo.class'}
        self.assertEqual(1,original.reader.physical_difference(before,after,{'batch:Transfer.class'},(2,4),added)[2])
        with self.assertRaises(ValueError):original.reader.physical_difference(before,dict(after,**{'other.class':'changed'}),{'batch:Transfer.class'},(2,4),added)
        raw=original.emitted('0'*64,'/home/mini/schubert-nk-pgpt/transfer/PG6770-original4197-transfer-v1')
        self.assertIn("('PG6768', (4197, 646, 1669), 1)",raw)


if __name__=='__main__':unittest.main()
