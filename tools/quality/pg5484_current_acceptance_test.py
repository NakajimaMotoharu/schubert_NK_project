"""Reuse unchanged independent admission/SQL fault algorithms with explicit296/88 fixture data."""
import ast
import inspect
import textwrap
import unittest
import pg5044_current_acceptance_test as reference
import pg5476_current_admission_image as admission
import pg5478_current_genuine_terminal as terminal
import pg5480_current_newday_rows as rows
import pg5482_current_newday_whole_seal as seal


class Current88Fixture(ast.NodeTransformer):
    def visit_Constant(self,node):
        if type(node.value)is int and node.value==80:
            return ast.copy_location(ast.Constant(88),node)
        if type(node.value)is str:
            value=node.value
            for before,after in(('all80','all88'),('before80','before88'),('current80','current88'),('nativeExecEntries\':80','nativeExecEntries\':88'),('!=80','!=88'),
                ('PG4980','PG5430'),('pg4980-manifest.sig','pg5430-manifest.sig')):
                value=value.replace(before,after)
            return ast.copy_location(ast.Constant(value),node)
        return node


class Acceptance(unittest.TestCase):
    pass


for name,method in vars(reference.Acceptance).items():
    if not name.startswith('test_'):continue
    tree=Current88Fixture().visit(ast.parse(textwrap.dedent(inspect.getsource(method))))
    namespace={**vars(reference),'admission':admission,'terminal':terminal,'rows':rows,'seal':seal,'__file__':__file__,'__name__':__name__}
    exec(compile(ast.fix_missing_locations(tree),'<explicit current296/88 independent fixture>','exec'),namespace)
    setattr(Acceptance,name,namespace[name])


if __name__=='__main__':unittest.main()
