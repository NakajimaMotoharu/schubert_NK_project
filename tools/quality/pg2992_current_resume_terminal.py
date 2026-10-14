"""Same-source/current new activation genuine DONE/PID1 proof, read-only."""
import inspect
import pg2878_network_newcurrent_terminal as previous
import pg2021_fresh_resume_terminal_receipt as transport
from pg2982_current_resume_observer import SOURCE

SLOT = 'pg2992-current-resume-terminal-v1'


def payload(binding):
    if binding.get('activation') == '74729e17-91c0-43e7-b01f-74f9e6461d6a':
        raise ValueError('original completed activation is not fresh activation')
    return previous.payload(binding).replace(previous.SLOT, SLOT)


def main():
    raw = inspect.getsource(transport.main).replace('pg2019-fresh-resume-live-binding-complete-v1', 'pg2990-current-resume-live-binding-v1').replace('pg2010-parent-watch-v1', 'pg2982-parent-watch-v1')
    raw = raw.replace("payload(actual['binding'])", "payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<current fresh genuine terminal dispatcher>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
