import ast
import types
import unittest
from pg2304_current_completed_resume_sources import sources,TOOLS,SAVE,CLASS,SOURCE,BOM,BEFORE,RUN


class CurrentResume(unittest.TestCase):
    def test_closed_twenty_source_and_current_authorities(self):
        values=sources()
        self.assertEqual(20,len(values))
        for name,raw in values.items():
            self.assertNotIn('PG1846',raw)
            self.assertNotIn('pg1980',raw)
            if name.endswith('.py'):
                for node in ast.walk(ast.parse(raw)):
                    names=[a.name for a in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)else[]
                    for module in names:
                        if module and module.startswith('pg'):
                            self.assertIn(module.split('.')[0]+'.py',values)
        java=values[CLASS+'.java']
        for literal in [SOURCE,BOM,RUN,'State.ISSUED','2026-10-13T15:28:38.568622Z','pg2126','FINITE_FRESH_RESUME_PREPARATION']:
            self.assertIn(literal,java)
        self.assertNotIn('pg1895-warning-publication',java)
        self.assertIn(BEFORE,values['pg2304_native_refs.py'])
        self.assertIn('pg2274-native-stop-v1/after.private.json',values['pg2304_native_refs.py'])
        self.assertEqual(1,values['pg2304_native_refs.py'].count("command(['/usr/bin/systemctl','daemon-reload'])"))
        self.assertNotIn("'start'",values['pg2304_native_refs.py'])

    def test_current_runtime_configuration_exact_delta_and_foreign_refusal(self):
        module=types.ModuleType('currentcontract')
        exec(sources()['pg2304_resume_contract.py'],module.__dict__)
        self.assertEqual('zz-pg2304-once-resume.conf',module.NAME)
        self.assertEqual(RUN,module.RUN)
        self.assertFalse(module.configuration(None,{},lambda _:None,lambda a,b,p:True))
        self.assertFalse(module.configuration({},None,lambda _:None,lambda a,b,p:True))
        row={str(i):''for i in range(30)}
        row.update(ExecStart='base',DropInPaths='fixed')
        old={module.MORNING:row}
        new={module.MORNING:{**row,'ExecStart':'resume','DropInPaths':'fixed '+module.TARGET}}
        parse=lambda value: ('java','base argv'+(' --resume '+RUN if value=='resume'else''),'no','n/a','n/a','0','(null)','0/0')
        self.assertTrue(module.configuration(old,new,parse,lambda a,b,p:True))
        new[module.MORNING]['DropInPaths']+=' unknown'
        self.assertFalse(module.configuration(old,new,parse,lambda a,b,p:True))
        self.assertFalse(module.runtime_tree({}, {},b'fixture',1,2))


if __name__=='__main__':unittest.main()
