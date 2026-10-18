"""New-only corrected stage/verify/finite execute; original refused slot remains immutable."""
import inspect
import sys
import pg5086_current_bootstrap_dispatch as previous
import pg5102_corrected_bootstrap_sources as role

W = role.W
SLOT = 'pg5106-corrected-bootstrap'
REMOTE = '/home/ubuntu/pg5106-corrected-bootstrap-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
STAGE = previous.STAGE


def namespace():
    template = previous.previous.previous
    ns = {**vars(template), 'role': role, 'W': W, 'SLOT': SLOT, 'REMOTE': REMOTE,
          'GUEST': GUEST, 'STAGE': STAGE, 'authenticate_host': role.before.admission.authenticate_host}
    fixed = inspect.getsource(template.fixed).replace('pg4824-frozen-v1.safe.json', 'pg5104-frozen-v1.safe.json')
    main = inspect.getsource(template.main).replace('Pg4820', 'Pg5102').replace('PG4702', 'PG4980')
    exec(compile(fixed + '\n' + main, '<one corrected closed stage/verify/execute>', 'exec'), ns)
    return ns


if __name__ == '__main__':
    if sys.argv[1:] not in (['stage'], ['verify'], ['execute']):
        raise SystemExit('one explicit corrected new phase')
    raise SystemExit(namespace()['main']())
