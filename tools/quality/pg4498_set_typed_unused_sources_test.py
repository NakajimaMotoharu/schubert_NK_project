"""Execute actual sealed show against independent literal full19 wire vectors."""
import ast
import unittest
import pg4498_set_typed_unused_sources as tool

FIELDS={'Id','LoadState','ActiveState','SubState','MainPID','ControlPID','Job','InvocationID','ControlGroup','Result','ExecMainCode','ExecMainStatus',
 'ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL'}
UNIT='schubert-nk-morning-controller.service'


class SealedShow(unittest.TestCase):
    def namespace(self,wire):
        def require(v):
            if v is not True:raise ValueError('sealed contract')
        def command(argv,limit):
            self.assertEqual(['/usr/bin/systemctl','show',UNIT,'--property='+','.join(sorted(FIELDS))],argv);self.assertEqual(1048576,limit)
            return wire.encode()
        ns={'require':require,'UNITS':[UNIT],'command':command};exec(tool.actual_show(),ns);return ns

    def test_actual_new_caller_has_set_and_full_literal19(self):
        values=tool.sources();tree=ast.parse(values['pg4444_native_refs.py'])
        binding=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='FIELDS'for x in ast.walk(n.targets[0])))
        ns={'sealed':{'UNITS':[UNIT]}};exec(compile(ast.Module(body=[binding],type_ignores=[]),'<actual new caller>','exec'),ns)
        self.assertIs(set,type(ns['FIELDS']));self.assertEqual(FIELDS,ns['FIELDS']);self.assertEqual(19,len(ns['FIELDS']))
        self.assertTrue(tool.previous.inspection_has_no_release_writes(values['pg4444_native_refs.py']))

    def test_actual_sealed_show_normal_both_field_orders_and_original_tuple_rejected(self):
        for order in [sorted(FIELDS),sorted(FIELDS,reverse=True)]:
            expected={k:'literal-'+k for k in order};wire=''.join(k+'='+v+'\n'for k,v in expected.items())
            self.assertEqual(expected,self.namespace(wire)['show'](UNIT,set(FIELDS)))
        wire=''.join(k+'=literal\n'for k in sorted(FIELDS))
        # This is the original failure contract, not a changed expected value.
        ns=self.namespace(wire)
        with self.assertRaises(ValueError):ns['show'](UNIT,tuple(sorted(FIELDS)))

    def test_all_missing_duplicate_unknown_and_malformed_vectors(self):
        lines=[k+'=literal'for k in sorted(FIELDS)]
        for i in range(19):
            wire='\n'.join(lines[:i]+lines[i+1:])+'\n'
            ns=self.namespace(wire)
            with self.subTest(missing=sorted(FIELDS)[i]),self.assertRaises(ValueError):ns['show'](UNIT,set(FIELDS))
        for lines2 in [lines+[lines[0]],lines+['Foreign=1'],lines+['malformed']]:
            ns=self.namespace('\n'.join(lines2)+'\n')
            with self.assertRaises(ValueError):ns['show'](UNIT,set(FIELDS))


if __name__=='__main__':unittest.main()
