"""Independent SS341 bundle oracle for two backup steps; eight SKIP rows are PG577 scope."""
import datetime
import hashlib
import json
import re

RUN = 'b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'
CUTOFF = '2026-10-08T07:36:21.802335Z'
VERSIONS = {'host': 'pgpt-r2', 'app': '0.1.0-SNAPSHOT', 'schema': '028', 'os': 'ubuntu-26.04',
            'jdk': '25.0.4', 'postgresql': '18.6', 'artemis': '2.56.0', 'age': '1.2.1'}


def require(v):
    if not v:
        raise ValueError('independent same-day backup refused')


def time(value):
    require(type(value) is str)
    t = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(t.tzinfo is not None)
    return t


def positive(n):
    return type(n) is int and 0 < n <= 9223372036854775807


def unique(items):
    d = {}
    for k, v in items:
        require(k not in d)
        d[k] = v
    return d


def validate(old, new, raw_manifest, files):
    require(type(raw_manifest) is bytes and 0 < len(raw_manifest) <= 4096)
    m = json.loads(raw_manifest, object_pairs_hook=unique)
    require(list(m) == ['format', 'database', 'runId', 'cutoff', 'startedAt', 'contentFinishedAt',
                        'databaseStep', 'configurationStep', 'versions', 'recipientSha256', 'files'])
    require(m['format'] == 'NKBACKUP1' and m['database'] == 'schubert_nk' and m['runId'] == RUN
            and m['cutoff'] == CUTOFF and m['versions'] == VERSIONS and list(m['versions']) == list(VERSIONS))
    require(raw_manifest == (json.dumps(m, ensure_ascii=True, separators=(',', ':')) + '\n').encode('ascii'))
    require(type(m['recipientSha256']) is str and re.fullmatch('[0-9a-f]{64}', m['recipientSha256']) is not None)
    names = ['schubert_nk.dump', 'config.tar', 'credentials.tar.age']
    require(type(files) is dict and set(files) == set(names) and list(m['files']) == names)
    for name, data in files.items():
        claim = m['files'][name]
        require(type(claim) is dict and list(claim) == ['size', 'sha256'] and positive(claim['size']))
        require(type(data) is bytes and claim == {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    for field in ('startedAt', 'contentFinishedAt'):
        require(type(m[field]) is str and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z', m[field]) is not None)
    start, finish = time(m['startedAt']), time(m['contentFinishedAt'])
    require(time(CUTOFF) <= start <= finish)
    require(type(old) is list and type(new) is list)
    old_ids = {r['id']: r for r in old}
    all_ids = {r['id']: r for r in new}
    require(len(old_ids) == len(old) and len(all_ids) == len(new)
            and all(positive(k) and all_ids.get(k) == v for k, v in old_ids.items()))
    rows = [r for r in new if r['id'] not in old_ids and r['step'] in ('BACKUP_DB', 'BACKUP_CONFIG')]
    require(len(rows) == 2 and {r['step'] for r in rows} == {'BACKUP_DB', 'BACKUP_CONFIG'})
    for field, step, count, size in [('databaseStep', 'BACKUP_DB', 1, len(files['schubert_nk.dump'])),
                                    ('configurationStep', 'BACKUP_CONFIG', 2, len(files['config.tar']) + len(files['credentials.tar.age']))]:
        row = next(r for r in rows if r['step'] == step)
        require(set(row) == {'attempt', 'business_date', 'byte_count', 'ended_at', 'error_code', 'error_summary',
                            'expiry_after_count', 'expiry_before_count', 'expiry_cutoff_at', 'failure_count',
                            'id', 'run_id', 'started_at', 'status', 'step', 'success_count', 'target_count'})
        require(positive(row['id']) and positive(row['attempt']) and row['run_id'] == RUN
                and row['business_date'] == '2026-10-08' and row['status'] == 'SUCCESS')
        previous = [r['attempt'] for r in old if r['step'] == step and r['business_date'] == '2026-10-08']
        require(row['attempt'] == (max(previous) + 1 if previous else 1))
        require(all(type(row[k]) is int for k in ('target_count', 'success_count', 'failure_count', 'byte_count'))
                and (row['target_count'], row['success_count'], row['failure_count'], row['byte_count']) == (count, count, 0, size))
        require(all(row[k] is None for k in ('error_code', 'error_summary', 'expiry_after_count', 'expiry_before_count', 'expiry_cutoff_at')))
        require(time(CUTOFF) <= time(row['started_at']) <= start <= finish <= time(row['ended_at']))
        claim = m[field]
        require(type(claim) is dict and list(claim) == ['id', 'attempt', 'startedAt']
                and positive(claim['id']) and positive(claim['attempt']) and claim['id'] == row['id']
                and claim['attempt'] == row['attempt'] and time(claim['startedAt']) == time(row['started_at']))
    return {'backupTwoFull17ColumnsAndActualByteCounts': True, 'allOldBatchRowsProtected': len(old),
            'manifestSha256': hashlib.sha256(raw_manifest).hexdigest(), 'eightSkipsVerifiedSeparatelyPG577': True}
