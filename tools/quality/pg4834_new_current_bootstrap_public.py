"""Publish same-source measured ten/twelve counters and redacted XML, no acceptance lift."""
import ast
import pg4812_new_current_native_public_projection as previous
from pg4832_new_current_bootstrap_native import SLOT as NATIVE

SLOT='pg4834-new-current-bootstrap-public-v1'
PUBLIC=previous.previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4832-new-current-bootstrap-native-v1'


def source():
    raw=previous.source()
    for old,new in [('pg4782-new-current-native-qualified-v1',NATIVE),('PG4782-native-v1','PG4832-native-v1'),('PG4782-new-current-native-measurement-v1','PG4832-new-current-bootstrap-native-v1')]:raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if len(node.ops)==1 and isinstance(node.ops[0],ast.Eq)and isinstance(node.left,ast.Subscript)and isinstance(node.left.slice,ast.Constant):
                key=node.left.slice.value
                if key in ('currentNativeStreams','validatedNativePoints'):
                    expected=10 if key=='currentNativeStreams'else 12
                    if len(node.comparators)!=1 or not isinstance(node.comparators[0],ast.Constant):raise ValueError('literal current measurement guard')
                    node.comparators=[ast.Constant(expected)]
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    return raw


def main():
    ns={**vars(previous.previous),'SOURCE':previous.SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<current genuine Bootstrap native technical projection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
