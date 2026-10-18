"""Hash-verified new296 six XML, raw native session IDs redacted; F03/BUG1453 held."""
import ast
import pg5074_current_native_public as previous
from pg5510_current_native_qualified import SOURCE,FULL

SLOT='pg5512-current-native-public-v1'
PUBLIC=previous.PUBLIC.parent/'PG5510-current-native-measurement-v1'


def source():
    raw=previous.source()
    for old,new in(('pg5072-current-native-qualified-v1','pg5510-current-native-qualified-v1'),
        ('pg4970-ssc304-whole-qualified-v1',FULL),('PG5072-native-v1','PG5510-native-v1'),
        ('PG5072-current-native-measurement-v1','PG5510-current-native-measurement-v1')):
        raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3791,553,1650,1657}:
                node.value={3791:3896,553:562,1650:1664,1657:1647}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    template=previous.previous.previous.previous
    ns={**vars(template),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<same3896 current native redacted proof>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
