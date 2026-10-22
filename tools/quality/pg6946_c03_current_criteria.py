"""C03 own-artifact/oracle/current-original-case audit only; no DB/process replay."""
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg6092_current3985_static_join import source_case_candidates

OWNED = ('src/deployment/postgresql/postgresql.conf.template', 'src/deployment/postgresql/pg_hba.conf.template')
ROLE_SQL = 'src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/PostgresDeploymentTest.java'
DESIGN = 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
# Independent literals transcribed from origin/main SS342 section6, not from deployed data/Test methods.
EXPECTED = {
 'listen_addresses': '127.0.0.1,::1', 'port': '5432', 'max_connections': '40',
 'shared_buffers': '2GB', 'effective_cache_size': '6GB', 'work_mem': '8MB',
 'maintenance_work_mem': '512MB', 'max_worker_processes': '8', 'max_parallel_workers': '4',
 'max_parallel_workers_per_gather': '2', 'temp_file_limit': '2GB', 'wal_compression': 'on',
 'min_wal_size': '1GB', 'max_wal_size': '4GB', 'checkpoint_timeout': '15min',
 'checkpoint_completion_target': '0.9', 'deadlock_timeout': '500ms', 'password_encryption': 'scram-sha-256',
 'ssl': 'off', 'log_statement': 'none', 'log_parameter_max_length': '0', 'log_parameter_max_length_on_error': '0',
 'log_connections': 'on', 'log_disconnections': 'on', 'log_checkpoints': 'on', 'log_lock_waits': 'on',
 'log_autovacuum_min_duration': '0', 'log_min_duration_statement': '-1', 'log_min_duration_sample': '-1',
 'log_transaction_sample_rate': '0', 'log_min_error_statement': 'panic', 'log_error_verbosity': 'terse'}
ROLES = {
 'app': ('1500ms', '500ms', '15s'), 'web_session': ('1500ms', '500ms', '15s'),
 'batch': ('30min', '5s', '60s'), 'backup': ('30min', '5s', '60s'),
 'migration': ('30min', '5s', '60s'), 'ops_ro': ('10s', '1s', '15s'),
 'inbox_inspector': ('30s', '5s')}
METHODS = ('literalConfiguration', 'nativeConfiguration', 'literalHba', 'nativeHba',
 'roleTimeouts', 'invalidConfiguration', 'invalidHba', 'isolationAndEvidence')


def lines(text):
    return [' '.join(s.split()) for s in text.splitlines() if s.strip() and not s.lstrip().startswith('#')]


def settings(text):
    result = {}
    for line in lines(text):
        key, separator, value = line.partition('=')
        key, value = key.strip(), value.strip()
        if not separator or not re.fullmatch('[a-z_]+', key) or key in result or not value:
            raise ValueError('one unique complete directive')
        if value.startswith("'") and value.endswith("'") and value.count("'") == 2:
            value = value[1:-1]
        elif "'" in value:
            raise ValueError('balanced literal, not permissive configuration parsing')
        result[key] = value
    return result


def hba_expected():
    rows = ['local all postgres peer']
    for role in ('app', 'web_session', 'batch', 'backup', 'ops_ro', 'migration'):
        for address in ('127.0.0.1/32', '::1/128'):
            rows.append('host schubert_nk schubert_' + role + ' ' + address + ' scram-sha-256')
    return rows + ['host schubert_nk schubert_inbox_inspector 127.0.0.1/32 scram-sha-256',
      'host all all 0.0.0.0/0 reject', 'host all all ::/0 reject']


def validate_templates(conf, hba):
    if settings(conf) != EXPECTED or lines(hba) != hba_expected():
        raise ValueError('exact independent32 directives and ordered16 HBA rules; no missing/extra/unsafe widening')


def validate_roles(sql):
    kinds = ('statement_timeout', 'lock_timeout', 'idle_in_transaction_session_timeout')
    actual = {}
    for role, key, value in re.findall(r"^ALTER ROLE (schubert_[a-z_]+) SET ([a-z_]+) = '([^']+)';$", sql, re.MULTILINE):
        if key not in kinds:
            continue
        pair = (role, key)
        if pair in actual:
            raise ValueError('one timeout setting per role/key')
        actual[pair] = value
    expected = {('schubert_' + role, key): value for role, values in ROLES.items() for key, value in zip(kinds, values)}
    if actual != expected:
        raise ValueError('all20 explicit role timeout settings, no invented Inspector idle timeout')


