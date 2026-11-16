"""BUG3130 analysis-only contexts retain original rules and bind actual fresh sibling bytes."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile

r=Path.cwd();tc=r.parent/'toolchain';b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
cp=b/'PG36956-backup-path-four-main-compile-v1/manifest.json';c=json.loads(cp.read_text())
sp=b/'PG36846-ssc449-boot-batch-static-v1/manifest.json';s=json.loads(sp.read_text())
assert c['actualExit']==0 and s['stages']['spotbugs']['actualExit']==1
# SDK role graph is unchanged: bind every POM to the same original compile before reuse.
old=json.loads((b/'PG36844-ssc449-four-main-compile-v1/manifest.json').read_text())
assert all(c['inputHashes'][p]==h for p,h in old['inputHashes'].items() if p.endswith('pom.xml'))
assert '## BUG-3130 ' in (r/'documents/900_OTHER/910_台帳/915_障害表.md').read_text()
work=r.parent/'pgpt-runs/PG379/pg36958-backup-path-fresh-sibling-static-v1'
out=b/'PG36958-backup-path-fresh-sibling-spotbugs-v1'
assert not work.exists() and not out.exists();work.mkdir();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
snapshot=Path(c['cwd']);ns={'m':'http://maven.apache.org/POM/4.0.0'}
classdirs={m:snapshot/('src/schubert-nk-'+m)/'target/classes' for m in c['physicalClassHashes']}
for m,p in classdirs.items():assert {str(f.relative_to(p)):sha(f) for f in p.rglob('*.class')}==c['physicalClassHashes'][m]
assert all(sha(r/p)==h==sha(snapshot/p) for p,h in c['inputHashes'].items())
jars={}
for module in ['storage','bootstrap']:
    p=work/('current-'+module+'.jar')
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as jar:
        for name,h in sorted(c['physicalClassHashes'][module].items()):
            raw=(classdirs[module]/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==h
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            jar.writestr(info,raw)
    with zipfile.ZipFile(p) as jar:
        assert set(jar.namelist())==set(c['physicalClassHashes'][module])
        assert all(hashlib.sha256(jar.read(n)).hexdigest()==h for n,h in c['physicalClassHashes'][module].items())
    jars[module]=dict(path=str(p),sha256=sha(p),source=c['sourceCore'],physical=len(c['physicalClassHashes'][module]))
sdk={};contexts={};configs={}
for module in ['bootstrap','batch']:
    entries=[]
    for entry in s['actualCompileClasspaths'][module]['entries']:
        if '/dev/codex/schubert/' in entry:continue
        p=Path(entry)
        assert p.suffix=='.jar' and p.is_file();entries.append(p);sdk[str(p)]=sha(p)
    entries.extend(Path(jars[x]['path']) for x in (['storage'] if module=='bootstrap' else ['storage','bootstrap']))
    original=ET.parse(r/('src/schubert-nk-'+module)/'pom.xml').getroot()
    plugin=next(x for x in original.findall('m:build/m:plugins/m:plugin',ns)
                if x.findtext('m:artifactId',namespaces=ns)=='spotbugs-maven-plugin')
    config=plugin.find('m:configuration',ns);assert config is not None
    configs[module]={x.tag.rsplit('}',1)[-1]:x.text for x in config}
    assert configs[module]==dict(effort='Max',threshold='Low',failOnError='true',xmlOutput='true')
    project=ET.Element('project',xmlns=ns['m'])
    def add(parent,name,value=None):
        item=ET.SubElement(parent,name)
        if value is not None:item.text=str(value)
        return item
    for name,value in [('modelVersion','4.0.0'),('groupId','dev.codex.pgpt.analysis'),
                       ('artifactId','fresh-'+module),('version','1')]:add(project,name,value)
    deps=add(project,'dependencies')
    for i,path in enumerate(dict.fromkeys(entries)):
        dependency=add(deps,'dependency')
        for name,value in [('groupId','dev.codex.pgpt.analysis.input'),('artifactId','input-'+str(i)),
                           ('version','1'),('scope','system'),('systemPath',path)]:add(dependency,name,value)
    build=add(project,'build');add(build,'directory',work/(module+'-target'));add(build,'outputDirectory',classdirs[module])
    plugins=add(build,'plugins');p=add(plugins,'plugin')
    for name,value in [('groupId','com.github.spotbugs'),('artifactId','spotbugs-maven-plugin'),('version','4.10.4.0')]:add(p,name,value)
    cfg=add(p,'configuration')
    for name,value in configs[module].items():add(cfg,name,value)
    pom=work/(module+'-analysis.pom.xml');ET.ElementTree(project).write(pom,encoding='utf-8',xml_declaration=True)
    (out/pom.name).write_bytes(pom.read_bytes());contexts[module]=dict(pom=str(pom),sha256=sha(pom),
       outputDirectory=str(classdirs[module]),classpath=[str(p) for p in dict.fromkeys(entries)])
env={'PATH':str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin','JAVA_HOME':str(tc/'jdk-25.0.4'),
     'HOME':os.environ['HOME'],'LANG':'C.UTF-8'}
def analyze(module):
    command=[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','-B','-ntp',
       '-f',contexts[module]['pom'],'-Dmaven.repo.local='+str(tc/'m2/repository'),
       'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']
    with (out/(module+'.stdout.log')).open('xb') as stdout,(out/(module+'.stderr.log')).open('xb') as stderr:
        try:
            result=subprocess.run(command,cwd=work,env=env,stdout=stdout,stderr=stderr,timeout=240)
            exit_code=result.returncode;timed_out=False
        except subprocess.TimeoutExpired:exit_code=124;timed_out=True
    report=work/(module+'-target/spotbugsXml.xml')
    if report.exists():(out/(module+'-spotbugs.xml')).write_bytes(report.read_bytes())
    return dict(command=command,actualExit=exit_code,timedOut=timed_out,
       stdoutSha256=sha(out/(module+'.stdout.log')),stderrSha256=sha(out/(module+'.stderr.log')))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures={m:executor.submit(analyze,m) for m in contexts};stages={m:f.result() for m,f in futures.items()}
reports={}
for module in contexts:
    report=out/(module+'-spotbugs.xml')
    if not report.exists():reports[module]=dict(missingReport=True);continue
    root=ET.parse(report).getroot();reports[module]=dict(bugs=len(root.findall('.//BugInstance')),
       missingClasses=[n.text for n in root.findall('.//MissingClass')],errors=[n.attrib for n in root.findall('.//Error')],
       classStats=sorted(n.get('class') for n in root.findall('.//ClassStats')),
       projectClasspath=[n.text for n in root.findall('.//Project/AuxClasspathEntry')])
assert all({str(f.relative_to(p)):sha(f) for f in p.rglob('*.class')}==c['physicalClassHashes'][m] for m,p in classdirs.items())
assert all(sha(Path(p))==h for p,h in sdk.items())
manifest=dict(actualExit=0,sourceCore=c['sourceCore'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    compile=ref(cp),originalFailure=ref(sp),contexts=contexts,originalSpotbugsConfigurations=configs,
    freshSiblingArtifacts=jars,sdkHashes=sdk,stages=stages,reports=reports,
    analysisOnly=True,productTestsExecuted=0,actualDbVmNativeServiceActions=0,heldClassfileActions=0,
    noQualityExclusions=True,rawCollectionOnly=True,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,stageExits={k:v['actualExit'] for k,v in stages.items()},
    reports={m:{k:(len(v) if k in ['classStats','projectClasspath'] else v) for k,v in report.items()} for m,report in reports.items()})))
