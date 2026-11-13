"""Frozen full Root PMD/Checkstyle on reviewed five tools/five whole Tests; raw findings retained."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[4];TC=R.parent/'toolchain';W=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG29238-chr-tool-full-static-v1';S=W/'pg29238-chr-tool-full-static-v1';snap=W/'pg29236-chr-whole5-normal46-v1/snapshot'
main=('ArtifactComparator','GateCli','GateContractValidator','TargetAdapter','CorrelatedLogEvidenceValidator');tests=('ArtifactComparatorTest','GateContractTest','GateContractValidatorNegativeTest','TargetAdapterTest','CorrelatedLogEvidenceValidatorTest')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def run():
 assert not P.exists() and not S.exists();P.mkdir();S.mkdir();sg=TC/'static-gates-20261015';java=TC/'jdk-25.0.4/bin/java';paths=[snap/'program/characterization/src/main/java/dev/codex/schubert/characterization'/(n+'.java') for n in main]+[snap/'program/characterization/tests/java/dev/codex/schubert/characterization'/(n+'.java') for n in tests];assert all(p.is_file() for p in paths)
 listing=S/'sources.txt';listing.write_text(''.join(str(p)+'\n' for p in paths));libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
 deps=[TC/'junit-platform-console-standalone-1.13.4.jar',TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',*[TC/'m2/repository/com/fasterxml/jackson/core'/n/'2.19.2'/(n+'-2.19.2.jar') for n in ('jackson-databind','jackson-core','jackson-annotations')]]
 assert all(p.is_file() for p in deps)
 cmds={'pmd':[str(java),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(R/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',':'.join(map(str,[snap/'program/characterization/target/classes',snap/'program/characterization/target/test-classes',*deps])),'--no-cache','--format','xml','--report-file',str(P/'pmd.xml')], 'checkstyle':[str(java),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(P/'checkstyle.xml'),'@'+str(listing)]}
 stages={}
 for label,cmd in cmds.items():
  start=dt.datetime.now(dt.timezone.utc).isoformat()
  with (S/(label+'.log')).open('xb') as f:child=subprocess.run(cmd,cwd=R,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  stages[label]=dict(actualExitCode=child.returncode,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),command=cmd,logSha256=sha(S/(label+'.log')))
  write(S/(label+'-exit.safe.json'),stages[label])
 pmd=ET.parse(P/'pmd.xml').getroot();errors=[dict(n.attrib) for n in pmd.iter() if n.tag.rpartition('}')[2] in ('error','configerror')];raw=[dict(path=n.get('name'),**v.attrib,message=' '.join(''.join(v.itertext()).split())) for n in pmd if n.tag.rpartition('}')[2]=='file' for v in n if v.tag.rpartition('}')[2]=='violation'];cs=ET.parse(P/'checkstyle.xml').getroot();m=dict(source=json.loads((W/'pg29236-chr-whole5-normal46-v1/begin.safe.json').read_text())['source'],stages=stages,inputHashes={str(p.relative_to(snap)):sha(p) for p in paths},rootRuleHashes={str(p.relative_to(R)):sha(p) for p in [R/'tools/quality/static/pmd.xml',R/'tools/quality/static/checkstyle.xml']},rawFindings=raw,processingErrors=errors,checkstyleErrors=len(cs.findall('.//error')),unclassified=len(raw),staticAccepted=False,formalAcceptanceAdded=0,productTestsExecuted=0)
 write(P/'manifest.json',m);print(json.dumps(dict(stages={k:v['actualExitCode'] for k,v in stages.items()},pmdRaw=len(raw),processingErrors=len(errors),checkstyleErrors=m['checkstyleErrors'])))
if __name__=='__main__':run()
