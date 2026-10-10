"""New-only read-only proof; exact OS password path is not a business dispatcher."""
import ast
from pg1002_cold_readonly import capture
from pg1029_cold_handoff_preflight_v2 import payload as previous


def payload():
    raw = previous().replace('pg1029-cold-handoff-preflight-v2', 'pg1030-cold-handoff-preflight-v3')
    raw = raw.replace('PG1029_REFUSED', 'PG1030_REFUSED')
    old = " for line in units.splitlines():\n  f=line.split();require(len(f)>=4 and f[2]not in ('active','activating','reloading')and f[3]not in ('waiting','running'))\n result['timerPathUnitsSha256']=hashlib.sha256(units.encode()).hexdigest()"
    new = " props=command(['systemctl','show','systemd-ask-password-console.path','--property=Id,LoadState,ActiveState,SubState,Job,Paths,Triggers,FragmentPath,DropInPaths'],4096).decode()\n pairs=[line.split('=',1)for line in props.splitlines()];console=dict(pairs);require(len(pairs)==len(console))\n result['timerPathClassification']=contract.timer_path_classification(units,console)"
    if raw.count(old) != 1:
        raise ValueError('fixed OS unit observation refused')
    raw = raw.replace(old, new)
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    capture('pg1030-cold-handoff-preflight-v3', payload())
