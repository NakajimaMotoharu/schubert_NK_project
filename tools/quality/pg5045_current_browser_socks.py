"""New owned loopback SOCKS after local reboot; no VM/business operation."""
import inspect
import json
from pathlib import Path
import types
import pg2882_network_chr_socks as previous
import pg1191_chr_socks_owner as owner
from pg4996_resume_connection import authenticate_host, process
from pg1446_current_cold_stage import W

SLOT = 'pg5045-current-browser-socks-v1'


def owned_socks():
    value = json.loads((W / SLOT / 'running.safe.json').read_bytes())
    if (value.get('localBoot') != Path('/proc/sys/kernel/random/boot_id').read_text().strip()
            or process(value['parent']['pid']) != value['parent']):
        raise ValueError('current SOCKS parent generation required')
    expected = {'pid': value['pid'], 'ticks': value['ticks'], 'argvSha256': value['argvSha256'],
                'executable': '/usr/bin/ssh', 'ppid': value['parentPid'],
                'uids': (1000, 1000, 1000, 1000), 'gids': (1000, 1000, 1000, 1000),
                'listenerAddresses': ('0100007F:D781',)}
    ns = {**vars(owner), 'EXPECTED': expected}
    for name in ('qualify', 'capture', 'require_owner'):
        ns[name] = types.FunctionType(getattr(owner, name).__code__, ns)
    return ns['require_owner']()


def main():
    authenticate_host()
    ns = {**vars(previous), 'SLOT': SLOT, 'process': process}
    raw = inspect.getsource(previous.main)
    marker = "value={'pid':child.pid"
    if raw.count(marker) != 1:
        raise ValueError('one fresh local-boot SOCKS receipt boundary')
    raw = raw.replace(marker, "value={'localBoot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'parent':process(os.getpid()),'pid':child.pid", 1)
    exec(compile(raw, '<new-only owned current Browser SOCKS>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
