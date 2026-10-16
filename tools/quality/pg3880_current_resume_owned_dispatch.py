"""Separate new-only stage and normal four-owned stop, no historical stop replay."""
import inspect
import sys
import pg3494_outbox_owned_dispatch as template
import pg3876_current_resume_owned_sources as role

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg3880-current-resume-owned-stage-v1'
ARCHIVE='pg3880-'+role.TOOLS+'.tar'
TOOLS=role.TOOLS
BOM=role.BOM


def namespace():
    values={**template.__dict__,'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(template.namespace),'<current resume exact owned-stop namespace>','exec'),values)
    return values['namespace']()


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('separate once-only stage or ownedstop required')
    return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
