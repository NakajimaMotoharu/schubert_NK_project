"""BUG813/814: preserve current-boot API namespace failure; no Unit/DB/file repair."""
import datetime, hashlib, json, os, pathlib, subprocess

def require(value):
    if not value:
        raise ValueError('fixed namespace diagnosis refused')

require(os.geteuid() == 0)
os.umask(0o077)
boot = 'cc9ed874-7f4f-450e-a188-8de1e42c8441'
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip() == boot)
save = pathlib.Path('/var/lib/pgpt-s1-preservation/pg512-api-namespace-v1')
require(not save.exists())
args = ['/usr/bin/journalctl', '--boot', '--no-pager', '-o', 'json', '-u', 'schubert-nk-api.service']
raw = subprocess.check_output(args, timeout=10)
rows = [json.loads(line) for line in raw.splitlines()]
require(rows and all(row.get('_BOOT_ID') == boot.replace('-', '') for row in rows))
messages = [row.get('MESSAGE', '') for row in rows]
roles = ['root-api193', 'ordinary-api193', 'root-web193', 'ordinary-web193', 'ordinary-inspector196', 'ordinary-bootstrap196']
missing = {role: not (pathlib.Path('/run/schubert-nk/pt-coverage') / role).exists() for role in roles}
matches = {role: sum('/run/schubert-nk/pt-coverage/' + role in m and 'No such file or directory' in m for m in messages) for role in roles}
counts = {p: sum(p in m for m in messages) for p in ['Failed to set up mount namespacing', 'Failed at step NAMESPACE', 'Failed to start']}
require(counts['Failed to set up mount namespacing'] == 5 and counts['Failed at step NAMESPACE'] == 5)
require(all(missing.values()) and sum(matches.values()) == 5)
require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == '/opt/schubert-nk/releases/0.1.0-PG495')
require(raw == subprocess.check_output(args, timeout=10))
save.mkdir(mode=0o700)
with (save / 'api-journal.private.jsonl').open('xb') as stream:
    stream.write(raw); stream.flush(); os.fsync(stream.fileno())
fd = os.open(save, os.O_RDONLY | os.O_DIRECTORY)
try:
    os.fsync(fd)
finally:
    os.close(fd)
print(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'privateJournalSha256': hashlib.sha256(raw).hexdigest(), 'rows': len(rows), 'missingNativeRoles': missing, 'exactMissingPathCounts': matches, 'failureCounts': counts, 'businessMutation': False, 'unitAction': False, 'productionChanged': False}))
