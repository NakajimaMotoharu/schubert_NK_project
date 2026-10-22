import ast
import unittest
import pg6760_transfer_io_selected as p


class TransferIoProfileTest(unittest.TestCase):
    def test_all_eight_new_cases_and_six_guards_exact(self):
        cases,counts=p.inventory()
        self.assertEqual((27,10),(sum(counts.values()),len(counts)));self.assertEqual(6,len(cases))
        self.assertEqual(8,counts['dev.codex.schubert.nk.batch.file.TransferIoBoundaryTest'])

    def test_exact_two_new_physical_types_and_strict_qualified_namespace(self):
        self.assertEqual({'batch:dev/codex/schubert/nk/batch/file/TransferCleanup$Io.class',
          'batch:dev/codex/schubert/nk/batch/file/TransferCleanup$NioIo.class'},p.ADDED)
        fn=p.qualification_definition()
        self.assertEqual(p.ADDED,fn.__globals__['ADDED'])
        self.assertIn('1669',str(fn.__code__.co_consts))

    def test_runner_uses_exact1669_not_dynamic_or_relaxed_threshold(self):
        raw=p.runner(*p.EXPECTED,{'batch':['batch/file/TransferCleanup']})
        ast.parse(raw);self.assertIn('len(physical)==1669',raw)
        self.assertNotIn('len(physical)==1667',raw);self.assertNotIn('len(physical)>=',raw)


if __name__=='__main__':unittest.main()
