"""Six original current XML hashes then redacted public projection; not formal acceptance."""
import ast
import inspect
import pg3672_current_native_public_projection as previous
from pg4662_current_native_qualified import SOURCE,FULL

SLOT='pg4664-current-native-public-projection-v1'
PUBLIC=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4662-current-native-measurement-v1'


def main():
    raw=inspect.getsource(previous.main)
    raw=raw.replace('pg3632-current-browser-native-qualified-v1','pg4662-current-native-qualified-v1').replace('pg3414-outbox-full-qualified-v1',FULL).replace('PG3632-native-v1','PG4662-native-v1').replace('PG3632-current-native-measurement-v1','PG4662-current-native-measurement-v1')
    raw=raw.replace("n['historicalSourceNativeImported']is False","n['oldNativeImported']is False")
    old="'canonicalAcceptance':{'source':SOURCE,'accepted':17,'total':190,'automaticSourceRebinding':False}"
    if raw.count(old)!=1:raise ValueError('one historical acceptance boundary')
    raw=raw.replace(old,"'canonicalAcceptance':{'source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','accepted':17,'total':190,'automaticSourceRebinding':False,'currentSourceCriteriaRevalidationPending':True}")
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {18,20,3712,1643,2217,645}:
                return ast.copy_location(ast.Constant({18:9,20:10,3712:3721,1643:1644,2217:1654,645:0}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    ns={**vars(previous),'SLOT':SLOT,'PUBLIC':PUBLIC,'SOURCE':SOURCE}
    exec(compile(raw,'<actual current six XML safe projection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
