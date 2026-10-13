"""BUG1203: fixed four-seal fresh closure; only new retire action, reuse immutable successful stage."""
import inspect
import os
import sys
import pg2052_fresh_runtime_retirement_dispatch as prior
from pg2040_fresh_normal_warning_terminal_post import SEALS
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate


def post_payload():
    raw=inspect.getsource(prior.post_payload)
    old="seals={name:value['sha256']for name,value in post['proofHashes'].items()}"
    if raw.count(old)!=1:raise ValueError('one fixed seal projection boundary required')
    raw=raw.replace(old,"seals={name:post['proofHashes'][name]['sha256']for name in SEALS}")
    ns={**prior.__dict__,'SEALS':SEALS}
    exec(compile(raw,'<actual fixed four seal current stopped payload>','exec'),ns);return ns['post_payload']()


def run_action(action):
    if action!='retire':raise ValueError('existing qualified stage must not be replayed')
    stage=prior.runner.json.loads((W/'pg2052-stage-v1.safe.json').read_bytes())
    if stage['actualExit']!=0 or stage['sourceQualified']is not True:raise ValueError('actual qualified unchanged stage required')
    raw=inspect.getsource(prior.run_action)
    anchor="raw=inspect.getsource(runner.run_action)"
    if raw.count(anchor)!=1:raise ValueError('one existing-stage guard binding required')
    raw=raw.replace(anchor,anchor+"\n    raw=raw.replace(\"W/'pg1826-stage-v1.exit'\",\"W/'pg2052-stage-v1.exit'\")\n    raw=raw.replace(\"'managerFailureRetained':True\",\"'oldRoot13ManagerFailureRetained':True,'normalUnit0or10':True,'currentManagerGc':True\")")
    raw=raw.replace("replace('pg1826','pg2052').replace('pg1827','pg2053')","replace('pg1826','pg2056').replace('pg1827','pg2057')").replace('pg2054-stopped-runtime-pre-retire-fresh-v1','pg2058-stopped-runtime-pre-retire-fresh-v1')
    raw=raw.replace("'post_payload':post_payload","'post_payload':post_payload")
    ns={**prior.__dict__,'run_action':run_action,'post_payload':post_payload}
    exec(compile(raw,'<new retire existing immutable stage fixed seals>','exec'),ns);return ns['run_action'](action)


def main():
    if sys.argv[1:]!=['retire']:raise ValueError('new retire only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action('retire')


if __name__=='__main__':raise SystemExit(main())
