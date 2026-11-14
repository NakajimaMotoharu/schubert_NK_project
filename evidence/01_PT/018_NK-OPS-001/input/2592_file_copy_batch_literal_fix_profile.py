"""Verify the already recorded BUG2883 fix without repeating its source mutation or failed phase."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';e=b/'evidence/PG30824-file-copy-batch-test-max-literal-repair-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
p=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/ScenarioFileCopyBatchTest.java';old=(e/'ScenarioFileCopyBatchTest.before.java.txt').read_text();current=p.read_text();name='ORACLE_MAXIMUM_N12';literal='"999999999999"';assert current.replace('  private static final String '+name+' = '+literal+';\n','').replace(name,literal)==old
assert current.count('@Test')==14
a=json.loads((i/'2590_file_copy_batch38_profile.json').read_text());unchanged=[]
for path in a['mainSources']+[x['path'] for x in a['testSources'] if x['path']!=str(p.relative_to(r))]:
 assert subprocess.check_output(['git','show','84a9fce233952bd7ec4d60bb1eb8f685d7d17383:'+path])==(r/path).read_bytes();unchanged.append(dict(path=path,sha256=sha(r/path)))
value=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bug='BUG2883',horizontal='YKT2412',beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterTest=ref(p),allOldJavaAndLiteralInverse=True,newDefinitions=0,wholeDefinitions=14,allMainAndOtherTestBytesUnchanged=unchanged,originalPrestyleFailureRetained=True,originalCompileAndUnitNotRun=True,malformedHeredocSuffixExit1AfterMutationRetainedAsToolFailure=True,normal38NotExecuted=True,formalAccepted=False)
assert not (e/'manifest.json').exists();(e/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
a.update(id='PG30838-FILE-COPY-BATCH-CLOSED38-FIXED');a['closureProofs'].append(ref(e/'manifest.json'));a['slots']={k:str((b/('evidence/PG'+str(n)+'-file-copy-batch38-fixed-'+k+'-v1')).relative_to(r)) for k,n in zip(['prestyle','prepare','static','preflight','unit','post'],[30830,30832,30834,30836,30838,30840])};a['privateDirs']=dict(prepare='pg30832-file-copy-batch38-fixed-prepare-v1',unit='pg30838-file-copy-batch38-fixed-unit-v1');p=i/'2593_file_copy_batch38_fixed_profile.json';assert not p.exists();p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,allOldTestTokensAndLiteralsInverse=True,allMainUnchanged=True,newDefinitions=0,normal38Pending=True)))