def main():
    qp, q, cases = read_whole()
    if sha(qp) != '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731':
        raise ValueError('fixed original4222 qualification, never repeat execution')
    source = q['productionSource']
    design = subprocess.check_output(['git', 'show', 'origin/main:' + DESIGN], cwd=ROOT)
    if design != (ROOT / DESIGN).read_bytes():
        raise ValueError('canonical design and implementation tree document agree')
    inputs = {}
    run = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    if sha(run / 'source.tar') != begin['archiveSha256'] or begin['source'] != source:
        raise ValueError('original full source archive')
    with tarfile.open(run / 'source.tar') as tar:
        for path in (*OWNED, ROLE_SQL, TEST):
            item = tar.getmember(path)
            if not item.isfile():
                raise ValueError('regular original public input')
            raw = tar.extractfile(item).read()
            if raw != (ROOT / path).read_bytes() or raw != subprocess.check_output(['git', 'show', source + ':' + path], cwd=ROOT):
                raise ValueError('every owned/shared/Test byte fixed to the actual original source')
            inputs[path] = sha(ROOT / path)
    validate_templates(*[(ROOT / p).read_text() for p in OWNED])
    validate_roles((ROOT / ROLE_SQL).read_text())
    inventory = json.loads((ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owned = {a['path']: a['sha256'] for a in inventory['currentPhysicalCandidate']['artifacts'] if a['owner'] == 'WBS-C03'}
    if owned != {p: inputs[p] for p in OWNED}:
        raise ValueError('both current C03 artifacts only; shared SQL has no second cost owner')
    text = (ROOT / TEST).read_text()
    joined = []
    for index, name in enumerate(METHODS, 1):
        digest = hashlib.sha256(source_case_candidates(text, name)[0].encode()).hexdigest()
        found = [c for c in cases if c['class'] == 'dev.codex.schubert.nk.api.database.PostgresDeploymentTest' and c['caseNameSha256'] == digest]
        if len(found) != 1 or found[0]['result'] != 'PASS_ORIGINAL_XML' or found[0]['source'] != source:
            raise ValueError('one actual current original PASS per independently identified PGCFG TestID')
        joined.append(dict(testId=f'PT-OPS-PGCFG-{index:03}', method=name, originalCase=found[0]))
    value = dict(actualExit=0, source=source, originalQualificationSha256=sha(qp),
      designMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(),
      designSha256=hashlib.sha256(design).hexdigest(), inputHashes=inputs, configurationKeys=32,
      hbaRules=16, roles=7, explicitTimeoutSettings=20, originalCases=joined,
      localEvidenceChecks=['WBS-C03:contract', 'WBS-C03:scope', 'WBS-C03:quality'],
      localEvidenceStatus='CURRENT_CRITERIA_EVIDENCE_READY_NOT_CANONICAL_ACCEPTANCE',
      runtimeDeploymentVerified=False, databaseAccessByReader=False, testsExecutedByReader=0,
      processActions=0, vmActions=0, configurationChanges=0, wholeReplayed=False,
      risks=['OS active config/remote rejection/drift and primary MESSAGE redaction remain separate runtime gates',
             'canonical historical17 is not rebased by this local evidence audit'],
      acceptedLeafDelta=0, formalAccepted=False, effortPercent=None, ptAlternativeCompleted=0,
      command='python3 -B tools/quality/pg6946_c03_current_criteria.py', toolSha256=sha(ROOT / 'tools/quality/pg6946_c03_current_criteria.py'))
    out = BASE / 'PG6946-c03-current-criteria-v1'
    os.umask(0o077)
    out.mkdir()
    path = out / 'manifest.json'
    with path.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), originalCases=8, localEvidenceChecks=3, acceptedLeafDelta=0)))


if __name__ == '__main__':
    main()
