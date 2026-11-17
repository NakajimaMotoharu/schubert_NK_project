"""Pin Parser existing4/new namespace1, source-only empty-private-ctor applicability candidates."""
from pathlib import Path
import json,hashlib,re,datetime,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();main=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/media/HttpByteRangeParser.java','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/media/package-info.java'];tests=[dict(path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/HttpByteRangeParserTest.java',tests=4),dict(path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/HttpByteRangeNamespaceContractTest.java',tests=1)];before=json.loads((b/'evidence/PG37534-range-source-before-v1/manifest.json').read_text());assert sha(r/tests[0]['path'])==before['original4TestSha256']
for x in tests:assert (r/x['path']).read_text().count('@Test')==x['tests']
# Candidate metadata only. Never treat same-class factory/no-instance heuristics as a dynamic pass.
rows=[];held_unread=[]
for module in ['protocol','storage','bootstrap','api','web','batch']:
 for p in (r/f'src/schubert-nk-{module}/src/main/java').rglob('*.java'):
  if any(s in p.stem for s in ['FailedStart','Cohort']):held_unread.append(str(p.relative_to(r)));continue
  text=p.read_text();m=re.search(r'\bprivate\s+'+re.escape(p.stem)+r'\s*\(\s*\)\s*\{',text)
  if not m:continue
  factory=bool(re.search(r'\bnew\s+'+re.escape(p.stem)+r'\s*\(\s*\)',text));after=text[m.end():];empty=bool(re.match(r'\s*}',after));sensitive=any(s in p.stem for s in ['Root','Linux','Native','Inode','FileCalls','Credential','Permit','Intent','Recovery','Startup'])
  status='INTENTIONAL_FACTORY_CANDIDATE_REQUIRES_SPEC_AND_RAW' if factory else 'SOURCE_ONLY_HOLD_NO_INSTANTIATION_OR_CLASSFILE_ACTION' if sensitive else 'PRIVATE_NAMESPACE_CANDIDATE_NOT_QUALIFIED'
  known=None
  if p.stem=='RequestLogDetails':known='PG37348 current raw5Code100; separate parser5 source proof'
  if p.stem=='MaintenanceRecords':known='PG37286 current raw53Code100 target6; no replay'
  if p.stem=='HttpByteRangeParser':status='CURRENT_RANGE_GROUP_GUARD_AND_NEW1_PENDING'
  rows.append(dict(path=str(p.relative_to(r)),sha256=sha(p),line=text[:m.start()].count('\n')+1,emptyBody=empty,sameClassNewFactoryCandidate=factory,status=status,knownLimitedProof=known,actualTestOrInstantiation=False,formalAccepted=False))
out=b/'evidence/PG37538-range-namespace5-source-v1';assert not out.exists();out.mkdir();(out/'private-noarg-source-candidates.json').write_text(json.dumps(dict(rows=rows,excludedHeldSourceNotRead=held_unread,wholeScopeAccepted=False),ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainSources=main,testSources=tests,sdkHashes={},inputHashes={n:sha(r/n) for n in main+[x['path'] for x in tests]},original4SourceOracleExact=True,expectedTests=5,newDefinitions=1,necessaryPriorDefinitions=4,privateNoargCandidates=len(rows),emptyPrivateBodies=sum(x['emptyBody'] for x in rows),sameClassFactoryCandidates=sum(x['sameClassNewFactoryCandidate'] for x in rows),heldSourceSkippedUnread=len(held_unread),ykt2647NotClosed=True,protectedFilesOrPrivateRawRead=False,sourceOnlyCandidateScanNotGate=True,productTestsExecuted=0,actualRootVmDbNativeKeyAuthorityOrHeldClassfileActions=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,Main2=True,whole5=True,privateNoargCandidates=len(rows),empty=sum(x['emptyBody'] for x in rows),sameClassFactories=sum(x['sameClassNewFactoryCandidate'] for x in rows),heldSourceNotRead=len(held_unread)))
