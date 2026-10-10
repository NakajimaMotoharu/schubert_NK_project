"""Independent fixed generation/payload closure; no VM operations."""
import ast
import unittest
from pg1117_current_done_probe import BINDING, payload


class ProbeTest(unittest.TestCase):
    def test_literal_binding(self):
        self.assertEqual(BINDING, {
            'boot':'cbca87383b244090b77cbf029677cdd6',
            'invocation':'21f20c0cdbe34ce99431a55b10f92285','job':'36002',
            'start':34658346852,'run':'343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
            'cutoff':'2026-10-10T12:40:27.396847Z',
            'activation':'ada3f7ff-8287-48d7-9ba9-5cce71f61bd3'})

    def test_payload_is_receipt_only_no_operations(self):
        text=payload();tree=ast.parse(text)
        self.assertTrue("scope':'RECEIPT_ONLY'" in text)
        self.assertFalse('pg960' in text or 'pg932' in text)
        literals=[node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str)]
        calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)
               and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name)
               and node.func.value.id=='subprocess']
        commands=[node.args[0] for node in calls if node.args and isinstance(node.args[0],ast.List)]
        operations=[item.value for command in commands for item in command.elts
                    if isinstance(item,ast.Constant) and isinstance(item.value,str)]
        self.assertFalse(any(x in operations for x in ['start','stop','restart','kill','daemon-reload']))
        self.assertTrue('qualify(BINDING,rows,done)' in text)
        self.assertTrue('terminal receipt unstable' in literals)

    def test_active_expected_literal_bytes(self):
        tree=ast.parse(payload())
        nodes=[node for node in tree.body if isinstance(node,ast.Assign)
               and any(isinstance(t,ast.Name)and t.id=='expected' for t in node.targets)]
        self.assertEqual(len(nodes),1)
        env={'BINDING':BINDING}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<expected-byte fixture>','exec'),env)
        self.assertEqual(env['expected'],
            b'NKACT1\n343a5a1b-d064-47d5-88c2-31c36d7ba7a4\n2026-10-10T12:40:27.396847Z\n'
            b'ada3f7ff-8287-48d7-9ba9-5cce71f61bd3\n')

    def test_oneshot_terminal_literal_and_all_negative_fields(self):
        tree=ast.parse(payload())
        candidates=[node for node in tree.body if isinstance(node,ast.If)
                    and any(isinstance(n,ast.Constant)and n.value=='current parent not terminal-success'
                            for n in ast.walk(node))]
        self.assertEqual(len(candidates),1)
        expr=ast.Expression(candidates[0].test)
        state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','Job':'',
               'Result':'success','ExecMainCode':'1','ExecMainStatus':'0',
               'InvocationID':'21f20c0cdbe34ce99431a55b10f92285',
               'ExecMainStartTimestampMonotonic':'34658346852'}
        code=compile(expr,'<independent terminal fixture>','eval')
        self.assertFalse(eval(code,{'state':state,'BINDING':BINDING}))
        for key in state:
            value=dict(state);value[key]='1' if key=='ExecMainStartTimestampMonotonic' else 'wrong'
            with self.subTest(key=key):
                self.assertTrue(eval(code,{'state':value,'BINDING':BINDING}))
        # The previously manufactured active/exited expectation must be rejected.
        value=dict(state,ActiveState='active',SubState='exited')
        self.assertTrue(eval(code,{'state':value,'BINDING':BINDING}))
        self.assertTrue("if os.path.lexists(base/'active')" in payload())
        self.assertFalse("read(base/'active')" in payload())


if __name__=='__main__':unittest.main()
