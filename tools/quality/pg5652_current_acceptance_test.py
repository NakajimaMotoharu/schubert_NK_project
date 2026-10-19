"""Independent admission/SQL fault algorithms, explicit0ea/94 fixture, no guest action."""
import ast
import inspect
import textwrap
import unittest
import pg5044_current_acceptance_test as reference
import pg5644_current_admission_image as admission
import pg5646_current_genuine_terminal as terminal
import pg5648_current_newday_rows as rows
import pg5650_current_newday_whole_seal as seal


class Current94Fixture(ast.NodeTransformer):
    def visit_Call(self,node):
        if ast.unparse(node.func)=='admission.live':
            return ast.copy_location(ast.Call(func=ast.Name(id='independent_observed',ctx=ast.Load()),args=[],keywords=[]),node)
        return self.generic_visit(node)

    def visit_Constant(self,node):
        if type(node.value)is int and node.value==80:return ast.copy_location(ast.Constant(94),node)
        if type(node.value)is str:
            value=node.value
            for before,after in(('all80','all94'),('before80','before94'),('current80','current94'),("nativeExecEntries':80","nativeExecEntries':94"),('!=80','!=94'),
              ('PG4980','PG5598'),('pg4980-manifest.sig','pg5598-manifest.sig')):value=value.replace(before,after)
            return ast.copy_location(ast.Constant(value),node)
        return node


class Acceptance(unittest.TestCase):
    pass


def independent_observed():
    # Handwritten, inert fixture; no read of any historical or future owner.
    return {'activation':'11111111-1111-4111-8111-111111111111','boot':'22222222-2222-4222-8222-222222222222',
      'cutoff':'2026-10-19T14:00:00Z','invocation':'3'*32,'job':'12345',
      'run':'44444444-4444-4444-8444-444444444444','start':123456,'rootPid':1234}


for name,method in vars(reference.Acceptance).items():
    if not name.startswith('test_'):continue
    tree=Current94Fixture().visit(ast.parse(textwrap.dedent(inspect.getsource(method))))
    namespace={**vars(reference),'admission':admission,'terminal':terminal,'rows':rows,'seal':seal,
      'independent_observed':independent_observed,'__file__':__file__,'__name__':__name__}
    exec(compile(ast.fix_missing_locations(tree),'<explicit current0ea/94 independent fixture>','exec'),namespace)
    setattr(Acceptance,name,namespace[name])


if __name__=='__main__':unittest.main()
