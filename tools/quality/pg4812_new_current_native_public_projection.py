"""Hash-verified six current XML, technical session IDs redacted, no formal acceptance."""
import ast
import inspect
import pg3672_current_native_public_projection as previous
from pg4782_new_current_native_qualified import SOURCE,FULL

SLOT='pg4812-new-current-native-public-projection-v1'
PUBLIC=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4782-new-current-native-measurement-v1'


def source():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg3632-current-browser-native-qualified-v1','pg4782-new-current-native-qualified-v1'),('pg3414-outbox-full-qualified-v1',FULL),('PG3632-native-v1','PG4782-native-v1'),('PG3632-current-native-measurement-v1','PG4782-new-current-native-measurement-v1')]:raw=raw.replace(old,new)
    raw=raw.replace("n['historicalSourceNativeImported']is False","n['oldNativeImported']is False")
    old="'canonicalAcceptance':{'source':SOURCE,'accepted':17,'total':190,'automaticSourceRebinding':False}"
    if raw.count(old)!=1:raise ValueError('one historical acceptance boundary')
    raw=raw.replace(old,"'canonicalAcceptance':{'source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','accepted':17,'total':190,'automaticSourceRebinding':False,'currentSourceCriteriaRevalidationPending':True}")
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            values={18:9,20:10,3712:3739,545:549,1643:1646,2217:1654,645:0}
            if type(node.value)is int and node.value in values:return ast.copy_location(ast.Constant(values[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    ns={**vars(previous),'SOURCE':SOURCE,'SLOT':SLOT,'PUBLIC':PUBLIC}
    exec(compile(source(),'<same825e original native XML redacted projection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
