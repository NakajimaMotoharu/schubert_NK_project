"""Finite new-only normal stage/ownedstop, gated by current composite seal."""
import inspect
import sys
import pg3494_outbox_owned_dispatch as template
import pg3600_current_browser_owned_sources as role

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg3604-current-browser-owned-stage-v1'
ARCHIVE='pg3604-'+role.TOOLS+'.tar'
BOM=role.BOM
TOOLS=role.TOOLS


def namespace():
    ns={**template.__dict__,'role':role,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE}
    exec(compile(inspect.getsource(template.namespace),'<actual current Browser stop dispatch>','exec'),ns);return ns['namespace']()


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('separate new-only stage or ownedstop required')
    return namespace()['main']()


def stage():return namespace()['stage']()


def run_source():return namespace()['run_source']()


if __name__=='__main__':raise SystemExit(main())
