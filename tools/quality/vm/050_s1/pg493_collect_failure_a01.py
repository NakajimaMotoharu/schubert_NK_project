"""Extract sanitized captured PG493 A01/timeout evidence, never rerun or normalize the parent."""
import hashlib,json,os,pathlib
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
metadata=json.loads((WORK/'pg493-chr-a01-execution.private.json').read_text())
assert metadata['exitCode']==0 and metadata['productionSource']=='38899a05b5c2daeecfc5af8ea5ae748e29954c60'
artifact=ROOT/'program/characterization/reports/nk/PG493-native-a01-v1/artifacts/CHR-A01.json'
case=json.loads(artifact.read_text())
assert case['status']=='PASS' and case['statusCode']==200 and case['csrf']=='<TOKEN>' and case['passwordValue']==''
assert (WORK/'pg493-a01-native-v1.exit').read_text().strip()=='0'
assert (WORK/'pg493-parent-observer-v1.exit').read_text().strip()=='0'
watch=[json.loads(x) for x in (WORK/'pg493-parent-watch-private-v1.jsonl').read_text().splitlines()]
assert any(x.get('caddyTlsLogin200') and x.get('sameApiWeb') and x.get('sameCaddySocket') and x.get('publicCaValidated') for x in watch)
# Exact parent's failure is an independent actual observation, not the observer/client exit0.
payload={'id':'PG493-parent-timeout-A01-limited','branch':'dev-foundation','productionSource':metadata['productionSource'],
 'A01':metadata,'A01ArtifactSha256':sha(artifact),'currentBaselineSha256':sha(ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json'),
 'commands':['bash tools/quality/vm/050_s1/pg493_a01_native_v1.sh','ssh existing-guest sudo -n python3 -B < tools/quality/vm/050_s1/pg493_capture_failure.py'],
 'parent':{'invocation':'52accf6d68f44487b6e0b3635c20396f','result':'timeout','actualExit':143,'kernelEmpty':True,'normalCloseAccepted':False},
 'privateCapture':{'actualExit':0,'observedAt':'2026-10-06T15:49:20.464359+00:00',
  'snapshotSha256':'6515cdbfaee4df2f518acb1cd85d527f65dea1f0daa505e86d04c1eb2c903752',
  'oldBatchRowsPreserved':432,'batchRows':442,'other20TablesUnchanged':True,
  'legitimateHttpWriteTables':['app_logs','web_log_outbox','web_http_sessions'],'liveCohortRetained':4,'startStopMutations':0},
 'environment':{'VM':'Ubuntu 26.04','JDK':'25.0.4','hostKernel':os.uname().release},
 'related':['BUG-799','YKT-570','QA-047','SSC-203'],'allCHRPassed':False,'allParentPassed':False,
 'nativeSameSourceAccepted':False,'coverage100':False,'formal':False,'ITSTAccepted':False,'rawSecretsInGit':False}
out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG493-parent-timeout-A01-limited/manifest.json'
assert not out.exists();out.parent.mkdir(parents=True)
with out.open('x') as f:json.dump(payload,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'A01Passed':True,'parentTimeout143':True,'formal':False,'manifestSha256':sha(out)}))
