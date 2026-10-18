"""First new-only normal owned stage/stop; both full pre-stop outputs distinct and fresh."""
import inspect
import sys
import types
import pg5064_current_owned_dispatch as previous
import pg5496_current_owned_sources as role
from pg5476_current_admission_image import live,authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5500-current-owned-stage-v1'
ARCHIVE='pg5500-'+role.TOOLS+'.tar'
rename_output=previous.rename_output


def unwrap_post(raw):
    template=previous.previous.previous.previous
    ns={**vars(template),'rename_output':rename_output}
    source=inspect.getsource(template.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1','pg5501-newboot-pre-stop-full-v1')
    exec(compile(source,'<fresh actual296 pre-stop two outputs>','exec'),ns)
    return ns['unwrap_post'](raw)


def namespace():
    ns={**vars(previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'unwrap_post':unwrap_post,'live':live}
    return types.FunctionType(previous.namespace.__code__,ns)()


if __name__=='__main__':
    if sys.argv[1:]not in(['stage'],['stop']):raise SystemExit('one explicit normal stage|stop')
    authenticate_host();raise SystemExit(namespace()['main']())
