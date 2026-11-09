"""Derive natural-zero-branch metadata from published XML scopes; never manufacture branch100 for an empty denominator."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001/evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def counter_map(node):
 result={}
 for c in node.findall('counter'):
  name=c.get('type');covered=c.get('covered');missed=c.get('missed');assert name and name not in result and isinstance(covered,str) and covered.isascii() and covered.isdecimal() and isinstance(missed,str) and missed.isascii() and missed.isdecimal();result[name]=dict(covered=int(covered),missed=int(missed))
 return result

def classify(nodes):
 assert nodes
 rows=[]
 for node in nodes:
  counters=counter_map(node);branch=counters.get('BRANCH');total=0 if branch is None else branch['covered']+branch['missed'];nonemptyFour=all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']);rows.append(dict(name=node.get('name'),counters=counters,naturalZeroBranch=total==0,branchDenominator=total,branchPercent=None if total==0 else 100*branch['covered']/total,branchStatus='N/A_NO_BRANCH' if total==0 else ('COVERED' if branch['missed']==0 else 'MISSED'),nonemptyFour100=nonemptyFour))
 return dict(entryCount=len(rows),naturalZeroBranchCount=sum(x['naturalZeroBranch'] for x in rows),naturalZeroBranchNames=sorted(x['name'] for x in rows if x['naturalZeroBranch']),allEntriesNonemptyFour100=all(x['nonemptyFour100'] for x in rows),entries=rows)

def checked_optional_int(m,key,actual):
 if key not in m:return dict(present=False,reported=None,effective=actual,status='OPTIONAL_FIELD_ABSENT_DERIVED_SUPPLEMENT_NOT_ZERO')
 value=m[key];assert type(value) is int and value>=0;return dict(present=True,reported=value,effective=actual,status='MATCH' if value==actual else 'METADATA_CORRECTION_REQUIRED')

def main():
 ids=[24874,24922,24964,24988,25012,25034,25054,25074,25094,25114,25134,25154,25172,25208,25228,25262,25288,25312,25332,25352,25382,25412,25454,25502];O=B/'PG25512-natural-branch24-metadata-supplement-v1';assert not O.exists();rows=[];cases=[]
 for run in ids:
  candidates=list(B.glob('PG'+str(run)+'-*'));assert len(candidates)==1;p=candidates[0];mp=p/'manifest.json';xp=p/'coverage.xml';m=json.loads(mp.read_bytes());assert type(m['actualExit']) is int and m['actualExit']==0 and m['newAcceptance']==0 and m['formalUpdated'] is False and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';x=E.parse(xp).getroot();classes=classify(x.findall('.//class'));sources=classify(x.findall('.//sourcefile'));assert type(m['allSourceFour100']) is bool and m['allSourceFour100']==sources['allEntriesNonemptyFour100'];classField=checked_optional_int(m,'naturalZeroBranchClasses',classes['naturalZeroBranchCount']);sourceField=checked_optional_int(m,'naturalZeroBranchSources',sources['naturalZeroBranchCount']);assert sourceField['status']=='MATCH'
  testXml=p/'testcases.safe.xml';testRoot=E.parse(testXml).getroot();pairs=[(t.get('classname'),t.get('name')) for t in testRoot.findall('testcase')];assert len(pairs)==len(set(pairs))==m['existingTestsRequalified'] and all(not any(t.findall(k) for k in ['failure','error','skipped']) for t in testRoot.findall('testcase'));cases.extend(pairs)
  rows.append(dict(run=run,manifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),coverageXml=dict(path=str(xp.relative_to(R)),sha256=sha(xp)),testcaseXml=dict(path=str(testXml.relative_to(R)),sha256=sha(testXml)),source=m['source'],productionCoreMain=m['productionCoreMain'],recordedExistingTests=len(pairs),classField=classField,sourceField=sourceField,classDetails=classes,sourceDetails=sources,sourceFourGateUnchanged=True,originalArtifactsUnchanged=True))
 assert len(rows)==24 and len(cases)==len(set(cases));corrections=[x for x in rows if x['classField']['status']=='METADATA_CORRECTION_REQUIRED'];unreported=[x for x in rows if not x['classField']['present']];assert [x['run'] for x in corrections]==[25288] and corrections[0]['classField']['reported']==0 and corrections[0]['classField']['effective']==2;assert [x['run'] for x in unreported]==[24874,24922]
 O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),scope='EXPLICIT_24_PUBLISHED_DYNAMIC_POSTS_METADATA_ONLY',rowCount=24,rows=rows,correctedClassFieldReports=len(corrections),optionalClassFieldsDerived=len(unreported),alreadyMatchingClassFieldReports=24-len(corrections)-len(unreported),sourceCountAndNonemptyFourGatesAllUnchanged=True,recordedExistingCasePairs=len(cases),distinctRecordedCasePairs=len(set(cases)),distinctRecordedWholeTestClasses=len({c for c,n in cases}),existingRecordedExecutionsAreNotNewTests=True,productTestsExecuted=0,newProductTests=0,oldSuccessfulProductRunsReexecuted=0,execOrCoverageUnion=False,coverageCountersChanged=False,originalArtifactsOverwritten=False,whole451Accepted=False,formalUpdated=False,newAcceptance=0,effortRate=None,bug='BUG-2601',ykt='YKT-2297',sourceCodeChanged=False,classfilesRead=False,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reports=24,correctedClassFieldReports=len(corrections),missingOptionalFieldsDerived=len(unreported),allSourceGatesUnchanged=True,recordedCasePairs=len(cases),wholeTestClasses=len({c for c,n in cases}),productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))

if __name__=='__main__':main()
