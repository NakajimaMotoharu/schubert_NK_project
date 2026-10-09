"""Emit sanitized evidence/current observations patch; no raw exec/session export or credit."""
import difflib,hashlib,json
from pathlib import Path
from pg747_wbs_candidate import transform
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');B=T/'documents/400_PGPT/470_PMO'
def main():
 private=W/'pg879-current-eight-native-v1/manifest.safe.json';m=json.loads(private.read_bytes());assert m['actualExit']==0 and m['productionSource']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
 gain={k:sum(v[k]for v in m['gain'].values())for k in ('LINE','METHOD','CLASS','BRANCH')};remaining={k:sum(v[k]['missed']for v in m['moduleCounters'].values())for k in gain}
 proof={'run':'PG875/876/877/878/879','source':m['productionSource'],'status':'NEW_GENUINE_A01_OWNEDSTOP_NATIVE8_QUALIFIED_NOT_GLOBAL_FORMAL','parentElapsedSeconds':1124.080833,'originalBudgetSeconds':1800,'ownedStopElapsedSeconds':27.455229,'independentFinalElapsedSeconds':2.059363,'sameSourceFrozenHost':'PG857','tests':3541,'suites':522,'staticModules':6,'staticIssues':0,'currentSingleSessionNativeStreams':8,'historicalNativeImported':0,'classByteMismatch':0,'newlyCoveredVsHost':gain,'remainingDiagnostic':remaining,'genuineRootAndPid1Done':True,'actualA01UnchangedCurrentDIF001Only':True,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'dbMaxObservationGapNanos':356918139,'wholeWbsAccepted':False,'formalAcceptedDelta':0,'actualAllocatedPp':None,'N':None,'T':None,'evidence':'evidence/01_PT/018_NK-OPS-001/609_当e016_fresh通常起動_仕様・結果.md'}
 public={'schemaVersion':1,**proof,'actualExit':0,'privateNativeManifestSha256':hashlib.sha256(private.read_bytes()).hexdigest(),'frozenHostManifestSha256':m['frozenHostManifestSha256'],'moduleCounters':m['moduleCounters'],'hostOnlyCounters':m['hostOnlyCounters'],'coverage100':m['coverage100'],'formalAccepted':False,'rawExported':False,'input':'Only current new1902 eight immutable source-bound streams, all single sessions/time windows and class bytes independently qualified','expected':'SS343/354 same source/byte/current cohort, no old import, global four counters each100 for final quality','actual':'Native qualification0; global counters remain incomplete','relatedBug':['BUG986'],'command':'python3 -B tools/quality/vm/050_s1/pg879_native_counter.py','osVersion':None,'osVersionNote':'Not freshly measured in this command; do not infer','jdk':'25.0.4','branch':'dev-foundation'}
 p=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG879-current-eight-native-v1/manifest.json';assert not p.exists();changes={p:(None,json.dumps(public,ensure_ascii=False,indent=2)+'\n')}
 p=B/'485_WBS網羅性・受入対応.json';old=p.read_text();seen=[]
 def edit(a):
  if Path(a.get('path','')).stem not in ('MaintenanceRunFiles','MorningNewRunAdmission','MorningResumeAdmission')or '/src/main/java/'not in a.get('path',''):return False
  v=a['candidateProvenance'];assert v['candidateSource']==m['productionSource'];v.update(state='DEPLOYED_NEW_GENUINE_NATIVE8_MEASURED_NOT_GLOBAL',evidence='PG857/858 fresh3541/522/static6zero; signed862; genuine875/A01 876/ownedstop877/post878/native879 eight qualified; 609',newNativePending=False,global100=False);seen.append(a['path']);return True
 new=transform(old,edit);assert len(seen)==3;changes[p]=(old,new)
 p=B/'486_WBS現行実績.json';old=p.read_text();digest=json.loads(old)['inventorySha256'];new=old.replace(digest,hashlib.sha256(changes[B/'485_WBS網羅性・受入対応.json'][1].encode()).hexdigest())
 assert 'currentE016ConnectionObservation'not in new
 new=new.replace('  "schemaVersion": 2,','  "schemaVersion": 2,\n  "currentE016ConnectionObservation": '+json.dumps(proof,ensure_ascii=False,separators=(',',':'))+',',1);changes[p]=(old,new)
 print('*** Begin Patch')
 for p,(old,new)in changes.items():
  if old is None:
   print('*** Add File: '+str(p))
   for l in new.splitlines():print('+'+l)
  else:
   print('*** Update File: '+str(p))
   for l in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]:print('@@'if l.startswith('@@')else l)
 print('*** End Patch')
if __name__=='__main__':main()
