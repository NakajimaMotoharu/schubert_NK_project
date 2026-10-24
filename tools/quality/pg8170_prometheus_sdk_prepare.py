"""Isolated public compile/runtime SDK artifacts only; no target load, POM edit or M2 write."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
TC=Path('/home/mini/codex/project1/work/toolchain')
SLOT=Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8170-prometheus-sdk-prepare-v1')
TARGET=TC/'prometheus-sdk-1.17.1-client-1.7.0-new-v1'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8170-prometheus-sdk-prepare-v1'
IDS=('prometheus-metrics-core','prometheus-metrics-tracer-common','prometheus-metrics-exposition-formats',
     'prometheus-metrics-model','prometheus-metrics-config','prometheus-metrics-tracer-initializer',
     'prometheus-metrics-exposition-textformats','prometheus-metrics-tracer-otel','prometheus-metrics-tracer-otel-agent')
NEW=(('io.micrometer','micrometer-registry-prometheus','1.17.1'),)+tuple(('io.prometheus',a,'1.7.0') for a in IDS)
PINS={
 ('io.micrometer','micrometer-core','1.17.1'):'9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56',
 ('io.micrometer','micrometer-commons','1.17.1'):'f2cee6ef046e72eec8128474c7f58c6217173b45ae373c30de0289f2a56ab0fd',
 ('io.micrometer','micrometer-observation','1.17.1'):'eb34f0cd84a879393ae5c21160fc06385ccdc74f36a4d1e31b199f59acfdaf71',
 ('org.hdrhistogram','HdrHistogram','2.2.2'):'22d1d4316c4ec13a68b559e98c8256d69071593731da96136640f864fa14fad8',
 ('org.jspecify','jspecify','1.0.1'):'070d75f261fe4c5b8202508366715f7f2d4660f88c8ef7e6d3575e48c9683b66'}
NS={'m':'http://maven.apache.org/POM/4.0.0'}


def digest(path,algorithm='sha256'):
    h=hashlib.new(algorithm)
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def write(path,value):
    with path.open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def rel(coordinate):
    group,artifact,version=coordinate
    return group.replace('.','/')+'/'+artifact+'/'+version+'/'+artifact+'-'+version


def fetch(url,path,limit):
    command=['/usr/bin/curl','--fail','--silent','--show-error','--proto','=https',
             '--max-time','60','--max-filesize',str(limit),url]
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    record_name=path.name+'.download.safe.json'
    with path.open('xb') as f:
        child=subprocess.Popen(command,cwd=SLOT,stdout=f,stderr=subprocess.PIPE,
                               stdin=subprocess.DEVNULL,close_fds=True)
        write(SLOT/(path.name+'.process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=command))
        _,stderr=child.communicate(timeout=70)
        f.flush()
        os.fsync(f.fileno())
    record=dict(command=command,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                actualExit=child.returncode,stderr=stderr.decode('utf-8','replace'),bytes=path.stat().st_size,
                sha256=digest(path))
    write(SLOT/record_name,record)
    if child.returncode!=0:
        raise ValueError('public artifact retrieval failed; preserve original and never switch route automatically')
    return record


def checked_file(coordinate,suffix):
    base=coordinate[1]+'-'+coordinate[2]+suffix
    file=TARGET/base
    url='https://repo.maven.apache.org/maven2/'+rel(coordinate)+suffix
    record=fetch(url,file,32*1024*1024 if suffix=='.jar' else 1024*1024)
    checksum_file=TARGET/(base+'.sha1')
    checksum=fetch(url+'.sha1',checksum_file,1024)
    expected=checksum_file.read_text().strip().lower()
    if re.fullmatch('[a-f0-9]{40}',expected) is None or digest(file,'sha1')!=expected:
        raise ValueError('actual published checksum mismatch; no extraction or class execution')
    return dict(path=str(file),url=url,sha256=digest(file),repositorySha1=expected,
                checksumPath=str(checksum_file),checksumSha256=checksum['sha256'],
                bytes=record['bytes'],downloadActualExit=0)


def pom_dependencies(coordinate,file):
    data=file.read_bytes()
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise ValueError('public dependency POM must not contain DTD/entities')
    doc=ET.fromstring(data)
    if doc.tag!='{'+NS['m']+'}project':
        raise ValueError('exact Maven POM namespace')
    group=doc.findtext('m:groupId',namespaces=NS) or doc.findtext('m:parent/m:groupId',namespaces=NS)
    version=doc.findtext('m:version',namespaces=NS) or doc.findtext('m:parent/m:version',namespaces=NS)
    artifact=doc.findtext('m:artifactId',namespaces=NS)
    if (group,artifact,version)!=coordinate:
        raise ValueError('declared official coordinate/version must match actual POM')
    included,excluded=[],[]
    for dep in doc.findall('m:dependencies/m:dependency',NS):
        item={k:dep.findtext('m:'+k,namespaces=NS) for k in ('groupId','artifactId','version','scope','optional')}
        scope=item['scope'] or 'compile'
        if scope in ('test','provided') or item['optional']=='true':
            excluded.append(dict(**item,reason='MAVEN_NON_TRANSITIVE_RUNTIME_'+scope+('_OPTIONAL' if item['optional']=='true' else '')))
            continue
        if scope not in ('compile','runtime') or item['optional'] not in (None,'false'):
            raise ValueError('unknown dependency semantics, never inferred as resolved')
        actual_version=version if item['version']=='$'+'{project.version}' else item['version']
        actual=(item['groupId'],item['artifactId'],actual_version)
        if actual not in NEW and actual not in PINS:
            raise ValueError('runtime dependency outside reviewed closed coordinate set')
        included.append(dict(coordinate=list(actual),scope=scope))
    # Do not silently reinterpret active profile dependencies as direct effective dependencies.
    active=[p for p in doc.findall('m:profiles/m:profile',NS)
            if p.findtext('m:activation/m:activeByDefault',namespaces=NS)=='true'
            and p.findall('m:dependencies/m:dependency',NS)]
    if active:
        raise ValueError('active profile dependency needs explicit review before closure claim')
    return included,excluded


def zip_metadata(file):
    with zipfile.ZipFile(file) as jar:
        entries=jar.infolist()
        if sum(e.file_size for e in entries)>256*1024*1024 or len(entries)>20000 or jar.testzip() is not None:
            raise ValueError('bounded verified Jar integrity')
        classes=[e.filename for e in entries if e.filename.endswith('.class')]
        if len(classes)!=len(set(classes)) or any(n.startswith('/') or '..' in n.split('/') for n in classes):
            raise ValueError('unambiguous class path metadata only')
        return dict(classFiles=len(classes),entries=len(entries),targetLoaded=False,targetInitialized=False)


def main():
    invocation=capture(Path(__file__))
    if SLOT.exists() or TARGET.exists() or OUT.exists():
        raise ValueError('new-only toolchain preparation; recover existing actual receipts instead of replay')
    reused={}
    for coordinate,expected in PINS.items():
        file=TC/'m2/repository'/(rel(coordinate)+'.jar')
        if not file.is_file() or file.is_symlink() or digest(file)!=expected:
            raise ValueError('all five original existing dependency pins unchanged')
        reused[':'.join(coordinate)]=dict(path=str(file),sha256=expected,existing=True)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    os.umask(0o077)
    SLOT.mkdir(mode=0o700)
    TARGET.mkdir(mode=0o700)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(SLOT/'begin.safe.json',dict(source=source,invocation=invocation,pid=os.getpid(),startUTC=start,
                                    reviewedCoordinates=[list(c) for c in NEW],existingPins=reused))
    downloaded={}
    graph={}
    excluded={}
    for coordinate in NEW:
        pom=checked_file(coordinate,'.pom')
        included,non_runtime=pom_dependencies(coordinate,Path(pom['path']))
        jar=checked_file(coordinate,'.jar')
        key=':'.join(coordinate)
        downloaded[key]=dict(pom=pom,jar=jar,jarMetadata=zip_metadata(Path(jar['path'])))
        graph[key]=included
        excluded[key]=non_runtime
    reachable={NEW[0]}
    while True:
        extra={tuple(item['coordinate']) for c in reachable if ':'.join(c) in graph
               for item in graph[':'.join(c)] if tuple(item['coordinate']) in NEW}
        combined=reachable|extra
        if combined==reachable:
            break
        reachable=combined
    if reachable!=set(NEW):
        raise ValueError('no unused or unconnected artifact may silently enter runtime bundle')
    if any(digest(Path(row['path']))!=row['sha256'] for row in reused.values()):
        raise ValueError('existing toolchain bytes changed during own preparation')
    verify(invocation)
    value=dict(actualExit=0,source=source,invocation=invocation,startUTC=start,
        endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),newJarCount=10,existingJarCount=5,
        downloaded=downloaded,reused=reused,directCompileRuntimeGraph=graph,nonRuntimeDependencies=excluded,
        closureScope='REVIEWED_PUBLISHED_DIRECT_COMPILE_RUNTIME_GRAPH_WITH_FIVE_PREQUALIFIED_TERMINAL_PINS',
        generalEffectivePomClaim=False,publicArtifactDownloads=40,repository='https://repo.maven.apache.org/maven2/',
        repositorySha1Verified=True,computedSha256Pinned=True,vendorSignatureVerified=False,
        existingM2Writes=0,productionPomChanges=0,targetClassLoaded=False,targetClassInitialized=False,
        actualVmActions=0,actualDatabaseActions=0,actualDaemonActions=0,targetNetworkActions=0,
        productTestsExecuted=0,formalUpdated=False,newAccepted=0,effortPercent=None,
        original4222Replayed=False,whole451Accepted=False)
    write(SLOT/'manifest.safe.json',value)
    OUT.mkdir()
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,newJars=10,reusedJars=5,manifestSha256=digest(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
