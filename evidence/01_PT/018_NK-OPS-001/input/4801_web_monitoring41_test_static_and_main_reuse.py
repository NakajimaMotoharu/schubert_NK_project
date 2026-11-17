"""Fresh changed-Test style/PMD, unchanged actual15 Main SpotBugs reuse by byte and dependency pins."""
from pathlib import Path
import datetime, hashlib, json, shutil, xml.etree.ElementTree as E
import pg9666_pagination_static as steps

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; tc=r.parent/'toolchain'
load=lambda p:json.loads(p.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37730-web-monitoring41-final-prepare-v3/manifest.json'; p=load(pp)
oldp=load(b/'evidence/PG37724-web-monitoring41-final-prepare-v2/manifest.json')
oldpath=b/'evidence/PG37726-web-monitoring41-final-static-v2/manifest.json'; old=load(oldpath)
assert old['actualExit']==p['actualExit']==0 and oldp['mainClassHashes']==p['mainClassHashes'] and oldp['dependencies']==p['dependencies']
assert all(oldp['inputHashes'][n]==p['inputHashes'][n]==sha(r/n) for n in p['apiMainSources'])
assert all(old['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert {n.replace('.','/')+'.class' for n in old['spotbugs']['classStats']}==set(p['mainClassHashes'])
work=r.parent/'pgpt-runs/PG379/pg37730-web-monitoring41-final-v3'
assert all(sha(work/'target/classes'/n)==h for n,h in p['mainClassHashes'].items())
out=b/'evidence/PG37732-web-monitoring41-final-static-v3'; assert not out.exists(); out.mkdir(); steps.SLOT=out
paths=p['apiMainSources']+p['apiTestSources']; listing=out/'sources.txt'
listing.write_text(''.join(str(r/n)+'\n' for n in paths))
sg=tc/'static-gates-20261015'; libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]; java=tc/'jdk-25.0.4/bin/java'
stages={}
stages['pmd']=steps.step('pmd',[str(java),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(work/'target/classes')+':'+':'.join(p['dependencies']),'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')],r)
stages['checkstyle']=steps.step('checkstyle',[str(java),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],r)
stages['format']=steps.step('format',[str(java),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(r/n) for n in paths]],r)
tree=E.parse(out/'pmd.xml').getroot(); errors=[dict(n.attrib) for n in tree.iter() if n.tag.rpartition('}')[2] in ['error','configerror']]
raw=[dict(path=x.get('name'),rule=y.get('rule'),line=y.get('beginline'),message=(y.text or '').strip()) for x in tree if x.tag.rpartition('}')[2]=='file' for y in x if y.tag.rpartition('}')[2]=='violation']
shutil.copyfile(oldpath.parent/'spotbugs.xml',out/'spotbugs.xml')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(pp),inputHashes=p['inputHashes'],stages=stages,
    rawFindings=raw,processingErrors=errors,checkstyleFindings=len(E.parse(out/'checkstyle.xml').findall('.//error')),
    spotbugs=old['spotbugs'],spotbugsReuse=dict(originalStatic=ref(oldpath),reportSha256=sha(out/'spotbugs.xml'),same15ActualMainClassBytes=True,sameSdkHashes=True,MainReanalyzedForConfirmation=False),
    originalMainCompileReplayed=False,productTestsExecuted=0)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(dict(actualExit=0,raw=len(raw),rules=sorted({x['rule'] for x in raw}),cs=v['checkstyleFindings'],spotbugs15ReusedNotReplayed=True))
