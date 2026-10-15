"""New-only v2 tool staging and not-yet-issued normal owned stop, no Root replay."""
import inspect
import sys
import pg3494_outbox_owned_dispatch as previous
import pg3520_outbox_owned_sources_v2 as role

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg3524-outbox-owned-stage-v2'
ARCHIVE = 'pg3524-' + role.TOOLS + '.tar'


def namespace():
    ns = {**previous.__dict__, 'role': role, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE}
    exec(compile(inspect.getsource(previous.namespace), '<v2 exact dispatch composer>', 'exec'), ns)
    return ns['namespace']()


def stage():return namespace()['stage']()


def run_source():return namespace()['run_source']()


def main():
    if sys.argv[1:] not in (['stage'], ['stop']):raise ValueError('new-only v2 stage or stop required')
    return namespace()['main']()


if __name__ == '__main__':raise SystemExit(main())
