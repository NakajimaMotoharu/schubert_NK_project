"""Same-source0ea provenance/count/CRC/session/redaction matrix; no VM authority."""
import ast
import inspect
import unittest
import pg5514_current_native_test as reference
import pg5678_current_owned_test as owned_fixture
import pg5680_current_native_catalog as catalog
import pg5682_current_native_qualified as native
import pg5684_current_native_public as public


class CurrentFixture(ast.NodeTransformer):
    def visit_Constant(self,node):
        if type(node.value)is int and node.value in{3896,562}:return ast.copy_location(ast.Constant({3896:3905,562:563}[node.value]),node)
        if type(node.value)is str:
            value=node.value
            for old,new in(('pg5496','pg5670'),('PG5414','PG5588'),('PG5510','PG5682'),('all88','all94'),('==88','==94'),
              ("full['tests'] == 3896","full['tests'] == 3905"),('3896','3905'),('562','563')):value=value.replace(old,new)
            return ast.copy_location(ast.Constant(value),node)
        return node


tree=ast.parse(inspect.getsource(reference.Native))
# Extra source-bound adapter does not change the coordinates algorithm.
raw=ast.unparse(tree).replace('native.previous.previous.previous.transport','native.previous.previous.previous.previous.transport')
tree=CurrentFixture().visit(ast.parse(raw))
namespace={**vars(reference),'owned_fixture':owned_fixture,'catalog':catalog,'native':native,'public':public,'__file__':__file__}
exec(compile(ast.fix_missing_locations(tree),'<explicit0ea/3905/563/all1664 independent matrix>','exec'),namespace)
Native=namespace['Native']


if __name__=='__main__':unittest.main()
