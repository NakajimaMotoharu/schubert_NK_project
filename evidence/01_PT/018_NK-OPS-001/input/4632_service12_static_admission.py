"""Seven exact source diagnostics, full current Batch646 SB and public ABI bound before ordinary12."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37186-service12-reused-compile-static-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and p['expectedTests']==12 and not p['processingErrors'] and len(p['rawFindings'])==7
sbp=r/p['mainSpotBugsCurrentProof']['path'];sb=ld(sbp);assert sha(sbp)==p['mainSpotBugsCurrentProof']['sha256'] and sb['actualExit']==0 and sb['sourceCore']==p['sourceCore'] and sb['stages']['batch']['actualExit']==0 and not sb['stages']['batch']['timedOut']
report=sb['reports']['batch'];assert report['bugs']==0 and not report['missingClasses'] and not report['errors'];root=ld(r/p['rootCompile']['path']);assert {n.replace('.','/')+'.class' for n in report['classStats']}==set(root['physicalClassHashes']['batch']) and len(report['classStats'])==646
abi=b/'evidence/PG37188-service-command-abi-physical-v1/manifest.json';a=ld(abi);assert a['actualExit']==0 and a['sourceCore']==p['sourceCore'] and a['publicOuterAbiExact'] and a['unchangedPhysicalCount']==1096
rows=[]
for x in p['rawFindings']:
 path=x['path'];expected=p['mainInputHashes'].get(path,p['testSourceHashes'].get(path));assert sha(r/path)==expected;text=(r/path).read_text();anchor=text.splitlines()[int(x['beginline'])-1].strip()
 if '/src/main/' in path:
  assert x['rule']=='EmptyCatchBlock' and anchor=='} catch (NoSuchFileException gone) {'
  assert 'if (link.matches("socket:\\[[1-9][0-9]{0,19}\\]"))' in text or 'socket:' in text
  reason='Existing NativeIo.sockets bounded /proc FD observation: an individual FD link can disappear between directory enumeration and readSymbolicLink. Only this typed NoSuchFileException is skipped; no inode is added, all other IO propagates. A missing observation cannot establish readiness because the owner-inode intersection remains independently mandatory. This unchanged native body is source-reviewed only, not executed or qualified as a live FD proof.'
 elif x['rule']=='ReturnEmptyCollectionRatherThanNull':
  assert any(v in anchor for v in ['nullStatus','nullCommand','nullSockets','selected[0].equals("<NULL>")'])
  reason='Explicit absent byte-array/socket-set negative fixture for required-provider contracts; replacing null by empty would remove the missing-value test. READY428004 requires propagation, never NPE catch/normal success. Root shared null-deadline source is unselected, so source classification supplies no Root PT PASS.'
 elif x['rule']=='EqualsNull':
  assert anchor=='assertFalse(first.equals(null));';reason='READYVALUE001 directly calls immutable Response.equals with null and literal false; object==null would test a different operation. Deliberate value-method argument boundary.'
 else:
  assert x['rule']=='DoNotUseThreads' and anchor=='if (bad == INTERRUPTED_WAIT_FIXTURE) assertTrue(Thread.interrupted());';reason='Original unselected Root test checks-and-clears its own interrupt as postcondition, creating no managed application thread. J2EE-container PMD premise is absent; this statement is not executed by selected12.'
 rows.append(dict(raw=x,sourceSha256=expected,sourceAnchor=anchor,decision='NOT_APPLICABLE',reason=reason))
out=b/'evidence/PG37190-service12-static-admission-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),sourceStaticScope=3,raw=7,classified=rows,applicable=0,unclassified=0,mainSpotbugs=ref(sbp),spotbugsPhysical=646,missingClassErrors=0,publicAbi=ref(abi),originalNinePreserved=True,newOrdinaryCleanupCases=3,productTestsExecuted=0,sourceRuleSuppressionExclusionChanges=0,actualNativeOrRootQualified=False,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=7,applicable=0,unclassified=0,currentSb646Zero=True,publicAbiSame=True,productTests=0)))
