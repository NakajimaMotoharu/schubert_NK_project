import ast
import unittest
from pg1270_fresh_log_journal_capture_v4 import payload
from pg1260_fresh_backup_independent_capture import SEALS


class ActualFrozenJournalTest(unittest.TestCase):
    def test_actual_namespace_fullfield_order_and_negative(self):
        s=payload(SEALS);n=ast.parse(s);compile(n,'<whole actual current Log>','exec')
        source=next(ast.literal_eval(t.value)for t in n.body if isinstance(t,ast.Assign)and any(isinstance(k,ast.Name)and k.id=='JOURNAL_SOURCE'for k in t.targets))
        e={};exec(source,e);project=e['project']
        a=b'{"__CURSOR":"literal","MESSAGE":"private fixture","OTHER":[1,2]}\n'
        b=b'{"OTHER":[1,2],"MESSAGE":"private fixture","__CURSOR":"literal"}\n'
        self.assertEqual(project(a),project(b));self.assertNotEqual(project(a),project(b.replace(b'[1,2]',b'[2,1]')))
        for raw in [None,b'{"__CURSOR":"literal","OTHER":null}',a+a,b'{"__CURSOR":"literal","__CURSOR":"literal"}']:
            with self.assertRaises((ValueError,TypeError)):project(raw)
        scope=next(t for t in n.body if isinstance(t,ast.Try))
        self.assertIn('verify_fresh',[t.func.attr for t in ast.walk(scope)if isinstance(t,ast.Call)and isinstance(t.func,ast.Attribute)])
        self.assertNotIn('save',[t.id for t in ast.walk(scope)if isinstance(t,ast.Name)])


if __name__=='__main__':unittest.main()
