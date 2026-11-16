"""PMD full287 current Main, unchanged original rules/SDK and fresh class directories."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=load(b/'PG36846-ssc449-boot-batch-static-v1/manifest.json')
original=load(b/'PG36844-ssc449-four-main-compile-v1/manifest.json')
cp=b/'PG36956-backup-path-four-main-compile-v1/manifest.json';current=load(cp)
assert current['actualExit']==0
assert all(current['inputHashes'][p]==h for p,h in original['inputHashes'].items() if p.endswith('pom.xml'))
assert all(sha(Path(p))==h for p,h in old['toolAndSdkHashes'].items())
assert sha(r/'tools/quality/static/pmd.xml')==old['fullRootRuleset']
for module,expected in current['physicalClassHashes'].items():
    folder=Path(current['cwd'])/('src/schubert-nk-'+module)/'target/classes'
    assert {str(p.relative_to(folder)):sha(p) for p in folder.rglob('*.class')}==expected
sources=sorted(p for p in current['inputHashes'] if p.endswith('.java') and any(p.startswith('src/schubert-nk-'+m+'/') for m in ['bootstrap','batch']))
assert len(sources)==287 and all(sha(r/p)==current['inputHashes'][p] for p in sources)
out=b/'PG36960-current287-root-pmd-v1';assert not out.exists();out.mkdir()
listing=out/'sources.txt';listing.write_text(''.join(str(r/p)+'\n' for p in sources))
command=[v.replace(original['cwd'],current['cwd']) for v in old['stages']['pmd']['command']]
command[command.index('--file-list')+1]=str(listing)
command[command.index('--report-file')+1]=str(out/'pmd.xml')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (out/'pmd.stdout.log').open('xb') as stdout,(out/'pmd.stderr.log').open('xb') as stderr:
    result=subprocess.run(command,cwd=current['cwd'],stdout=stdout,stderr=stderr,timeout=120)
assert result.returncode in [0,4]
raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
    tag=node.tag.rsplit('}',1)[-1]
    if tag in ['error','configerror']:errors.append(dict(node.attrib))
    if tag=='file':
        for item in node:
            if item.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**item.attrib,message=(item.text or '').strip()))
assert not errors
assert all(sha(r/p)==h for p,h in current['inputHashes'].items())
(out/'raw-findings.json').open('x').write(json.dumps(raw,indent=2)+'\n')
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,actualToolExit=result.returncode,
    sourceCore=current['sourceCore'],sourceInputs={p:current['inputHashes'][p] for p in sources},
    command=command,cwd=current['cwd'],startAtUTC=start,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    mainCount=287,rawFindings=len(raw),processingErrors=errors,originalFullRulesetSha256=old['fullRootRuleset'],
    originalToolAndSdkHashes=old['toolAndSdkHashes'],freshSiblingClassDirs=True,
    files={p.name:sha(p) for p in out.iterdir() if p.is_file()},productTestsExecuted=0,
    rawCollectionOnly=True,wholeF03Accepted=False,formalUpdated=False),indent=2)+'\n')
print(json.dumps(dict(actualExit=0,toolExit=result.returncode,mainCount=287,raw=len(raw),processingErrors=0)))
