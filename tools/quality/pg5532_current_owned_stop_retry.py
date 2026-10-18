"""BUG1455: reuse actual stage/ABI, new-only stop attempt and every auxiliary output.

No second stage, Root or Browser. The failed5500.requested remains untouched.
"""
import types
import pg5500_current_owned_dispatch as previous
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P,W

PARENT='pg5531-parent-two-source-prequalification-v1'
PRESTOP='pg5533-newboot-pre-stop-full-v1'
ATTEMPT='pg5532-stop-v1'


def output_paths(base):
    return[base/(ATTEMPT+suffix)for suffix in('.requested','.private.log','.exit','.safe.json')]+[
        base/(slot+suffix)for slot in(PARENT,PRESTOP)for suffix in('.private.log','.safe.json')]


def ensure_outputs(base):
    if any(path.exists()or path.is_symlink()for path in output_paths(base)):
        raise ValueError('new-only stop and every auxiliary output must be absent before SSH')


def run_source():
    raw=previous.namespace()['run_source']()
    changes={"('pg5500-' + action + '-v1')":"('pg5532-' + action + '-v1')",
        'pg5063-parent-two-source-prequalification-v1':PARENT,
        'pg5501-newboot-pre-stop-full-v1':PRESTOP}
    for before,after in changes.items():
        if before not in raw:raise ValueError('explicit stop-only output role missing '+before)
        raw=raw.replace(before,after)
    old='capture_output=True, timeout=120'
    if raw.count(old)!=1:raise ValueError('one read-only full-chain transport timeout, separate from Root budget')
    # Actual5526 took 164s including host construction; the doubled preservation
    # chain must not be interrupted by the legacy one-cohort 120s client budget.
    # No Root/Unit deadline, Browser clock condition or ownership guard changes.
    raw=raw.replace(old,'capture_output=True, timeout=300',1)
    # Both stderr files are CREATE_NEW; never alter an old log before safe open.
    for slot in(PARENT,PRESTOP):
        old="(W / '"+slot+".private.log').write_bytes(r.stderr)"
        if raw.count(old)!=1:raise ValueError('one exact auxiliary stderr writer')
        raw=raw.replace(old,"with (W / '"+slot+".private.log').open('xb') as preserved_error:\n            preserved_error.write(r.stderr)",1)
    if "'pg5500-stage-v1.exit'"not in raw:raise ValueError('reuse actual stage, never synthesize new stage success')
    compile(raw,'<new-only original unused owned-stop retry>','exec')
    return raw


def action():
    ensure_outputs(W)
    constructor=previous.namespace()['run_action']
    env={**constructor.__globals__,'run_source':run_source}
    return types.FunctionType(constructor.__code__,env)('stop')


def main():
    ensure_outputs(W)
    previous.authenticate_host()
    with management_gate(P/'current-management-critical.lock'):return action()


if __name__=='__main__':raise SystemExit(main())
