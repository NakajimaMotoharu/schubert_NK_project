"""Actual current ten/twelve native counters, redacted sessions, no acceptance lift."""
import ast
import pg4928_current_native_public as previous
from pg4942_current_bootstrap_native import SOURCE,SLOT as NATIVE

SLOT='pg4944-current-bootstrap-public-v1'
PUBLIC=previous.previous.previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4942-current-bootstrap-native-v1'


def source():
    raw=previous.source()
    for old,new in [('pg4926-current-native-qualified-v1',NATIVE),('PG4926-native-v1','PG4942-native-v1'),('PG4926-current-native-measurement-v1','PG4942-current-bootstrap-native-v1')]:raw=raw.replace(old,new)
    class PairCounts(ast.NodeTransformer):
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if len(node.ops)==1 and isinstance(node.ops[0],ast.Eq)and isinstance(node.left,ast.Subscript)and isinstance(node.left.slice,ast.Constant):
                key=node.left.slice.value
                if key in ('currentNativeStreams','validatedNativePoints'):
                    if len(node.comparators)!=1 or not isinstance(node.comparators[0],ast.Constant):raise ValueError('literal native pair guard')
                    node.comparators=[ast.Constant(10 if key=='currentNativeStreams'else 12)]
            return node
    return ast.unparse(ast.fix_missing_locations(PairCounts().visit(ast.parse(raw))))


def main():
    ns={**vars(previous.previous.previous),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<current physical1647 technical public projection>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
