"""Hash-verified new0ea six XML/native; raw session IDs redacted, no formal acceptance."""
import ast
import pg5512_current_native_public as previous
from pg5682_current_native_qualified import SOURCE,FULL

SLOT='pg5684-current-native-public-v1'
PUBLIC=previous.PUBLIC.parent/'PG5682-current-native-measurement-v1'


def source():
    raw=previous.source()
    for old,new in(('pg5510-current-native-qualified-v1','pg5682-current-native-qualified-v1'),
      ('pg5416-ownership-whole-qualified-v2',FULL),('PG5510-native-v1','PG5682-native-v1'),
      ('PG5510-current-native-measurement-v1','PG5682-current-native-measurement-v1')):raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3896,562}:node.value={3896:3905,562:563}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    template=previous.previous.previous.previous.previous
    ns={**vars(template),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<same3905 currentnative redacted evidence>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
