"""All-emitted static global closure, actual role/argv and no-signal boundary."""
import ast
import unittest
from pg1777_warning_retained_pair_readonly_proof import payload


class Proof(unittest.TestCase):
    def test_actual_actor_and_child_inputs_do_not_use_old_profile(self):
        raw=payload();tree=ast.parse(raw)
        argv=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EXPECTED_ARGV'for t in n.targets))
        args=ast.literal_eval(argv).split(b'\0')
        self.assertEqual(b'Pg1772NativeStop',args[-3]);self.assertEqual(b'stop',args[-2])
        child=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='ref_child')
        compare=next(n for n in ast.walk(child)if isinstance(n,ast.Compare)and isinstance(n.left,ast.Name)and n.left.id=='argv')
        expression=ast.Expression(compare.comparators[0]);child_argv=eval(compile(expression,'<literal argv golden>','eval'),{'__builtins__':{}})
        self.assertEqual([b'/usr/bin/python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg1772-warning-owned-stop-tools-v1/pg1772_native_refs.py',b'stop',b'476114',b''],child_argv.split(b'\0'))
        self.assertIn('len(fds)==101',raw);self.assertIn('children=={476116}',raw)
        for old in ['383695','383693','PG1719-bootstrap-guard','len(fds)==99']:
            self.assertNotIn(old,raw)
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertNotIn('os.kill(',raw)
        self.assertIn("'stopReservations0':True",raw)


if __name__=='__main__':unittest.main()
