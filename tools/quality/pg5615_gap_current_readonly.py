"""Fresh deployed identity after observation gap; prior success is not current permission."""
import types
import pg5602_current_vm_reauthentication as previous

SLOT='pg5615-gap-current-readonly-v1'


if __name__=='__main__':
    entry=types.FunctionType(previous.main.__code__,{**vars(previous),'SLOT':SLOT})
    raise SystemExit(entry())
