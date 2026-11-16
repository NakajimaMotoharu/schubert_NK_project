"""Current actual reactor static checks, SDK compile graph, no product tests or entrypoints."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();tc=r.parent/'toolchain';b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
cp=b/'PG36844-ssc449-four-main-compile-v1/manifest.json';c=json.loads(cp.read_text())
assert c['actualExit']==0 and c['mainCount']==477
work=Path(c['cwd']);out=b/'PG36846-ssc449-boot-batch-static-v1'
assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
modules=['protocol','storage','bootstrap','batch'];selected=['bootstrap','batch']
classdirs={m:work/('src/schubert-nk-'+m)/'target/classes' for m in modules}
assert all({str(p.relative_to(classdirs[m])):sha(p) for p in classdirs[m].rglob('*.class')}==c['physicalClassHashes'][m] for m in modules)
env={'PATH':str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin','JAVA_HOME':str(tc/'jdk-25.0.4'),
     'HOME':os.environ['HOME'],'LANG':'C.UTF-8'}
mvn=[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','-B','-ntp',
     '-Dmaven.repo.local='+str(tc/'m2/repository'),'-pl',
     ','.join('src/schubert-nk-'+m for m in selected),'-am']
def run(name,command):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
        try:
            result=subprocess.run(command,cwd=work,env=env,stdout=stdout,stderr=stderr,timeout=240)
            exit_code=result.returncode;timed_out=False
        except subprocess.TimeoutExpired:exit_code=124;timed_out=True
    return dict(command=command,actualExit=exit_code,timedOut=timed_out,
        startAtUTC=start,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        stdoutSha256=sha(out/(name+'.stdout.log')),stderrSha256=sha(out/(name+'.stderr.log')))
stages={}
stages['compile-dependencies']=run('compile-dependencies',mvn+[
    'org.apache.maven.plugins:maven-dependency-plugin:3.9.0:build-classpath',
    '-DincludeScope=compile','-Dmdep.outputFile=target/ssc449-compile-classpath.txt'])
assert stages['compile-dependencies']['actualExit']==0,'keep original failure; no implicit retry'
sdk=set();declared={}
for module in ['storage',*selected]:
    p=work/('src/schubert-nk-'+module)/'target/ssc449-compile-classpath.txt'
    text=p.read_text().strip();declared[module]=dict(path=str(p),sha256=sha(p),entries=text.split(os.pathsep) if text else [])
    for entry in declared[module]['entries']:
        path=Path(entry)
        if path.suffix=='.jar' and '/dev/codex/schubert/' not in entry:
            assert path.is_file();sdk.add(path)
qual=tc/'m2/repository/org/checkerframework/checker-qual/3.55.1/checker-qual-3.55.1.jar'
assert all(str(qual) in declared[module]['entries'] for module in selected)
sources=sorted(p for p in c['inputHashes'] if p.endswith('.java') and
               any(p.startswith('src/schubert-nk-'+m+'/') for m in selected))
assert len(sources)==287
listing=out/'sources.txt';listing.write_text(''.join(str(r/p)+'\n' for p in sources))
sg=tc/'static-gates-20261015'
libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
rule=r/'tools/quality/static/pmd.xml'
assert rule.read_bytes()==subprocess.check_output(['git','show','1634e3884a7b645f50b3552642ed4a1844736ab5:tools/quality/static/pmd.xml'])
aux=[tc/'jdk-25.0.4/lib/jrt-fs.jar',*classdirs.values(),*sorted(sdk)]
commands={
 'pmd':[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join(map(str,libs)),
    'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rule),
    '--use-version','java-25','--aux-classpath',':'.join(map(str,aux)),'--no-cache',
    '--format','xml','--report-file',str(out/'pmd.xml')],
 'spotbugs':mvn+['com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    futures={name:pool.submit(run,name,command) for name,command in commands.items()}
    stages.update({name:future.result() for name,future in futures.items()})
raw=[];errors=[];pd=ET.parse(out/'pmd.xml').getroot()
for node in pd.iter():
    tag=node.tag.rsplit('}',1)[-1]
    if tag in ['error','configerror']:errors.append(dict(node.attrib))
    if tag=='file':
        for item in node:
            if item.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(
                path=str(Path(node.get('name')).relative_to(r)),**item.attrib,message=(item.text or '').strip()))
reports={}
for module in ['storage',*selected]:
    file=work/('src/schubert-nk-'+module)/'target/spotbugsXml.xml'
    if not file.exists():reports[module]=dict(missingReport=True);continue
    (out/(module+'-spotbugs.xml')).write_bytes(file.read_bytes());root=ET.parse(file).getroot()
    reports[module]=dict(bugs=len(root.findall('.//BugInstance')),
        missingClasses=[n.text for n in root.findall('.//MissingClass')],errors=[n.attrib for n in root.findall('.//Error')],
        classStats=sorted(n.get('class') for n in root.findall('.//ClassStats')),
        projectClasspath=[n.text for n in root.findall('.//Project/AuxClasspathEntry')])
assert all({str(p.relative_to(classdirs[m])):sha(p) for p in classdirs[m].rglob('*.class')}==c['physicalClassHashes'][m] for m in modules)
assert all(sha(r/p)==h==sha(work/p) for p,h in c['inputHashes'].items())
assert not list(work.rglob('surefire-reports'))
(out/'raw-findings.json').open('x').write(json.dumps(raw,indent=2)+'\n')
m=dict(actualExit=0,sourceCore=c['sourceCore'],compile=dict(path=str(cp.relative_to(r)),sha256=sha(cp)),
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),stages=stages,
    inputHashes=c['inputHashes'],reports=reports,pmdRaw=len(raw),pmdErrors=errors,
    actualCompileClasspaths=declared,pmdClasspathFreshSiblingsFirst=True,
    toolAndSdkHashes={str(p):sha(p) for p in [*libs,*sorted(sdk)]},fullRootRuleset=sha(rule),
    productTestsExecuted=0,actualNativeDbVmServiceActions=0,heldClassfileActions=0,
    rawCollectionOnly=True,wholeF03Accepted=False,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(m,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,stageExits={k:v['actualExit'] for k,v in stages.items()},pmdRaw=len(raw),
    pmdErrors=len(errors),spotbugs={k:{x:(len(y) if x in ['classStats','projectClasspath'] else y) for x,y in v.items()} for k,v in reports.items()})))
