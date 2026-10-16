"""New-only stage/normal owned stop; generic receipt is unwrapped explicitly, never synthesized."""
import inspect
import sys
import pg4046_literal_invariant_owned_dispatch as previous
import pg4282_current_owned_sources as role
import pg4272_current_browser_composite as composite
from pg4260_stable_admission_image import live
from pg4060_original_profile_dual_stack import once

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4286-current-owned-stage-v1'
ARCHIVE='pg4286-'+role.TOOLS+'.tar'


def rename_output(raw,expected,slot):
    import ast
    from collections import Counter
    from immutable_payload_binding import PROTECTED
    def capsules(value):
        return Counter(ast.get_source_segment(value,n)for n in ast.walk(ast.parse(value))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets))
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='SAVE']
    if not nodes:raise ValueError('one final fixed output assignment required')
    node=nodes[-1];value=node.value
    if not(isinstance(value,ast.BinOp)and isinstance(value.op,ast.Div)and isinstance(value.left,ast.Name)and value.left.id=='BASE'and isinstance(value.right,ast.Constant)and value.right.value==expected and node.lineno==node.end_lineno):raise ValueError('exact final output role required')
    lines=raw.splitlines(keepends=True);line=lines[node.lineno-1]
    if not line.isascii():raise ValueError('canonical output definition required')
    lines[node.lineno-1]=line[:node.col_offset]+'SAVE = BASE / '+repr(slot)+line[node.end_col_offset:]
    result=''.join(lines)
    if capsules(result)!=capsules(raw):raise ValueError('every immutable capsule must remain exact')
    return result


def unwrap_post(raw):
    marker="post = json.loads((W / POST_SLOT / 'manifest.safe.json').read_bytes())"
    raw=once(raw,marker,marker+"\n    post = {**post['result'], 'actualExit':post['actualExit'], 'productionSource':post['source']}")
    raw=once(raw,"fresh = post_payload().replace(POST_SLOT, 'pg4289-newboot-pre-stop-full-v1')","fresh = rename_output(post_payload(), POST_SLOT, 'pg4289-newboot-pre-stop-full-v1')")
    return inspect.getsource(rename_output)+'\n'+raw


def namespace():
    ns={**vars(previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(previous.namespace),'<new owned transport namespace>','exec'),ns)
    result=ns['namespace']();original=result['run_source']
    result['run_source']=lambda:unwrap_post(original())
    result['post_payload']=lambda:composite.payload(live())
    return result


if __name__=='__main__':
    if sys.argv[1:]not in (['stage'],['stop']):raise SystemExit('explicit new-only stage/stop')
    raise SystemExit(namespace()['main']())
