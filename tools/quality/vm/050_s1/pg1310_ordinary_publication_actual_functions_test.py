"""Execute composed capture/check functions with independent data fixtures; no VM authority."""
import ast
import copy
import unittest
from pg1308_ordinary_publication_sources_v2 import sources


class ActualPublicationFunctionsTest(unittest.TestCase):
    def test_current_link_selection_after_exchange_and_unchanged_other_fields(self):
        code=sources()['pg1308_native_refs.py'];tree=ast.parse(code)
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        check=next(n for n in main.body if isinstance(n,ast.FunctionDef)and n.name=='check_data')
        def require(value):
            if not value:raise ValueError('fixture refused')
        first={'startup':{'epoch':'old'},'rows':{'all24':'fixed'},'originals':{'done':'genuine-fixed'},'configuration':{'all32':'fixed'}}
        observed=[];kernel=[]
        class Helper:
            def terminal(self,value):return value=={'MainPID':'0','ControlPID':'0','Job':''}
            def kernel_empty(self,u):kernel.append(u)
        env={'require':require,'first':first,'same_value':lambda a,b:a==b,'UNITS':['unitA','unitB'],'h':Helper(),
             'show':lambda u,f:{'MainPID':'0','ControlPID':'0','Job':''},'FIELDS':{'MainPID','ControlPID','Job'},
             'phase_observe':observed.append,'publication_phase':'epoch'}
        exec(compile(ast.Module(body=[check],type_ignores=[]),'<actual composed protected data function>', 'exec'),env)
        current=copy.deepcopy(first);current['startup']={'epoch':'new-invalid'}
        env['check_data'](current)
        self.assertEqual(observed,['epoch']);self.assertEqual(kernel,['unitA','unitB'])
        for key in ['rows','originals','configuration']:
            bad=copy.deepcopy(current);bad[key]={'changed':'not allowed'}
            with self.assertRaises(ValueError):env['check_data'](bad)
        env['show']=lambda u,f:{'MainPID':'7','ControlPID':'0','Job':''}
        with self.assertRaises(ValueError):env['check_data'](current)
        self.assertEqual(observed,['epoch'])

    def test_complete_generated_source_and_publication_order(self):
        code=sources()['pg1308_native_refs.py'];tree=ast.parse(code)
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        loop=next(n for n in main.body if isinstance(n,ast.For)and ast.unparse(n.iter)=='sys.stdin.buffer')
        text=ast.unparse(loop)
        sequence=["phase_observe('link-staged')","exchange_io.exchange(directory, 'pg1305-current.part')","phase_observe('exchanged')",'exchange_io.move_old_link(directory, save_fd',"publication_phase = 'old-linked-private'"]
        positions=[text.index(value)for value in sequence];self.assertEqual(positions,sorted(positions))
        self.assertLess(text.index("phase_observe('release')"),text.index('os.close(save_fd)'))
        self.assertLess(text.index('os.close(save_fd)'),text.index('manager.UnrefUnit'))
        capture=next(n for n in main.body if isinstance(n,ast.FunctionDef)and n.name=='capture_data')
        self.assertIn("publication_phase == 'old-linked-private'",ast.unparse(capture))


if __name__=='__main__':unittest.main()
