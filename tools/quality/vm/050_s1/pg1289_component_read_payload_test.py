import ast
import unittest
from pg1288_physical_pin_counter import exec_read_payload


class ComponentReadPayloadTest(unittest.TestCase):
    def test_actual_sizes_and_boundaries_compile(self):
        for name in ['rw.exec','ro.exec']:
            for size in [1,1004,1133,1048576]:
                code=exec_read_payload(name,dict(execBytes=size,execSha256='f'*64))
                ast.parse(code)
                self.assertIn(str(size)+' and ',code)
                self.assertIn('(0,0,0o600,1)',code)

    def test_unknown_null_and_injection_refused(self):
        valid=dict(execBytes=1133,execSha256='f'*64)
        for name in ['',None,'../rw.exec',"rw.exec');print('injected"]:
            with self.assertRaises(ValueError):exec_read_payload(name,valid)
        for value in [None,{},dict(valid,execBytes=None),dict(valid,execBytes=True),dict(valid,execBytes=0),dict(valid,execBytes=1048577),dict(valid,execSha256='g'*64),dict(valid,execSha256=None)]:
            with self.assertRaises(ValueError):exec_read_payload('rw.exec',value)


if __name__=='__main__':unittest.main()
