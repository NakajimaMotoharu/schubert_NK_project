"""Single fresh Max/Low analysis of all251 exact safe physical Main classes; no product startup/PT."""
from pathlib import Path
import datetime,hashlib,json,shutil,xml.etree.ElementTree as E
import pg9666_pagination_static as step
from pgpt_spotbugs_contract import canonical_plugin,checked_command,FLAGS
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37782-pure-protocol-web-maxlow-prepare-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and len(p['physicalClassHashes'])==251
work=Path(p['work']);target=work/'target/classes';assert sha(work/'pom.xml')==p['analysisPomSha256']
assert {str(n.relative_to(target)):sha(n) for n in target.rglob('*.class')}==p['physicalClassHashes']
assert all(sha(r/n)==h for n,h in p['sourceHashes'].items()) and all(sha(Path(n))==h for n,h in p['dependencies'].items())
assert E.tostring(canonical_plugin((work/'pom.xml').read_text()))==E.tostring(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()))
out=b/'evidence/PG37784-pure-protocol-web-maxlow-static-v1';assert not out.exists();out.mkdir();step.SLOT=out
cmd=checked_command([str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true',*FLAGS,'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'])
stage=step.step('spotbugs-maxlow251',cmd,work,timeout=240)
report=work/'target/spotbugsXml.xml';assert report.exists();shutil.copyfile(report,out/'spotbugs.xml');t=E.parse(out/'spotbugs.xml').getroot();summary=dict(bugs=len(t.findall('.//BugInstance')),missing=len(t.findall('.//MissingClass')),errors=len(t.findall('.//Error')));stats=sorted(n.get('class') for n in t.findall('.//ClassStats'))
v=dict(actualExit=stage['actualExit'],terminalAtUTC=stage['endUTC'],stage=stage,prepare=ref(pp),sourceCore=p['sourceCore'],physicalClassHashes=p['physicalClassHashes'],dependencies=p['dependencies'],sourceHashes=p['sourceHashes'],spotbugs=summary,classStats=stats,classStatsSetExact={n.replace('.','/')+'.class' for n in stats}==set(p['physicalClassHashes']),spotbugsMaxLowExplicit=True,originalWebQualityPluginExact=True,all251ByteUnchanged={str(n.relative_to(target)):sha(n) for n in target.rglob('*.class')}==p['physicalClassHashes'],newAnalysisOnlyContext=True,noCachedAnalysis=True,MainCompiled=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=v['actualExit'],physical=251,spotbugs=summary,ClassStats=len(stats),setExact=v['classStatsSetExact']))
assert stage['actualExit']==0 and not stage['timedOut'] and all(n==0 for n in summary.values()) and v['classStatsSetExact'] and v['all251ByteUnchanged']
