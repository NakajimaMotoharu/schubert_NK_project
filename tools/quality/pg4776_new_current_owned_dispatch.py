"""New-only normal reverse owned stop; same current immutable normal chain required."""
import inspect
import sys
import pg4286_current_owned_dispatch as previous
import pg4772_new_current_owned_sources as role
from pg4752_new_current_admission_image import live,authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4776-new-current-owned-stage-v1'
ARCHIVE='pg4776-'+role.TOOLS+'.tar'
rename_output=previous.rename_output


def unwrap_post(raw):
    source=inspect.getsource(previous.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1','pg4779-newboot-pre-stop-full-v1')
    ns={**vars(previous),'rename_output':rename_output}
    exec(compile(source,'<explicit new normal pre-stop output>','exec'),ns);return ns['unwrap_post'](raw)


def namespace():
    ns={**vars(previous.previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(previous.previous.namespace),'<new normal owned namespace>','exec'),ns)
    result=ns['namespace']();original=result['run_source'];result['run_source']=lambda:unwrap_post(original())
    result['post_payload']=lambda:role.composite_payload(live());return result


if __name__=='__main__':
    if sys.argv[1:]not in (['stage'],['stop']):raise SystemExit('explicit new-only stage|normal stop')
    authenticate_host();raise SystemExit(namespace()['main']())
