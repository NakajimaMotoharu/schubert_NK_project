"""One new closed current stage/verify/existingADMIN20; no Root or foreign operations."""
import inspect
import sys
import pg4936_current_bootstrap_dispatch as previous
import pg5082_current_bootstrap_sources as role

W = role.W
SLOT = 'pg5086-current-bootstrap'
REMOTE = '/home/ubuntu/pg5086-current-bootstrap-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
STAGE = previous.STAGE.replace('PG4860', 'PG4980')


def namespace():
    template = previous.previous
    ns = {**vars(template), 'role': role, 'W': W, 'SLOT': SLOT, 'REMOTE': REMOTE,
          'GUEST': GUEST, 'STAGE': STAGE, 'authenticate_host': role.before.admission.authenticate_host}
    fixed = inspect.getsource(template.fixed).replace('pg4824-frozen-v1.safe.json', 'pg5084-frozen-v1.safe.json')
    main = inspect.getsource(template.main).replace('Pg4820', 'Pg5082').replace('PG4702', 'PG4980')
    exec(compile(fixed + '\n' + main, '<current one closed existing20 transport>', 'exec'), ns)
    return ns


if __name__ == '__main__':
    if sys.argv[1:] not in (['stage'], ['verify'], ['execute']):
        raise SystemExit('one current existing20 phase required')
    raise SystemExit(namespace()['main']())
