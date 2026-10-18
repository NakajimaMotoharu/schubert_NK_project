"""First new-only normal owned stage/stop; SAVE and RAW_SAVE distinct and fresh."""
import inspect
import sys
import pg4920_current_owned_dispatch as previous
import pg5060_current_owned_sources as role
from pg5036_current_admission_image import live, authenticate_host

GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS
REMOTE = '/home/ubuntu/pg5064-current-owned-stage-v1'
ARCHIVE = 'pg5064-' + role.TOOLS + '.tar'
rename_output = previous.rename_output


def unwrap_post(raw):
    template = previous.previous.previous
    ns = {**vars(template), 'rename_output': rename_output}
    source = inspect.getsource(template.unwrap_post).replace('pg4289-newboot-pre-stop-full-v1', 'pg5065-newboot-pre-stop-full-v1')
    exec(compile(source, '<both fresh actual pre-stop outputs>', 'exec'), ns)
    return ns['unwrap_post'](raw)


def namespace():
    template = previous.previous.previous.previous
    ns = {**vars(template), 'role': role, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE}
    exec(compile(inspect.getsource(template.namespace), '<normal a2ecc owned namespace>', 'exec'), ns)
    result = ns['namespace']()
    original = result['run_source']
    result['run_source'] = lambda: unwrap_post(original())
    result['post_payload'] = lambda: role.composite_payload(live())
    return result


if __name__ == '__main__':
    if sys.argv[1:] not in (['stage'], ['stop']):
        raise SystemExit('one explicit normal stage|stop')
    authenticate_host()
    raise SystemExit(namespace()['main']())
