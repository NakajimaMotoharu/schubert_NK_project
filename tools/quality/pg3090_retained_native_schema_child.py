"""Fresh210904 child identity/four FD capture, no historical actor used."""
import types
import pg3072_retained_browser_child as template
from pg3088_retained_native_schema_readonly import host_owner

SLOT = 'pg3090-retained-native-schema-child-v1'
BODY = template.BODY
for old, new in [('pg3072-retained-browser-child-v1', SLOT), ('208849', '210904'), ('2423591', '2505343'), ('3ea1a485e65e91c73cb0c7a404cb956186581d38587e15751b353fed2e1263ed', '986f027bee00bad890fde1869ba6411ff60514f7c86be3ce2109e2161246124d'), ('208880', '210935')]:
    BODY = BODY.replace(old, new)


def main():
    fn = template.previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'BODY': BODY, 'host_owner': host_owner}, 'native_schema_current_child_readonly')()


if __name__ == '__main__':
    raise SystemExit(main())
