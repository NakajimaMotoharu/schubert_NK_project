"""Newonly0ea owned stage/stop; all auxiliary outputs create-new before any SSH."""
import inspect
import sys
import types
import pg5500_current_owned_dispatch as previous
import pg5670_current_owned_sources as role
from pg5644_current_admission_image import live,authenticate_host
from pg1446_current_cold_stage import W

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5674-current-owned-stage-v1'
ARCHIVE='pg5674-'+role.TOOLS+'.tar'
PARENT='pg5673-parent-two-source-prequalification-v1'
PRESTOP='pg5675-newboot-pre-stop-full-v1'
rename_output=previous.rename_output


def unwrap_post(raw):
    template=previous.previous.previous.previous.previous
    ns={**vars(template),'rename_output':rename_output}
    raw_source=inspect.getsource(template.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1',PRESTOP)
    exec(compile(raw_source,'<fresh0ea pre-stop two outputs>','exec'),ns)
    return ns['unwrap_post'](raw)


def fresh_paths(base):
    return[base/('pg5674-stop-v1'+s)for s in('.requested','.private.log','.exit','.safe.json')]+[
      base/(slot+s)for slot in(PARENT,PRESTOP)for s in('.private.log','.safe.json')]


def ensure_outputs(base):
    if any(p.exists()or p.is_symlink()for p in fresh_paths(base)):raise ValueError('all new-only stop/auxiliary paths absent before SSH')


def protect_outputs(raw):
    old='capture_output=True, timeout=120'
    if raw.count(old)!=1:raise ValueError('one independent fullchain transport bound')
    raw=raw.replace(old,'capture_output=True, timeout=300',1)
    for slot in(PARENT,PRESTOP):
        old="(W / '"+slot+".private.log').write_bytes(r.stderr)"
        if raw.count(old)!=1:raise ValueError('one auxiliary stderr writer per new role')
        raw=raw.replace(old,"with (W / '"+slot+".private.log').open('xb') as preserved_error:\n            preserved_error.write(r.stderr)",1)
    return raw


def namespace():
    ns={**vars(previous.previous),'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'unwrap_post':unwrap_post,'live':live}
    result=types.FunctionType(previous.previous.namespace.__code__,ns)();original=result['run_source']
    result['run_source']=lambda:protect_outputs(original())
    return result


def main():
    if sys.argv[1:]not in(['stage'],['stop']):raise ValueError('one explicit stage|stop only')
    if sys.argv[1:]==['stop']:ensure_outputs(W)
    authenticate_host();return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
