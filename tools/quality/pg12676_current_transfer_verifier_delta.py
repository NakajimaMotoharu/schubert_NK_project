"""Three original verifier Test corrections only, no raw suppression or new context credit."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12656_current_run_session_delta import state_after as previous_state

SOURCE='8ccadeed207cf1f38264c35199bd4def12aae6c3'
OUT=data.BASE/'PG12676-current-transfer-verifier-delta-v1'
POST=data.BASE/'PG12678-current-transfer-verifier-delta-post-v1'
REMOVED={'PMD-02669','PMD-02670','PMD-02671'}

def state_after():
 ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
 return ids-REMOVED,refs,pending

def expected():
 plan=data.read_checked(data.BASE/'PG12664-transfer-verifier-plan-v1/manifest.json','ea86a69bf4b7ca5d5aa70d7d1f825b6f80b1ee543eaeaca122dbb113c90bb155')
 static=data.read_checked(data.BASE/'PG12670-transfer-verifier-static-v1/manifest.json','9aadfc3732078e310172ff095fd03290e3544530e662db99ef341fbd98dddbe8')
 proof=data.read_checked(data.BASE/'PG12672-transfer-verifier-post-v1/manifest.json','5606c98f263fd7d0aeb157199382fad6b8513c51955c383f5bd7f20511483ad7')
 assert static['source']==proof['source']==SOURCE and static['actualExit']==proof['actualExit']==0 and proof['observedTestExecutions']==3 and proof['ownedTempRootEmptyAfter'] and proof['renamedInnerMapping']['after'].endswith('$ChunkedInput.class')
 changes={r['path']:r for r in plan['sourceChanges']};assert len(changes)==1 and static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
 for label,v in static['reports'].items():
  assert v['findings']==v['processingErrors']==0
  raw=(data.BASE/'PG12670-transfer-verifier-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
  assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ['violation','error','configerror']]
 original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
 scope=[r for r in original if r['path'] in changes];assert len(scope)==3 and {r['id'] for r in scope}==REMOVED and all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in scope)
 assert {r['rule'] for r in scope}=={'CloseResource','TestClassWithoutTestCases','AvoidLiteralsInIfCondition'}
 ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8498,3175,784,5323]
 assert len({r['id'] for r in original}-ids)==919 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
 return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=[],sourceReboundExistingContextIds=[],newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8498,mainRaw=1506,testRaw=6992,totalPriorCorrections=919,joinedContextWarnings=3175,sourceReboundCurrentWholePending=784,noCurrentReferenceInThisJoin=5323,oldScopeFindings=3,newScopeFindings=0,newContextClassifications=0,newSourceRebindings=0,staticActualExit=0,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)

def main():
 invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',v)
 data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
 invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
 assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
 def require(v):
  if v!=reference:raise ValueError('exact original scope removal and unchanged contexts required')
 require(candidate);labels=[]
 for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',920),('newAccepted',1),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('newContextClassifications',1),('newSourceRebindings',1),('staticActualExit',1)]:
  bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
  try:require(bad)
  except ValueError:labels.append(field)
  else:raise AssertionError('invalid static correction credit accepted')
 verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8498,totalPriorCorrections=919,joinedContextWarnings=3175,sourceReboundCurrentWholePending=784,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':main()
