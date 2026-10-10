"""New-only readonly retry; old1028 failure and oldJava1023 are unchanged."""
import ast
from pg1002_cold_readonly import capture
from pg1028_cold_handoff_preflight import payload as previous


def payload():
    raw = previous()
    old = 'owned_flocks(actor_fd_locks,lockmeta,3091)'
    if raw.count(old) != 1:
        raise ValueError('fixed FD binding refused')
    raw = raw.replace(old, 'owned_flocks(contract.fd_alias_records(actor_fd_locks),lockmeta,3091)')
    raw = raw.replace('pg1028-cold-handoff-preflight-v1', 'pg1029-cold-handoff-preflight-v2')
    if raw.count('failed=failure') != 1:
        raise ValueError('fixed refusal phase refused')
    raw = raw.replace('failed=failure', 'failed=failure;failed_phase=phase')
    old = "if failed is not None:\n print(json.dumps("
    if raw.count(old) != 1:
        raise ValueError('fixed safe refusal refused')
    raw = raw.replace(old, "if failed is not None:\n print('PG1029_REFUSED phase='+failed_phase+' type='+type(failed).__name__,file=sys.stderr,flush=True)\n print(json.dumps(")
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    capture('pg1029-cold-handoff-preflight-v2', payload())
