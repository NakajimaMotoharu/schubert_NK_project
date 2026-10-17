"""Hash-verified current six XML; technical sessions redacted, no acceptance rebind."""
import ast
import pg4812_new_current_native_public_projection as previous
from pg4926_current_native_qualified import SOURCE,FULL

SLOT='pg4928-current-native-public-v1'
PUBLIC=previous.previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4926-current-native-measurement-v1'


def source():
    raw=previous.source()
    for a,b in [('pg4782-new-current-native-qualified-v1','pg4926-current-native-qualified-v1'),('pg4696-ssc299-whole-qualified-v1',FULL),('PG4782-native-v1','PG4926-native-v1'),('PG4782-new-current-native-measurement-v1','PG4926-current-native-measurement-v1')]:raw=raw.replace(a,b)
    # Latest actual individual17 qualification is7fff (PG3954), not the original
    #4856 origin. Both remain history; neither is requalified by current native.
    old="'source': '4856b3fcaeb4cae983d77757a38dc0bf56a693e2', 'accepted': 17"
    if raw.count(old)!=1:raise ValueError('one immutable historical acceptance boundary')
    raw=raw.replace(old,"'source': '7fffab57a567914956b66452e5e54388642efdec', 'originSource': '4856b3fcaeb4cae983d77757a38dc0bf56a693e2', 'accepted': 17",1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            values={3739:3761,549:551,1646:1647,1654:1655}
            if type(node.value)is int and node.value in values:return ast.copy_location(ast.Constant(values[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    ns={**vars(previous.previous),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<same current3761 native redacted evidence>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
