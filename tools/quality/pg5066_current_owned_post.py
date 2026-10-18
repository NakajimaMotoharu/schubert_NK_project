"""Independent current original/24/native/resource post after genuine5064 stop only."""
import inspect
import pg4922_current_owned_post as previous
import pg5060_current_owned_sources as role
from pg5036_current_admission_image import live, authenticate_host

SLOT = 'pg5066-current-owned-post-v1'


def namespace():
    template = previous.previous.previous
    ns = {**vars(template), 'role': role, 'SLOT': SLOT}
    exec(compile(inspect.getsource(template.namespace), '<currenta2ecc independent full stop post>', 'exec'), ns)
    result = ns['namespace']()
    def payload(seals):
        b = live()
        qualified = {'binding': {k: v for k, v in b.items() if k != 'rootPid'}, 'rootPid': b['rootPid']}
        return result['emit'](seals, role.context(), qualified)
    result['payload'] = payload
    source = role.bind(inspect.getsource(previous.previous.entry_source.entry))
    env = {**result['entry'].__globals__, 'payload': payload}
    exec(compile(source, '<exact actual first5064 independent post selector>', 'exec'), env)
    if (env['entry'].__code__.co_code != result['entry'].__code__.co_code
            or env['entry'].__code__.co_consts != result['entry'].__code__.co_consts):
        raise ValueError('exact full post factory, no synthetic successful selector')
    result['entry'] = env['entry']
    return result


if __name__ == '__main__':
    authenticate_host()
    raise SystemExit(namespace()['entry']()())
