"""Current child's actual start/argv/four FD capture; single queued, no signal."""
import types
import pg2962_retained_child_readonly as previous
from pg3070_retained_browser_readonly import host_owner

SLOT = 'pg3072-retained-browser-child-v1'
BODY = previous.BODY
for old, new in [('pg2962-retained-child-readonly-v1', SLOT), ('118988', '208849'), ('1642675', '2423591'), ('74aa0c400f2cce31c86c72fa4b37c41b60bb8230e656c3753e2a32159d6a4b40', '3ea1a485e65e91c73cb0c7a404cb956186581d38587e15751b353fed2e1263ed'), ('119019', '208880')]:
    BODY = BODY.replace(old, new)


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'BODY': BODY, 'host_owner': host_owner}, 'current_child_readonly')()


if __name__ == '__main__':
    raise SystemExit(main())
