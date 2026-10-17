"""First new-only normal owned stage/stop; SAVE and RAW_SAVE always distinct/fresh."""
import inspect
import sys
import pg4776_new_current_owned_dispatch as previous
import pg4916_current_owned_sources as role
from pg4900_current_admission_image import live,authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4920-current-owned-stage-v1'
ARCHIVE='pg4920-'+role.TOOLS+'.tar'


def rename_output(raw,expected,slot):
    import ast
    from collections import Counter
    from immutable_payload_binding import PROTECTED
    def capsules(value):
        return Counter(ast.get_source_segment(value,n)for n in ast.walk(ast.parse(value))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))
    original=capsules(raw);tree=ast.parse(raw)
    for name,old,new in [('SAVE',expected,slot),('RAW_SAVE',expected+'-raw',slot+'-raw')]:
        nodes=[n for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id==name]
        # Full seal includes the immutable imported helper's inactive default
        # before the one final output binding. Preserve exactly that declaration;
        # neither an arbitrary earlier slot nor a second final binding is allowed.
        if name=='SAVE'and len(nodes)==2:
            known=ast.parse("BASE / 'pg1562-pending-runtime-v1'",mode='eval').body
            if ast.dump(nodes[0].value)!=ast.dump(known):raise ValueError('only known imported default before final SAVE')
        elif len(nodes)!=1:raise ValueError('one explicit '+name+' final output, never protected capsules')
        node=nodes[-1];v=node.value
        if not(isinstance(v,ast.BinOp)and isinstance(v.op,ast.Div)and isinstance(v.left,ast.Name)and v.left.id=='BASE'and isinstance(v.right,ast.Constant)and v.right.value==old):
            raise ValueError('exact original '+name+' evidence slot')
        raw=raw.replace(ast.get_source_segment(raw,node),name+'=BASE/'+repr(new),1);tree=ast.parse(raw)
    if capsules(raw)!=original:raise ValueError('all immutable SQL/history/Browser capsules unchanged')
    return raw


def unwrap_post(raw):
    ns={**vars(previous.previous),'rename_output':rename_output}
    source=inspect.getsource(previous.previous.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1','pg4923-newboot-pre-stop-full-v1')
    exec(compile(source,'<both fresh outputs inside actual pre-stop transport>','exec'),ns)
    return ns['unwrap_post'](raw)


def namespace():
    ns={**vars(previous.previous.previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(previous.previous.previous.namespace),'<normal04bb owned namespace>','exec'),ns)
    result=ns['namespace']();original=result['run_source'];result['run_source']=lambda:unwrap_post(original())
    result['post_payload']=lambda:role.composite_payload(live());return result


if __name__=='__main__':
    if sys.argv[1:]not in (['stage'],['stop']):raise SystemExit('one explicit normal stage|stop')
    authenticate_host();raise SystemExit(namespace()['main']())
