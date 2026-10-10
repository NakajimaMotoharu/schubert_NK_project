"""Business and post oracle inside actual metadata Ref lifetime, save after close."""
import ast
import inspect
import pg1257_fresh_independent_terminal_post as transport
import pg1266_fresh_log_independent_capture as previous
import pg1267_fresh_before_provenance as provenance
from pg1268_fresh_log_independent_capture_v2 import before_receipt


def extend_scope(prefix, business):
    tree=ast.parse(prefix)
    if not tree.body or not isinstance(tree.body[-1],ast.Try) or tree.body[-1].handlers or not tree.body[-1].finalbody:
        raise ValueError('explicit metadata try/finally lifetime required')
    tree.body[-1].body.extend(ast.parse(business).body)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def payload(seals):
    if seals!=previous.SEALS:raise ValueError('current actual fixed stop seals required')
    prefix=transport.payload(seals)
    marker="result={'actualExit':0,'run':'PG1257-fresh-terminal-post-v1'"
    if prefix.count(marker)!=1:raise ValueError('fixed Ref lifetime end insertion required')
    prefix=prefix[:prefix.index(marker)]
    body=previous.BODY.replace('pg1266-fresh-independent-log-v1','pg1269-fresh-scoped-log-v3').replace('PG1266-fresh-independent-log-v1','PG1269-fresh-scoped-log-v3')
    old="old=json.loads(old_raw)['current'];require(old['source']==data['source']['commit'])"
    if body.count(old)!=1:raise ValueError('fixed before schema join required')
    body=body.replace(old,"authority=types.ModuleType('explicit_before_provenance');exec(BEFORE_SOURCE,authority.__dict__);old=json.loads(old_raw)['current'];authority.verify(BEFORE_RECEIPT,old);require(BEFORE_RECEIPT['productionSource']==data['source']['commit'])")
    cut=body.index("save=base/'pg1269-fresh-scoped-log-v3'")
    definitions='INDEPENDENT_SOURCE='+repr(previous.independent_source())+'\nBEFORE_SOURCE='+repr(inspect.getsource(provenance))+'\nBEFORE_RECEIPT='+repr(before_receipt())+'\n'
    s=definitions+extend_scope(prefix,body[:cut])+"\nresult['normalNewMetadataScopes']=True\n"+body[cut:]
    compile(s,'<whole actual scoped fresh Log v3>', 'exec');return s


def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1269-fresh-scoped-log-v3')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only scoped Log actual transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
