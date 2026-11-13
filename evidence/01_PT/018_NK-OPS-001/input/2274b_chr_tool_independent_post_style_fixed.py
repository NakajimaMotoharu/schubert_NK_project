"""Independent frozen-source XML/counter/physical-class/baseline audit; never executes a test."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[4];W=R.parent/'pgpt-runs/PG379';S=W/'pg29246-chr-whole5-normal46-v1';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG29250-chr-tool-independent-post-v1';E=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG29246-chr-whole5-normal46-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
def main():
 assert not P.exists();P.mkdir();begin=json.loads((S/'begin.safe.json').read_text());term=json.loads((S/'exit.safe.json').read_text());assert term['source']==begin['source'] and term['actualExitCode']==0 and not term['timedOut'] and term['beginSha256']==sha(S/'begin.safe.json') and term['logSha256']==sha(S/'maven.log')
 snap=S/'snapshot';target=snap/'program/characterization/target';assert all(sha(snap/p)==h for p,h in begin['inputHashes'].items());assert inventory(R/'program/characterization/baseline/current')==begin['originalBaselineHashes']
 assert subprocess.check_output(['git','diff','--name-only',begin['source'],'--','program/characterization','pom.xml'],cwd=R)==b''
 expected={'ArtifactComparatorTest':9,'GateContractTest':8,'GateContractValidatorNegativeTest':17,'TargetAdapterTest':3,'CorrelatedLogEvidenceValidatorTest':9};xmls=list((target/'surefire-reports').glob('TEST-*.xml'));assert len(xmls)==5
 rows=[];cases=[]
 for p in sorted(xmls):
  t=ET.parse(p).getroot();name=t.get('name').rsplit('.',1)[1];assert name in expected and int(t.get('tests'))==expected[name];assert all(int(t.get(k))==0 for k in ('failures','errors','skipped'));tests=t.findall('testcase');assert len(tests)==expected[name] and all(not list(x) for x in tests)
  cases +=[(x.get('classname'),x.get('name')) for x in tests];rows.append(dict(name=name,tests=len(tests),failures=0,errors=0,skipped=0,privateXmlSha256=sha(p)))
  # Explicitly remove JVM properties (not test results), retain original input hash for audit.
  prop=t.find('properties')
  if prop is not None:t.remove(prop)
  ET.indent(t);ET.ElementTree(t).write(P/p.name,encoding='utf-8',xml_declaration=True)
 assert len(cases)==len(set(cases))==46
 tree=ET.parse(target/'site/jacoco/jacoco.xml');root=tree.getroot();classes={x.get('name')+'.class':x for x in root.findall('.//class')};physical=inventory(target/'classes');assert set(classes)==set(physical) and len(classes)==10
 sb=ET.parse(target/'spotbugsXml.xml').getroot();assert all(not sb.findall('.//'+n) for n in ('BugInstance','MissingClass','Error'));assert {x.get('class').replace('.','/')+'.class' for x in sb.findall('.//ClassStats')}==set(physical)
 counters=lambda n:[dict(x.attrib) for x in n.findall('counter')]
 classc={name:counters(x) for name,x in classes.items()};methodc={x.get('name'):{y.get('name'):counters(y) for y in x.findall('method') if y.get('name') in ('secretScan','containsAny','prefixes')} for x in classes.values() if x.get('name').endswith('GateCli')}
 # Coverage instrumentation IDs are not published. No authentication/session material is read.
 for n in list(root.findall('sessioninfo')):root.remove(n)
 tree.write(P/'jacoco.xml',encoding='utf-8',xml_declaration=True);shutil.copyfile(target/'spotbugsXml.xml',P/'spotbugs.xml')
 m=dict(source=begin['source'],operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),independentPostAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExitCode=0,originalTerminal=term,wholeClasses=rows,totalToolTests=46,failures=0,errors=0,skipped=0,allTestIdentities=cases,physicalClassHashes=physical,physicalCounters=classc,allCounters=counters(root),changedScannerMethodCounters=methodc,artifactComparatorAllPhysicalFour100=all(int(c['missed'])==0 for n,cs in classc.items() if '/ArtifactComparator' in n for c in cs if c['type'] in ('LINE','METHOD','CLASS','BRANCH')),baselineUnchanged=True,sourceInputsUnchanged=True,rawCoverageSha256=sha(target/'site/jacoco/jacoco.xml'),privateExecSha256=sha(target/'jacoco.exec'),pmdReview='PG29248 raw findings await per-site applicability; not accepted',wholeGateCliTest='HOLD12 actual20GiB unavailable',fullBundleAccepted=False,formalAcceptanceAdded=0,appNormalRosterDelta=0,toolNormalSuccesses=46,effortCompletionRate=None,verifierSha256=sha(Path(__file__)))
 (P/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExitCode=0,toolTests=46,allPhysicalClasses=10,baselineUnchanged=True,fullBundleAccepted=False)))
if __name__=='__main__':main()
