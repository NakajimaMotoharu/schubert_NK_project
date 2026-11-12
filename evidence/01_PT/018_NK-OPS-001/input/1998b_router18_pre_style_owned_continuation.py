"""BUG2739 append-only continuation: never reexecute or overwrite the seven completed stages."""
from pathlib import Path
import ast,hashlib,json,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG28100-router18-pre-style-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());assert O.exists() and not (O/'manifest.json').exists();c.SLOT=O;listing=O/'sources.txt';paths=[Path(x) for x in listing.read_text().splitlines()];assert len(paths)==9 and len(set(paths))==9;stages={};done=set()
for q in sorted(O.glob('*-exit.safe.json')):
 label=q.name.removesuffix('-exit.safe.json');x=ld(q);assert x['actualExit']==0 and not x['timedOut']
 for stream in ['stdout','stderr']:assert sha(O/(label+'.'+stream))==x[stream+'Sha256']
 if label.startswith('format-'):p=Path(x['command'][-1]);assert p in paths and p not in done;done.add(p)
 else:assert label=='style-pmd' and '--file-list' in x['command'] and str(listing) in x['command']
 stages[label]=x
assert len(stages)==7 and len(done)==6
for p in paths:
 if p in done:continue
 label='format-'+str(p.relative_to(R)).replace('/','_').removesuffix('.java');assert label not in stages
 stages[label]=c.step(label,[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',str(p)],R);done.add(p)
stages['checkstyle']=c.step('checkstyle',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*[str(p) for p in paths]],R)
rt=ET.parse(O/'pmd.xml').getroot();errors=[dict(x.attrib) for x in rt.iter() if x.tag.rpartition('}')[2] in ['error','configerror']];findings=[dict(path=x.get('name'),rule=y.get('rule'),line=y.get('beginline'),message=(y.text or '').strip()) for x in rt if x.tag.rpartition('}')[2]=='file' for y in x if y.tag.rpartition('}')[2]=='violation'];assert not errors and done==set(paths) and len(stages)==11
v=dict(actualExit=0,preliminaryOnly=True,fullQualityGateSatisfied=False,fullRootRulesetUnchangedSha256=sha(R/'tools/quality/static/pmd.xml'),stages=stages,rawFindings=findings,checkstyleFindings=len(ET.parse(O/'checkstyle.xml').findall('.//error')),processingErrors=errors,inputHashes={str(p.relative_to(R)):sha(p) for p in paths},productTestsExecuted=0,MainCompiled=False,MainChanged=False,reusedCompletedStages=7,newStages=4,bug2739='UNIQUE_PATH_LABELS_9_PATH_COMMANDS_BIJECTIVE_NO_OVERWRITE',verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=len(findings),checkstyle=v['checkstyleFindings'],stageExits={k:x['actualExit'] for k,x in stages.items()},noDuplicateExecutions=True)))
