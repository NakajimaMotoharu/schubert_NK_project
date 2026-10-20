import ast
import inspect
import unittest
import pg6106_locked_flag_selected as p


class LockedFlagSelectionTest(unittest.TestCase):
    def test_same925_declared_tests_and_strict_class_counter_gate(self):
        _,counts=p.inventory();self.assertEqual((925,150),(sum(counts.values()),len(counts)))
        raw=p.runner_source();ast.parse(raw)
        for text in ('done=done and target100','len(physical)==1667',"'expectedTests':925",'os.pathsep+NODE_PATH,MAVEN_OPTS'):
            self.assertIn(text,raw)
        own=inspect.getsource(p.main)
        self.assertIn("'TARGETS':{'web':['web/messaging/ArtemisReplyConsumers']}",own)
        self.assertIn('before.replace',own)
        for name in ('systemctl','qemu-system','sudo ','--recover','--resume'):
            self.assertNotIn(name,raw)


if __name__=='__main__':unittest.main()
