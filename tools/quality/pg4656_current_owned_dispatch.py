"""New-only normal reverse stop; current certificate and unmodified immutable capsules."""
import inspect
import sys
import pg4286_current_owned_dispatch as previous
import pg4652_current_owned_sources as role
from pg4584_current_admission_image import live

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4656-current-owned-stage-v1'
ARCHIVE='pg4656-'+role.TOOLS+'.tar'
rename_output=previous.rename_output


def unwrap_post(raw):
    source=inspect.getsource(previous.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1','pg4659-newboot-pre-stop-full-v1')
    ns={**vars(previous),'rename_output':rename_output}
    exec(compile(source,'<current explicit receipt and output unwrap>','exec'),ns);return ns['unwrap_post'](raw)


def namespace():
    ns={**vars(previous.previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(previous.previous.namespace),'<new owned namespace>','exec'),ns)
    result=ns['namespace']();original=result['run_source']
    result['run_source']=lambda:unwrap_post(original())
    result['post_payload']=lambda:role.composite_payload(live())
    return result


if __name__=='__main__':
    if sys.argv[1:]not in (['stage'],['stop']):raise SystemExit('explicit new-only stage|normal stop')
    raise SystemExit(namespace()['main']())
