"""Changed-five Main-only PMD/Checkstyle; no Product invocation or dynamic fixture."""
from pathlib import Path
import datetime,hashlib,json,sys
import pg9666_pagination_static as c
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
normalp=r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json';normal=load(normalp);assert normal['actualExit']==0 and normal['source']=='56720d75714f60d7e31da59c3da8c02baf05de52';assert sha(normalp)=='e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
oldp=r/'evidence/01_PT/006_NK-MSG-002/evidence/PG21012-outbox-null-oracle-static-v1';pmd=load(oldp/'pmd-begin.safe.json')['command'];cs=load(oldp/'checkstyle-begin.safe.json')['command'];names=normal['begin']['changes'];assert len(names)==5
for n in names:assert sha(r/n)==normal['begin']['inputHashes'][n] and '/src/main/java/' in n
slot=r.parent/'pgpt-runs/PG379/pg21926-consumer-stop-five-style-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot
filelist=slot/'source-list.txt';filelist.write_text('\n'.join(str(r/n) for n in names)+'\n')
for flag,value in [('--file-list',str(filelist)),('--report-file',str(slot/'pmd.xml'))]:pmd[pmd.index(flag)+1]=value
aux=pmd[pmd.index('--aux-classpath')+1];aux=aux.replace('pg20990-outbox-required-six-main-compile-v1','pg21922-consumer-stop-six-main-compile-v1');aux=':'.join(n for n in aux.split(':') if 'junit-platform-console' not in n)
sdk=load(r.parent/'pgpt-runs/PG379/pg21818-jms-reply-current-codec-compile-v1/context.safe.json')['runtimeInputs']
aux += ':'+':'.join(n for n in sdk if Path(n).name.startswith(('jakarta.jms-api-','artemis-jms-client-','artemis-core-client-','artemis-commons-')))
pmd[pmd.index('--aux-classpath')+1]=aux;cs[cs.index('-o')+1]=str(slot/'checkstyle.xml');cs[-1]='@'+str(filelist)
write(slot/'begin.safe.json',dict(source=normal['source'],inputHashes={n:sha(r/n) for n in names},commands=dict(pmd=pmd,checkstyle=cs),productExecution=False,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
a=c.step('pmd',pmd,r,timeout=120);b=c.step('checkstyle',cs,r,timeout=120)
assert a['actualExit'] in [0,4] and not a['timedOut'] and b['actualExit'] in [0,1] and not b['timedOut'];value=dict(source=normal['source'],actualExit=0,stages=dict(pmd=a,checkstyle=b),inputHashes={n:sha(r/n) for n in names},classification='RAW_FINDINGS_PENDING_INDIVIDUAL_REVIEW_NOT_STATIC_PASS',findingsClassified=False,productTestsExecuted=0,newAcceptance=0);write(slot/'raw-manifest.safe.json',value)
print(json.dumps(dict(actualExit=0,pmdRawExit=a['actualExit'],checkstyleRawExit=b['actualExit'],rawManifestSha256=sha(slot/'raw-manifest.safe.json'))))
sys.exit(0)
