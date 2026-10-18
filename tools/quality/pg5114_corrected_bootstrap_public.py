"""Current10 streams/12 points, six hash-verified redacted XML; no formal promotion."""
import ast
import pg5074_current_native_public as previous
from pg5112_corrected_bootstrap_native import SOURCE,SLOT as NATIVE

SLOT='pg5114-corrected-bootstrap-public-v1'
PUBLIC=previous.PUBLIC.parent/'PG5112-corrected-bootstrap-native-v1'


def source():
    raw=previous.source()
    for old,new in [('pg5072-current-native-qualified-v1',NATIVE),('PG5072-native-v1','PG5112-native-v1'),
                    ('PG5072-current-native-measurement-v1','PG5112-corrected-bootstrap-native-v1')]:
        raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if len(node.ops)==1 and isinstance(node.ops[0],ast.Eq)and isinstance(node.left,ast.Subscript)and isinstance(node.left.slice,ast.Constant):
                key=node.left.slice.value
                if key in ('currentNativeStreams','validatedNativePoints'):
                    node.comparators=[ast.Constant(10 if key=='currentNativeStreams'else 12)]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    template=previous.previous.previous.previous
    ns={**vars(template),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<same current1650 technical projection>', 'exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
