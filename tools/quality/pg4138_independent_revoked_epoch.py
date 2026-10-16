"""Independent reverse reconstruction tied to pre-recovery ISSUED hash; no permit publication."""
import re
from pg4086_failed_done_recovery_contract import invalid_epoch,require


def former_issued(actual,permit_sha256):
    require(type(actual)is bytes and 0<len(actual)<=4096 and type(permit_sha256)is str
            and re.fullmatch('[0-9a-f]{64}',permit_sha256)is not None)
    try:lines=actual.decode('ascii').split('\n')
    except UnicodeDecodeError:raise ValueError('independent revoked epoch refused')from None
    require(len(lines)==9 and lines[1]=='state=INVALID'and lines[7]=='permit_sha256=-')
    lines[1]='state=ISSUED';lines[7]='permit_sha256='+permit_sha256
    issued='\n'.join(lines).encode('ascii')
    require(invalid_epoch(issued)==actual)
    return issued
