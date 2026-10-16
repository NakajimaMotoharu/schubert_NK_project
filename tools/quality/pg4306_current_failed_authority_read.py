"""Current failed four-actor detailed read; full configuration/FD/NSS, zero operation authority."""
import inspect
import pg4080_failed_ordinary_full_capture as previous
import pg4300_current_failed_capture as current
from pg4060_original_profile_dual_stack import once

SLOT='pg4306-current-failed-authority-read-v1'


def payload():
    prefix=current.payload();prefix=prefix[:prefix.index('import dbus\nbus=')].replace(current.SLOT,SLOT)
    body=previous.BODY
    guard="require(current.resolve(strict=True)==root and manifest.read_bytes()==raw and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)"
    body=once(body,guard,guard+"\nrequire(not Path('/proc/795724').exists())")
    return prefix+'\n'+previous.contracts()+'\nACTOR_POLICY='+repr(inspect.getsource(previous.policy))+'\n'+body


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<new current four-actor detailed read>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
