import ast
import unittest
import pg2144_normal_unused_fixed_sources as p


class NormalSettings(unittest.TestCase):
    def test_literal_parent_contract_all_actual_graph(self):
        values=p.sources('a'*64)
        self.assertIn('Pg2144UnusedStage.java',values)
        raw=values['pg2144_native_refs.py']
        self.assertIn("parent_config=={'Type':'oneshot','SuccessExitStatus':'10'}",raw)
        self.assertIn('qualify_warning_parent(parent)',raw)
        self.assertIn('pg2130-current-normal-before-v1',raw)
        for body in values.values():
            self.assertNotIn("parent_config=={'Type':'oneshot','SuccessExitStatus':''}",body)
            self.assertNotIn('pg2132-current-normal-unused-tools-v1',body)
            self.assertNotIn('pg2136-current-normal-unused-placement-v1',body)
        # Execute just the literal fixed condition with an independent tuple table.
        expr=next(n.args[0] for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'and any(isinstance(v,ast.Name)and v.id=='parent_config'for v in ast.walk(n)))
        code=compile(ast.Expression(expr),'<independent normal tuple>','eval')
        for cfg,expected in [({'Type':'oneshot','SuccessExitStatus':'10'},True),({'Type':'oneshot','SuccessExitStatus':''},False),({'Type':'simple','SuccessExitStatus':'10'},False),({'Type':'oneshot','SuccessExitStatus':'0 10'},False),({'Type':'oneshot','SuccessExitStatus':None},False)]:
            self.assertEqual(eval(code,{'parent_config':cfg,'parent':{'Type':'oneshot'}}),expected)


if __name__=='__main__':unittest.main()
