"""Fresh current Main14/Test3 style; exact existing all251 MaxLow analysis covers all195 unchanged bytes."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
import pg9666_pagination_static as steps
from pgpt_spotbugs_contract import checked_command
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37852-web-forms-complete24-prepare-v2/manifest.json';p=ld(pp);assert p['actualExit']==0 and len(p['physicalClassHashes'])==195
sp=b/'evidence/PG37784-pure-protocol-web-maxlow-static-v1/manifest.json';old=ld(sp);independent=ld(b/'evidence/PG37786-pure-protocol-web-maxlow-independent-v1/manifest.json');assert old['actualExit']==independent['actualExit']==0 and old['classStatsSetExact'] and old['all251ByteUnchanged']
checked_command(old['stage']['command']);assert all(old['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert all(old['physicalClassHashes'][n]==h for n,h in p['physicalClassHashes'].items())
oldstats={n.replace('.','/')+'.class' for n in old['classStats']};assert oldstats==set(old['physicalClassHashes']) and set(p['physicalClassHashes'])<=oldstats
assert all(sha(r/n)==h for n,h in p['inputHashes'].items())
work=Path(p['work']);assert all(sha(work/'component'/n)==h for n,h in p['physicalClassHashes'].items());assert all(sha(Path(n))==h for n,h in p['dependencies'].items())
paths=p['apiMainSources']+p['apiTestSources'];out=b/'evidence/PG37854-web-forms-complete24-static-v1';assert not out.exists();out.mkdir();steps.SLOT=out;listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in paths))
sg=tc/'static-gates-20261015';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];java=tc/'jdk-25.0.4/bin/java';stages={}
stages['pmd']=steps.step('pmd',[str(java),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(work/'component')+':'+':'.join(p['dependencies']),'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')],r)
stages['checkstyle']=steps.step('checkstyle',[str(java),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],r)
stages['format']=steps.step('format',[str(java),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(r/n) for n in paths]],r)
tree=E.parse(out/'pmd.xml').getroot();errors=[dict(n.attrib) for n in tree.iter() if n.tag.rpartition('}')[2] in ['error','configerror']];raw=[dict(path=x.get('name'),rule=y.get('rule'),line=y.get('beginline'),message=(y.text or '').strip()) for x in tree if x.tag.rpartition('}')[2]=='file' for y in x if y.tag.rpartition('}')[2]=='violation']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(pp),inputHashes=p['inputHashes'],stages=stages,rawFindings=raw,processingErrors=errors,checkstyleFindings=len(E.parse(out/'checkstyle.xml').findall('.//error')),spotbugsReuse=dict(original=ref(sp),independent=ref(b/'evidence/PG37786-pure-protocol-web-maxlow-independent-v1/manifest.json'),originalFullClassStats251Unfiltered=True,allCurrent195BytesAnalyzedBefore=True,target19NamesIncluded=True,bugMissingError0=True,explicitMaxLowFailOnError=True,oldProductExecUnchanged=True,analysisReplayed=False),originalMainCompileReplayed=False,productTestsExecuted=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,raw=len(raw),rules=sorted({x['rule'] for x in raw}),checkstyle=v['checkstyleFindings'],stages={k:s['actualExit'] for k,s in stages.items()},current195MaxLowReused=True))
