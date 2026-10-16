"""SSC287 common terminal mechanics and strict one-shot plan; no parent-success adaptation."""
import ast
import hashlib
import re
import uuid
from pathlib import Path

ORDER = ('caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service',
         'schubert-nk-expiry-cleanup.service', 'artemis.service', 'schubert-nk-cleanup.service')
FROZEN = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg3876-current-resume-owned-tools-v1')
FILES = {'pg526_term_witness.py': 'ebdc5130088f2362dfaaab39fec63f0d9437fef0968080bee4a29330d3f9dfed',
         'pg526_native_term_witness.py': 'a1376d489d596e9b30213c4ae6fa93fc02484c7d39c9538ff7065f0bd6349644',
         'pg3876_native_owned_stop.py': '1e61e7616ee613d1e267025aa05ed08129c56822c30c5a80b9b566b8545ffb64'}


def require(v):
    if v is not True: raise ValueError('specific failed-DONE recovery refused')


def shared_sources():
    values = {}
    for name, digest in FILES.items():
        raw = (FROZEN / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest)
        values[name] = raw.decode()
    old = ast.parse(values.pop('pg3876_native_owned_stop.py'))
    names = {'kernel_empty', 'terminal', 'same_generation', 'normal_terminal', 'broker_witness'}
    selected = [n for n in old.body if isinstance(n, ast.FunctionDef) and n.name in names]
    require({n.name for n in selected} == names)
    # No parent_receipt, normal-parent qualifier, holder, stop command or old expected actor is copied.
    values['recovery_terminal.py'] = ("import hashlib,json,pathlib\nfrom pg526_term_witness import FIELDS,unique\n"
        "from pg526_native_term_witness import witness as witness\n__all__=['witness','kernel_empty','terminal','same_generation','normal_terminal','broker_witness']\nBOOT='79a3260a-e16d-42bf-942a-b914ed144c28'\n"
        + "def require(v):\n if not v:raise ValueError('owned recovery terminal refused')\n"
        + ast.unparse(ast.Module(body=selected, type_ignores=[])) + '\n')
    return values


class Plan:
    """In-memory protocol state only; external native guards remain mandatory at every boundary."""
    def __init__(self):
        self.next = 0
        self.reserved = None
        self.revoked = False
        self.finished = False

    def reserve(self, unit):
        require(not self.finished and not self.revoked and self.reserved is None
                and self.next < len(ORDER) and type(unit) is str and unit == ORDER[self.next])
        self.reserved = unit

    def terminal(self, unit):
        require(type(unit) is str and unit == self.reserved and self.next < len(ORDER)
                and unit == ORDER[self.next] and not self.revoked and not self.finished)
        self.reserved = None
        self.next += 1

    def revoke(self):
        require(self.next == len(ORDER) and self.reserved is None and not self.revoked and not self.finished)
        self.revoked = True

    def finish(self):
        require(self.revoked and not self.finished and self.reserved is None)
        self.finished = True


def invalid_epoch(before):
    """Independent exact text oracle for the ONLY permitted startup file delta, never permission."""
    require(type(before) is bytes and 0 < len(before) <= 4096)
    try: lines = before.decode('ascii').split('\n')
    except UnicodeDecodeError: raise ValueError('specific failed-DONE recovery refused') from None
    require(len(lines) == 9 and lines[0] == 'NKEPOCH1' and lines[1] == 'state=ISSUED' and lines[-1] == '')
    for line, key in zip(lines[2:7], ['boot_id', 'epoch_id', 'run_id', 'cutoff_utc', 'activation_id']):
        require(line.startswith(key + '=') and len(line) > len(key) + 1)
    require(lines[2] == 'boot_id=79a3260a-e16d-42bf-942a-b914ed144c28'
            and lines[4] == 'run_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f'
            and lines[5] == 'cutoff_utc=2026-10-16T05:44:47.267413Z'
            and lines[6] == 'activation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04')
    epoch = lines[3].split('=', 1)[1]
    try: require(str(uuid.UUID(epoch)) == epoch and uuid.UUID(epoch).int != 0)
    except (ValueError, AttributeError): raise ValueError('specific failed-DONE recovery refused') from None
    require(re.fullmatch(r'permit_sha256=[0-9a-f]{64}', lines[7]) is not None)
    lines[1] = 'state=INVALID'; lines[7] = 'permit_sha256=-'
    return '\n'.join(lines).encode('ascii')
