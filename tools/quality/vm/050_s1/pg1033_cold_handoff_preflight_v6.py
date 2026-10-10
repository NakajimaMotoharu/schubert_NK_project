"""Fresh readonly proof with exact producer/path/run trace binding."""
from pg1002_cold_readonly import capture
from pg1032_cold_handoff_preflight_v5 import payload as previous


def payload():
    raw = previous()
    if raw.count("'PG1028-cold-handoff-preflight-v1'") != 1:
        raise ValueError('fixed old producer literal refused')
    raw = raw.replace('pg1032-cold-handoff-preflight-v5', 'pg1033-cold-handoff-preflight-v6')
    raw = raw.replace('PG1028-cold-handoff-preflight-v1', 'PG1033-cold-handoff-preflight-v6')
    raw = raw.replace('PG1032_REFUSED', 'PG1033_REFUSED')
    return raw


if __name__ == '__main__':
    capture('pg1033-cold-handoff-preflight-v6', payload())
