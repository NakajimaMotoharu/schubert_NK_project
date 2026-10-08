"""SS331/341/343 SSC228: independent same-run resume full-column oracle.

No Production imports; literal cohort, ten slots and SQL postconditions.
This proves rows/Backup preservation only, not parent DONE/ready/native.
"""
import datetime
import json

RUN = 'e49243d5-de84-4714-8612-6912ddc17e9e'
CUTOFF = '2026-10-08T18:32:42.140966Z'
REFERENCE = '3a53b979-fa01-47dd-92a6-7b26affcfb5c'
STEPS = ('BACKUP_DB', 'BACKUP_CONFIG', 'CLEAN_NOTIFICATION', 'CLEAN_QUESTION',
         'CLEAN_SESSION', 'CLEAN_INBOX_OUTBOX', 'CLEAN_LOG', 'CLEAN_BATCH_RUN',
         'CLEAN_TRANSFER', 'CLEAN_EXPIRY')
COLUMNS = {'id', 'run_id', 'business_date', 'step', 'attempt', 'started_at',
           'ended_at', 'status', 'target_count', 'success_count', 'failure_count',
           'byte_count', 'error_code', 'error_summary', 'expiry_cutoff_at',
           'expiry_before_count', 'expiry_after_count'}


def require(value):
    if not value:
        raise ValueError('independent same-run resume postcondition rejected')


def canonical(rows):
    require(type(rows) is list and all(type(r) is dict for r in rows))
    values = [json.dumps(r, sort_keys=True) for r in rows]
    require(len(values) == len(set(values)))
    return sorted(values)


def instant(value):
    require(type(value) is str)
    result = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None)
    return result


def validate(old, new, old_backup, new_backup):
    require(type(old) is dict and type(new) is dict and len(old) == 24
            and set(old) == set(new))
    require(type(old_backup) is dict and bool(old_backup) and old_backup == new_backup)
    for table in old:
        if table != 'schubert.batch_runs':
            require(canonical(old[table]) == canonical(new[table]))
    before = old['schubert.batch_runs']
    after = new['schubert.batch_runs']
    require(len(before) == 494 and len(after) == 504)
    canonical(before); canonical(after)
    prior = {r['id']: r for r in before}
    actual = {r['id']: r for r in after}
    require(len(prior) == 494 and len(actual) == 504
            and all(type(k) is int and k > 0 for k in actual)
            and all(actual.get(k) == r for k, r in prior.items()))
    added = [r for k, r in actual.items() if k not in prior]
    require(len(added) == 10 and {r.get('step') for r in added} == set(STEPS))
    for row in added:
        require(set(row) == COLUMNS and row['run_id'] == RUN
                and row['business_date'] == '2026-10-09' and row['status'] == 'SKIPPED'
                and row['error_code'] == 'ALREADY_SUCCESSFUL'
                and row['error_summary'] == 'step already successful for business date')
        require(all(type(row[k]) is int and row[k] == 0 for k in
                    ('target_count', 'success_count', 'failure_count', 'byte_count')))
        require(row['ended_at'] == row['started_at']
                and instant(row['started_at']) >= instant(CUTOFF))
        history = [r for r in before if r['step'] == row['step']
                   and r['business_date'] == '2026-10-09']
        require(type(row['attempt']) is int and row['attempt'] == max(r['attempt'] for r in history) + 1)
        successes = [r for r in history if r['status'] == 'SUCCESS'
                     and (row['step'] not in STEPS[:2] or r['run_id'] == RUN)]
        require(len(successes) == 1 and successes[0]['run_id'] ==
                (RUN if row['step'] in STEPS[:2] else REFERENCE))
        if row['step'] == 'CLEAN_EXPIRY':
            require(instant(row['expiry_cutoff_at']) == instant(CUTOFF) - datetime.timedelta(days=7)
                    and type(row['expiry_before_count']) is int
                    and type(row['expiry_after_count']) is int
                    and row['expiry_before_count'] == row['expiry_after_count'] == 0)
        else:
            require(all(row[k] is None for k in
                        ('expiry_cutoff_at', 'expiry_before_count', 'expiry_after_count')))
    return {'oldBatchRowsUnchanged': 494, 'newSameRunSkippedAttempts': 10,
            'all24TablesIndependentPostcondition': True, 'backupAllMetadataAndHashesUnchanged': True,
            'originalSuccessReferencesUnchanged': True, 'retentionDeletes': 0,
            'parentDoneAccepted': False, 'formalAccepted': False}
