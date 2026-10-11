"""Independent golden source/IO guards; no VM mutation or Production PT credit."""
import ast
import unittest
from pg1441_current_cold_sources import java
from pg1441_current_cold_refs import source


class ColdSourceTest(unittest.TestCase):
    def test_actual_static_namespace_prefix(self):
        syntax=ast.parse(source()); selected=[]
        names={'CAPTURE_BOUND','UNIT_VECTOR','CONFIG_CONTRACT','CONFIG_FIELDS'}
        for n in syntax.body:
            if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name)and t.id in names for t in n.targets):
                selected.append(n)
            elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec' and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Name)and n.value.args[1].id in names:
                selected.append(n)
        namespace={}
        exec(compile(ast.Module(body=selected,type_ignores=[]),'<isolated static contract namespaces>','exec'),namespace)
        self.assertEqual(32,len(namespace['CONFIG_FIELDS']))
        self.assertTrue(namespace['CAPTURE_BOUND']['accepted'](0,36343264,67108864))
        self.assertFalse(namespace['UNIT_VECTOR']['matches'](None,None,None))
        self.assertTrue(callable(namespace['CONFIG_CONTRACT']['same']))

    def test_current_fixed_java_binding_and_no_authority(self):
        s=java()
        for literal in ['3d69f5af-6bac-46b1-a540-7591c4a79a0d','769ddb15cd735c25fef581b5f9850ef9d0053c0f',
                        'ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',
                        'd2e3a86f-27a4-4c2a-be21-b512eebf1216','841b507c-2713-4ffe-8882-68f5fb3f87f5',
                        '2026-10-10T23:54:39.918039Z','PG243-cold-empty','parent.createPrivateChild(name)',
                        'child.atDirectory(held->','child.sync();parent.sync();']:
            self.assertIn(literal,s)
        for denied in ['PG932','pg1062','eeae04ea-713c','systemctl start','invalidate(','.revoke(','issuePermit']:
            self.assertNotIn(denied,s)
        self.assertIn('refs.check("prepared");original(session);',s)

    def test_independent_fixed_role_set_and_ids(self):
        p=ast.parse(source())
        assignment=next(n for n in p.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROLE_IDS'for t in n.targets))
        self.assertEqual({'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),
            'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),
            'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)},
            ast.literal_eval(assignment.value))

    def test_sql_numeric_boundaries_and_phase_guards(self):
        s=source();ast.parse(s)
        self.assertNotIn('str(BACKEND)+"and',s)
        for text in ['REF_READY','REF_CHECKED','REF_RELEASED','PEER_CLOSED=True','PREPARED=True',
                     'metadata(ROOT/name)==before_runtime[name]','before_inventory','ownershipRetained=true']:
            self.assertIn(text,s)
        self.assertIn("require('VERSION'in",s)
        self.assertIn('open_file()',s)
        self.assertIn('matches',s) # Complete metadata-nine plus SHA verifier.


if __name__=='__main__':unittest.main()
