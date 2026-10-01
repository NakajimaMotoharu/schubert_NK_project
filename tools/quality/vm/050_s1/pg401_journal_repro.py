"""Read-only real JSON ordering canary; prints metadata only, never journal fields."""
import subprocess, json, hashlib, pathlib
boot = pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-', '')
command = ['/usr/bin/journalctl','--no-pager','--quiet','--all','--output=json',
           '--output-fields=MESSAGE,PRIORITY,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_SYSTEMD_UNIT',
           '_SYSTEMD_UNIT=artemis.service','_BOOT_ID=' + boot]
rows = [json.loads(s) for s in subprocess.check_output(command).splitlines()]
closed = [r['_SYSTEMD_INVOCATION_ID'] for r in rows if 'AMQ221002:' in r.get('MESSAGE','') and ' stopped, uptime ' in r.get('MESSAGE','')]
assert closed
query = command + ['_SYSTEMD_INVOCATION_ID=' + closed[-1]]
first, second = subprocess.check_output(query), subprocess.check_output(query)
def canonical(raw):
    text = 'NKJOURNAL1\n'
    for ordinal, row in enumerate(json.loads(s) for s in raw.splitlines()):
        for key in sorted(row):
            assert isinstance(row[key], str)
            text += 'ROW|' + str(ordinal) + '|' + key + '|' + row[key].encode('utf-8', errors='strict').hex() + '\n'
    return hashlib.sha256(text.encode('ascii')).hexdigest()
objects_equal = [json.loads(s) for s in first.splitlines()] == [json.loads(s) for s in second.splitlines()]
canonical_hashes = [canonical(first), canonical(second)]
assert objects_equal and canonical_hashes[0] == canonical_hashes[1]
print(json.dumps({'rawByteEqual':first == second,'objectsEqual':objects_equal,
    'byteCounts':[len(first),len(second)],'entryCount':len(first.splitlines()),
    'rawSha256':[hashlib.sha256(first).hexdigest(),hashlib.sha256(second).hexdigest()],
    'canonicalSha256':canonical_hashes,'readOnly':True,'wholeStartupAccepted':False}))
