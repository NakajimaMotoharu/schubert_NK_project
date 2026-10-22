import unittest
import pg6767_transfer_io_bytecode as p


class OriginalIoApplicabilityTest(unittest.TestCase):
    def test_abstract_declarations_have_no_executable_counter(self):
        raw='\n'.join(' public abstract Object f();\n descriptor: ()V'for _ in range(3))
        self.assertEqual(0,p.inspect_type('Io',raw)['instructionCount'])
        with self.assertRaises(ValueError):p.inspect_type('Io',raw+'\n Code:\n 0: return')

    def test_missing_method_or_conditional_is_not_branchless(self):
        raw='\n'.join(' descriptor: ()V\n Code:\n 0: return'for _ in range(4))
        self.assertEqual([],p.inspect_type('NioIo',raw)['conditionalInstructions'])
        for bad in (raw+'\n 1: ifnull 4',raw.replace('descriptor:','gone:',1)):
            with self.assertRaises(ValueError):p.inspect_type('NioIo',bad)


if __name__=='__main__':unittest.main()
