"""Independent literal vectors and immutable published XML metadata reconciliation, no Java execution."""
from pathlib import Path
import datetime,hashlib,json,runpy,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
T=B/'input/983_natural_branch_metadata_audit.py';A=B/'evidence/PG25512-natural-branch24-metadata-supplement-v1/manifest.json';O=B/'evidence/PG25514-natural-branch24-independent-v1';assert not O.exists();a=json.loads(A.read_bytes());assert a['actualExit']==0 and a['rowCount']==24
f=runpy.run_path(str(T));classify=f['classify'];optional=f['checked_optional_int'];checks=[]
def accept(label,node,zero,percent,status,gate):
 v=classify([X.fromstring(node)]);r=v['entries'][0];assert (v['naturalZeroBranchCount'],r['branchPercent'],r['branchStatus'],v['allEntriesNonemptyFour100'])==(zero,percent,status,gate);checks.append(label)
def reject(label,call):
 try:call()
 except (AssertionError,ValueError,TypeError):checks.append(label);return
 raise AssertionError(label)
base='<class name="literal"><counter type="LINE" covered="1" missed="0"/><counter type="METHOD" covered="1" missed="0"/><counter type="CLASS" covered="1" missed="0"/>{}</class>'
accept('missing BRANCH is N/A',base.format(''),1,None,'N/A_NO_BRANCH',False)
accept('explicit zero BRANCH is N/A',base.format('<counter type="BRANCH" covered="0" missed="0"/>'),1,None,'N/A_NO_BRANCH',False)
accept('nonempty complete branch',base.format('<counter type="BRANCH" covered="2" missed="0"/>'),0,100,'COVERED',True)
accept('all missed is not N/A',base.format('<counter type="BRANCH" covered="0" missed="2"/>'),0,0,'MISSED',False)
accept('partial missed is not N/A',base.format('<counter type="BRANCH" covered="1" missed="1"/>'),0,50,'MISSED',False)
accept('branch full cannot hide method miss',base.format('<counter type="BRANCH" covered="2" missed="0"/>').replace('type="METHOD" covered="1" missed="0"','type="METHOD" covered="0" missed="1"'),0,100,'COVERED',False)
reject('empty scope',lambda:classify([]))
for bad in ['-1','1.0','true','１２','']:
 reject('invalid counter '+repr(bad),lambda bad=bad:classify([X.fromstring(base.format('<counter type="BRANCH" covered="'+bad+'" missed="0"/>'))]))
reject('duplicate counter',lambda:classify([X.fromstring(base.format('<counter type="BRANCH" covered="1" missed="0"/><counter type="BRANCH" covered="1" missed="0"/>'))]))
for value in [-1,True,'0',None]:reject('invalid declared '+repr(value),lambda value=value:optional({'naturalZeroBranchClasses':value},'naturalZeroBranchClasses',2))
missing=optional({},'naturalZeroBranchClasses',2);assert missing['present'] is False and missing['reported'] is None and missing['effective']==2;checks.append('absent differs from zero')
wrong=optional({'naturalZeroBranchClasses':0},'naturalZeroBranchClasses',2);assert wrong['status']=='METADATA_CORRECTION_REQUIRED';checks.append('incorrect declaration requires correction')
matched=optional({'naturalZeroBranchClasses':2},'naturalZeroBranchClasses',2);assert matched['status']=='MATCH';checks.append('matching declaration')
# Independently sum raw XML, with no use of imported classification helpers.
for row in a['rows']:
 for key in ['manifest','coverageXml','testcaseXml']:assert sha(R/row[key]['path'])==row[key]['sha256']
 root=X.parse(R/row['coverageXml']['path']).getroot()
 for kind,tag in [('classDetails','class'),('sourceDetails','sourcefile')]:
  nodes=root.findall('.//'+tag);actual=[];full=True
  for node in nodes:
   counts={c.attrib['type']:(int(c.attrib['covered']),int(c.attrib['missed'])) for c in node.findall('counter')}
   if sum(counts.get('BRANCH',(0,0)))==0:actual.append(node.attrib['name'])
   if any(k not in counts or counts[k][0]<=0 or counts[k][1]!=0 for k in ['LINE','METHOD','CLASS','BRANCH']):full=False
  assert len(nodes)==row[kind]['entryCount'] and sorted(actual)==row[kind]['naturalZeroBranchNames'] and len(actual)==row[kind]['naturalZeroBranchCount'] and full is row[kind]['allEntriesNonemptyFour100']
  # Every raw counter in supplement remains identical to independent original XML.
  for node,entry in zip(nodes,row[kind]['entries']):
   assert entry['name']==node.attrib['name']
   assert entry['counters']=={c.attrib['type']:{'covered':int(c.attrib['covered']),'missed':int(c.attrib['missed'])} for c in node.findall('counter')}
 assert row['sourceFourGateUnchanged'] is True
assert (a['correctedClassFieldReports'],a['optionalClassFieldsDerived'],a['alreadyMatchingClassFieldReports'],a['recordedExistingCasePairs'],a['distinctRecordedCasePairs'],a['distinctRecordedWholeTestClasses'])==(1,2,21,515,515,57)
assert all(a[k] is False for k in ['execOrCoverageUnion','coverageCountersChanged','originalArtifactsOverwritten','whole451Accepted','formalUpdated','sourceCodeChanged','classfilesRead']) and a['productTestsExecuted']==a['newProductTests']==a['newAcceptance']==0 and a['effortRate'] is None
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),auditManifest={'path':str(A.relative_to(R)),'sha256':sha(A)},toolSha256=sha(T),independentToolSha256=sha(Path(__file__)),metadataChecks=len(checks),checks=checks,originalReportHashesRechecked=24,independentXmlScopesChecked=48,originalArtifactsUnchanged=True,independentCounterDerivationMatches=True,recordedExistingCases=515,recordedWholeClasses=57,productTestsExecuted=0,newProductTests=0,newAcceptance=0,formalUpdated=False,coverageCountersChanged=False,whole451Accepted=False,effortRate=None,bug='BUG-2601',ykt='YKT-2297');(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,metadataChecks=len(checks),reports=24,manifestSha256=sha(O/'manifest.json'))))
