"""BUG3188: new analysis-only contexts, original18/15 bytes, no Main compile/PT/replayed exec."""
from pathlib import Path
import datetime,hashlib,json,shutil,xml.etree.ElementTree as E
import pg9666_pagination_static as step
import pgpt_closed_host_profile as paths
from pgpt_spotbugs_contract import FLAGS,canonical_plugin,checked_command
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';runs=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
out=b/'evidence/PG37762-web-original18-15-maxlow-static-v1';assert not out.exists();out.mkdir();allrows=[]
settings=E.tostring(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()));ns='{http://maven.apache.org/POM/4.0.0}';E.register_namespace('',ns[1:-1])
for label,oldname,preparename,count in [('public-enum','pg37692-web-enum-eight-v1','PG37692-web-enum-eight-prepare-v1',18),('monitoring','pg37716-web-monitoring41-v1','PG37716-web-monitoring41-prepare-v1',15)]:
    old=runs/oldname;pp=b/'evidence'/preparename/'manifest.json';p=ld(pp);assert p['actualExit']==0 and len(p['mainClassHashes'])==count
    assert all(sha(r/n)==p['inputHashes'][n] for n in p['apiMainSources'])
    assert all(sha(Path(n))==h for n,h in p['dependencies'].items())
    work=runs/('pg37762-maxlow-'+label);assert not work.exists();work.mkdir();target=work/'target/classes';target.mkdir(parents=True)
    for n,h in p['mainClassHashes'].items():
        paths.relative_name(n);source=old/'target/classes'/n;assert sha(source)==h;dest=target/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert sha(dest)==h
    root=E.parse(old/'pom.xml').getroot();plugins=root.find(ns+'build/'+ns+'plugins');assert plugins is not None
    assert not any(x.findtext(ns+'artifactId')=='spotbugs-maven-plugin' for x in plugins)
    plugins.append(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()));E.ElementTree(root).write(work/'pom.xml',encoding='unicode',xml_declaration=True)
    assert E.tostring(canonical_plugin((work/'pom.xml').read_text()))==settings
    slot=out/label;slot.mkdir();step.SLOT=slot
    command=checked_command([str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true',*FLAGS,'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'])
    stage=step.step('spotbugs-max-low',command,work,timeout=180)
    assert stage['actualExit']==0 and not stage['timedOut']
    shutil.copyfile(work/'target/spotbugsXml.xml',slot/'spotbugs.xml');tree=E.parse(slot/'spotbugs.xml').getroot();stats=sorted(n.get('class') for n in tree.findall('.//ClassStats'))
    summary=dict(bugs=len(tree.findall('.//BugInstance')),missing=len(tree.findall('.//MissingClass')),errors=len(tree.findall('.//Error')))
    assert all(x==0 for x in summary.values())
    assert {n.replace('.','/')+'.class' for n in stats}==set(p['mainClassHashes'])
    assert {str(f.relative_to(target)):sha(f) for f in target.rglob('*.class')}==p['mainClassHashes']
    allrows.append(dict(label=label,originalPrepare=ref(pp),oldWork=str(old),newAnalysisOnlyWork=str(work),sourceHashes={n:p['inputHashes'][n] for n in p['apiMainSources']},mainClassHashes=p['mainClassHashes'],dependencies=p['dependencies'],analysisPomSha256=sha(work/'pom.xml'),originalWebContractSha256=hashlib.sha256(settings).hexdigest(),stage=stage,spotbugs=summary,classStats=stats,originalCodeAndUnitExecUnchanged=True,MainCompiled=False,TestsExecuted=0,oldAnalysisReportOverwritten=False))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=allrows,spotbugsSettingsExplicitMaxLow=True,spotbugsFailOnError=True,noAnalysisCacheReused=True,allPhysicalClassesAnalyzed=True,oldUnitAndCoverageReplayed=False,heldClassfileActions=0,actualRootVmDbNativeKeysAuthorityActions=0,originalDefect='BUG3188',crossDeployment='YKT2656',unknownOtherSubsetContextsRemainOpen=True,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,scopes=2,physicalClasses=[len(x['mainClassHashes']) for x in allrows],MainCompiled=False,productTestsExecuted=0))
