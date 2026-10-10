"""New pin namespace distinct from preserved old helper namespace."""
import ast
import inspect
from pg1154_native_failed_owner_proof_v2 import payload as previous
import pg1120_current_failed_capture as transport


def payload():
    s=previous().replace('native-failed-owner-proof-v2','native-failed-owner-proof-v3')
    if not s.startswith('FILES='):raise ValueError('fixed new pin insertion refused')
    s='NATIVE_FILES='+s[len('FILES='):]
    i=s.index('JAVA=410279');s=s[:i]+s[i:].replace('FILES','NATIVE_FILES')
    tree=ast.parse(s)
    def stores(n,name):
        if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Lambda)):return 0
        return int(isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)and n.id==name)+sum(stores(c,name)for c in ast.iter_child_nodes(n))
    if any(stores(tree,name)!=1 for name in ['NATIVE_FILES','FILES','before','CURRENT']):raise ValueError('immutable separate pins refused')
    return s


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1155-native-failed-owner-proof-v3').replace('PG1120-current-failed-capture-v1','PG1155-native-failed-owner-proof-v3')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<separate native pin namespace>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
