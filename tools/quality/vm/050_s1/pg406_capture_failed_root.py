"""Independent PG406 failure capture; no Root/ready/coverage-100 acceptance."""
import datetime, hashlib, json, pathlib, re
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
run = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p, header):
    lines = p.read_text().splitlines()
    assert lines[0] == header and p.read_bytes().endswith(b'\n')
    pairs = [s.split('=', 1) for s in lines[1:]]
    assert len(dict(pairs)) == len(pairs)
    return dict(pairs)
def rows(name): return [s for s in (run/name).read_text().splitlines() if re.match(r'^\d+\|', s)]
base = json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG406-root-launch-baseline/manifest.json').read_text())
before, after = rows('pg406-native-db-before-full.log'), rows('pg406-native-db-final-full.log')
assert len(before) == 142 and len(after) == 152 and after[:142] == before
steps = ['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION',
         'CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY']
for i, line in enumerate(after[142:]):
    f = line.split('|')
    assert len(f) == 14 and f[0] == str(143+i) and f[3] == steps[i]
    assert f[4] == ('22' if i < 2 else '14' if i < 9 else '10')
    assert f[7:] == ['SKIPPED','0','0','0','0','ALREADY_SUCCESSFUL','step already successful for business date']
assert (run/'pg406-backup-before-private.json').read_bytes() == (run/'pg406-backup-after-private.json').read_bytes()
watch = [json.loads(s) for s in (run/'pg406-root-watch-private.jsonl').read_text().splitlines()]
assert watch[-1]['terminalObserved'] is True
manager = watch[-2]['units']
assert all(v['MainPID'] == v['ControlPID'] == '0' and not v['Job'] for v in manager.values())
assert manager['schubert-nk-morning-controller.service']['ExecMainStatus'] == '30'
assert manager['schubert-nk-api.service']['ExecMainStatus'] == '30'
ownerpath, launchpath = run/'pg406-owner-public-private.txt', run/'pg406-launch-public-private.txt'
owner, launch = record(ownerpath, 'NKMAINTOWNER1'), record(launchpath, 'NKLAUNCH1')
assert owner['run'] == '31100027-2222-4333-8444-555555555555'
assert owner['activation'] == '31100027-6666-4777-8888-999999999999'
assert owner['cutoff'] == '2026-09-27T15:00:00Z' and launch['service'] == 'API'
assert launch['owner_sha256'] == sha(ownerpath) and launch['epoch'] == owner['epoch'] and launch['boot'] == owner['boot']
assert owner['morning_invocation'] == manager['schubert-nk-morning-controller.service']['InvocationID']
assert launch['invocation'] == manager['schubert-nk-api.service']['InvocationID']
seen = [d['units']['schubert-nk-api.service'] for d in watch[:-1]
        if d['units']['schubert-nk-api.service']['MainPID'] != '0']
assert seen and all(s['MainPID'] == launch['pid'] for s in seen)
assert all(s.get('entry') != 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain' for s in seen)
assert any(s.get('process', {}).get('Uid') == '0\t0\t0\t0'
           and s['process']['CapEff'] == '00000000000801c4' for s in seen)
reached = (run/'pg406-native/RootServiceExecutableAdmission-root-reached.txt').read_text()
assert 'coveredLines=' in reached and ',112,' in reached and ',113,' not in reached
assert not (run/'pg406-native/RootServiceFacts-root-reached.txt').read_text().strip()
observed = json.loads((run/'pg406-native-final-private.json').read_text())
assert observed['invalid'] and 'permit-start.intent' in observed['namespaces']['startup']
assert len(observed['namespaces']['startup']) == 7
assert all(not observed['namespaces'][k] for k in ['maintenance','backup-request','cleanup-request','expiry-request'])
coverage = {n:json.loads((run/f'pg406-native/{n}-five-union.json').read_text()) for n in ['protocol','storage','bootstrap','api','web','batch']}
assert all(v['classByteMismatch'] == 0 for v in coverage.values())
miss = {k:sum(v[k]['missed'] for v in coverage.values()) for k in ['BRANCH','LINE','METHOD','CLASS']}
manifest = {
    'id':'PG406-native-root-refused', 'formal':False, 'sourceCommit':base['sourceCommit'],
    'branch':'dev-foundation','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'environment':'isolated Ubuntu26.04/JDK25.0.4/PostgreSQL18.6/Artemis2.56/JaCoCo0.8.15',
    'command':'pg406_deploy.sh; Pg406RootCoverage; pg406_native.sh exactly once; five actual execs same-byte union',
    'exitCode':30,'rootExit':30,'wholeStartupAccepted':False,'bugs':['BUG-403'],
    'ssc':['SSC-137','SSC-138','SSC-139','SSC-140','SSC-141','SSC-142','SSC-143'],'ykt':['YKT-323'],
    'releaseManifestSha256':sha(pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private/pg406-release/RELEASE-MANIFEST.json')),
    'actual':{'old142RowsUnchanged':True,'rows':152,'newSkippedSteps':10,'backupInventoryUnchanged':True,
              'realRootAndParentTicketBinding':True,'rootUidZero':True,'rootFiveCaps':True,
              'ordinaryApiObserved':False,'rootJavaSelectorRefusalLine':112,'factsNotReached':True,
              'currentInvalid':True,'startupEntries':7,'intentsPreserved':True,'requestsEmpty':True,
              'ownerHash':sha(ownerpath),'launchHash':sha(launchpath)},
    'coverage':{'moduleUnion':coverage,'totalMissed':miss,'classByteMismatch':0,
                'sameRunRoles':['parent','backup','cleanup','expiry','root-api']},
    'nativeExecHashes':{n:sha(run/f'pg406-native/{n}.exec') for n in ['parent','backup','cleanup','expiry','root-api']},
    'fullRegression':{'tests':base['tests'],'failures':0,'errors':0,'skipped':0,'staticModulesZero':6},
    'logs':[{'path':str(run/n),'sha256':sha(run/n)} for n in ['pg406-six-v3.log','pg406-deploy.log','pg406-root-coverage-prepare.log','pg406-native-db-before-full.log','pg406-native-db-final-full.log','pg406-root-watch-private.jsonl']],
    'limitations':['BUG403 Root selector open; same-PID ordinary exec/ready/CHR not reached',
                   'failed startup intents remain isolated; exact normal resume required',
                   'native UNKNOWN/hard-timeout/completed receipt/M-final-close/BUG392 pending',
                   '100% coverage and formal PT-WEB-20260925-24 unchanged'],
    'redaction':'No raw journal/InvocationIDs/owner/launch/native exec/credentials/password/session/token/master/dump in Git',
}
out = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/manifest['id']
out.mkdir(parents=True, exist_ok=False)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'missed':miss,'readyAccepted':False}))
