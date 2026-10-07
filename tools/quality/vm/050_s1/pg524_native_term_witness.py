"""SSC193194: native capture is an additional TERM postcondition, not Unit success.
No process action. The legacy full journal oracle still authenticates the complete
manager/generation/boot/PID interval and cleanup-before-stopped ordering.
"""
import json
from pg524_term_witness import witness as ordinary_witness, require, unique


def witness(role, before, after, raw, pid, uid):
    result = ordinary_witness(role, before, after, raw, pid, uid)
    rows = [json.loads(line, object_pairs_hook=unique) for line in raw.decode('utf-8').splitlines()]
    captures = [(i, r) for i, r in enumerate(rows)
                if r['MESSAGE'] == f'{role} fixed PT native capture complete']
    stopped = [(i, r) for i, r in enumerate(rows) if r['MESSAGE'] == f'{role} process stopped']
    require(len(captures) == len(stopped) == 1)
    ci, capture = captures[0]
    si, stop = stopped[0]
    require(ci > si and capture['_UID'] == uid)
    require(int(capture['__MONOTONIC_TIMESTAMP']) >= int(stop['__MONOTONIC_TIMESTAMP']))
    require(not any('Exception' in r['MESSAGE'] or 'Error' in r['MESSAGE']
                    or 'cleanup unconfirmed' in r['MESSAGE'] for r in rows))
    return {**result, 'nativeCaptureComplete': True, 'nativeFileAcceptedSeparately': True,
            'coverage100': False, 'parentAccepted': False}
