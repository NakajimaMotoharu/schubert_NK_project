"""Current immutable D5 ownership/full post reauthentication; no business mutation."""
import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path
import pg1257_fresh_independent_terminal_post as transport
from pg1260_fresh_backup_independent_capture import SEALS


def payload():
    code = transport.payload(SEALS)
    marker = "save=base/'pg1257-fresh-terminal-post-v1'"
    if code.count(marker) != 1:
        raise ValueError('qualified read-only boundary must be unique')
    code = code[:code.index(marker)]
    code += "\nresult.update(run='PG1281-current-readonly-v1',startsStopsReloadsSqlWrites0=True)\nprint(json.dumps(result))\n"
    compile(code, '<current immutable D5 read-only guard>', 'exec')
    return code


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean current operator source required')
    build = json.loads((transport.W/'pg1254-frozen-v1.safe.json').read_bytes())
    if build['actualExit'] != 0 or build['productionSource'] != transport.SOURCE:
        raise ValueError('qualified installed immutable ABI required')
    names = [n.replace('1216', '1253') for n in [
        'Pg1216NativeStop.class', 'Pg1216NativeStop$References.class',
        'pg1216_native_refs.py', 'pg1216_native_owned_stop.py',
        'pg526_term_witness.py', 'pg526_native_term_witness.py',
        'pg1216_parent_receipt.py', 'pg1216_durable.py',
        'pg1216_configuration.py', 'pg1216_configuration_capture.py',
        'pg1216_row_bound.py', 'pg1216_stable_journal.py']]
    hashes = {n: build['fileHashes'][n] for n in names}
    receipt = (transport.W/'pg1253-native-tools-v1/pg1253_parent_receipt.py').read_text()
    code = 'HASHES='+repr(hashes)+'\nRECEIPT='+repr(receipt)+'\n'+payload()
    base = transport.W/'pg1281-current-readonly-v1'
    if any(Path(str(base)+suffix).exists() for suffix in ['.safe.json', '.private.log', '.exit']):
        raise ValueError('new-only current observation slot required')
    start = datetime.datetime.now(datetime.timezone.utc)
    result = subprocess.run(transport.SSH, input=code.encode(), capture_output=True, timeout=90)
    with Path(str(base)+'.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x') as f:
        f.write(str(result.returncode)+'\n')
    safe = dict(actualExit=result.returncode,
        operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        startedUTC=start.isoformat(), completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        privateLogSha256=hashlib.sha256(result.stderr).hexdigest(), formalAccepted=False)
    if result.returncode == 0:
        safe.update(json.loads(result.stdout))
    with Path(str(base)+'.safe.json').open('x') as f:
        json.dump(safe,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in safe.items() if k not in {'proofHashes','toolHashes'}}))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
