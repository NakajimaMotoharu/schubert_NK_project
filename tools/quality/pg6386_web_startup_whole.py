"""Necessary grouped4052 whole: SS324 Main and four independent new Test methods."""
import inspect
import pg6188_native_ownership_whole as base
from pg6384_web_fatal_callback_retry_qualification import original_source

LABEL = 'PG6386'
SLOT = 'pg6386-web-startup-six-v1'


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source}
    for name in ('declared_inventory', 'server_source', 'driver_source', 'prerequisites', 'main'):
        raw = inspect.getsource(getattr(base, name))
        for before, after in (
            ('4023', '4052'), ('605', '608'), ('pg6188', 'pg6386'),
            ('PG6184-unstarted-management-qualification-v1', 'PG6384-web-fatal-callback-retry-qualification-v1'),
            ('pg6184-unstarted-management-qualification-v1', 'pg6384-web-fatal-callback-retry-qualification-v1'),
            ('PG6186-native-ownership-order-v1', 'PG6380-web-startup-order-v1'),
            ('(59,20,1667)', '(22,8,1667)'), ('original59', 'original22'), ('Original59', 'Original22'),
            ('SS313..317 ownership regression', 'SSC324 Web startup and callback regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.',
             'SSC324 caller-owned startup retention; Life TERM and fatal runtime callback; four new method identities since original4048.')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<necessary4052 '+name+'>', 'exec'), scope)
    return scope


def declared_inventory(): return definitions()['declared_inventory']()
def server_source(head, digest): return definitions()['server_source'](head, digest)
def driver_source(fresh): return definitions()['driver_source'](fresh)
def prerequisites(source): return definitions()['prerequisites'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
