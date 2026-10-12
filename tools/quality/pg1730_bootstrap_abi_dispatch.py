"""Fresh120-file Bootstrap version; current recovery post and VM ABI oracle."""
import sys
from pathlib import Path
import pg1721_current_bootstrap_dispatch as prior
from pg1728_bootstrap_abi_sources import bind
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P

def source():
    raw=bind(prior.source()).replace('pg1720-frozen-v1','pg1729-frozen-v1').replace('pg1721','pg1730')
    marker="    frozen=json.loads("
    at=raw.index(marker)
    raw=raw[:at]+"""    recovery=json.loads((W/'pg1727-bootstrap-recovery-full-post-v1/manifest.safe.json').read_bytes())
    assert recovery['actualExit']==0 and recovery['guest']['beforeSha256']==before['beforeSha256']and recovery['guest']['ownedJavaDbAdvisoryMA0']is True
"""+raw[at:]
    old="commands=[(SSH+[prefix+'Pg1728BootstrapArgumentTest'],None),(SSH+[prefix+'Pg1728BootstrapExisting '+action],None)]"
    new="commands=[(SSH+[prefix+'Pg1728BootstrapArgumentTest'],None),(SSH+[prefix+'Pg1728BootstrapExpectedTest'],None),(SSH+[prefix+'Pg1728BootstrapExisting '+action],None)]"
    if raw.count(old)!=1:raise ValueError('one VM before-ownership constructor fixture boundary required')
    raw=raw.replace(old,new)
    compile(raw,'<new current Bootstrap ABI dispatch>','exec');return raw

def main():
    if sys.argv[1:]not in (['stage'],['verify'],['execute']):raise ValueError('exact three Bootstrap phases required')
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg1730_bootstrap_abi_dispatch.py'),'__name__':'current_bootstrap_abi_dispatch'}
    exec(compile(source(),'<new current Bootstrap transport>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):
        return ns['main']()

if __name__=='__main__':raise SystemExit(main())
