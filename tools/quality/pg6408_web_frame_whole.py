"""One necessary4054 whole after one Main and two independent retention Test classes."""
import inspect
import pg6188_native_ownership_whole as base
from pg6414_web_frame_pending_qualification import original_source

LABEL = 'PG6408'
SLOT = 'pg6408-web-frame-six-v1'


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source}
    for name in ('declared_inventory', 'server_source', 'driver_source', 'prerequisites', 'main'):
        raw = inspect.getsource(getattr(base, name))
        for before, after in (
            ('4023', '4054'), ('605', '610'), ('pg6188', 'pg6408'),
            ('PG6184-unstarted-management-qualification-v1', 'PG6414-web-frame-pending-qualification-v1'),
            ('pg6184-unstarted-management-qualification-v1', 'pg6414-web-frame-pending-qualification-v1'),
            ('PG6186-native-ownership-order-v1', 'PG6402-web-frame-order-v1'),
            ('(59,20,1667)', '(26,12,1667)'), ('original59', 'original26'), ('Original59', 'Original26'),
            ('SS313..317 ownership regression', 'SSC325 normal and exceptional Web borrowed-frame regression'),
            ('SSC317 unstarted management stop remains UNKNOWN.',
             'SSC325 two finally retaining frames and protected diagnostic; two new Test methods since original4052. Explicit branch applicability requires actual JVM proof, never injected zero.')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<necessary4054 '+name+'>', 'exec'), scope)
    return scope


def declared_inventory(): return definitions()['declared_inventory']()
def server_source(head, digest): return definitions()['server_source'](head, digest)
def driver_source(fresh): return definitions()['driver_source'](fresh)
def prerequisites(source): return definitions()['prerequisites'](source)
def main(): return definitions()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
