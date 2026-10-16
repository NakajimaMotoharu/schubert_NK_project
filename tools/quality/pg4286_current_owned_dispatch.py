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


def unwrap_post(raw):
    marker="post = json.loads((W / POST_SLOT / 'manifest.safe.json').read_bytes())"
    return once(raw,marker,marker+"\n    post = {**post['result'], 'actualExit':post['actualExit'], 'productionSource':post['source']}")


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
