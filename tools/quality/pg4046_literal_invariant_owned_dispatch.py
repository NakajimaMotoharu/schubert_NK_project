"""Once-only owned stage/stop after genuine same-source composite and parent18."""
import inspect
import sys
import pg3494_outbox_owned_dispatch as template
import pg4042_literal_invariant_owned_sources as role

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg4046-literal-invariant-owned-stage-v1'
ARCHIVE = 'pg4046-' + role.TOOLS + '.tar'


def namespace():
    values = {**template.__dict__, 'role': role, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE}
    exec(compile(inspect.getsource(template.namespace), '<new exact owned-stop action namespace>', 'exec'), values)
    return values['namespace']()


def main():
    if sys.argv[1:] not in (['stage'], ['stop']): raise ValueError('one explicit new stage or normal owned stop only')
    return namespace()['main']()


if __name__ == '__main__': raise SystemExit(main())
