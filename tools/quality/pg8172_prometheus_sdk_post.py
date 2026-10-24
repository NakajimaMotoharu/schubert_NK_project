"""Independent SDK bytes/graph/class-name audit; never target load, collector or Java execution."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import zipfile
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW=BASE/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
OUT=BASE/'PG8172-prometheus-sdk-post-v1'
RAW_SHA='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'


def sha(file,kind='sha256'):
    h=hashlib.new(kind)
    with file.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def require(value):
    if not value:
        raise ValueError('exact declared isolated dependency graph and honest scope required')


def assess(raw):
    require(raw['actualExit']==0 and raw['source']=='69204dd13'+raw['source'][9:] and len(raw['source'])==40)
    require(raw['newJarCount']==len(raw['downloaded'])==10 and raw['existingJarCount']==len(raw['reused'])==5)
    require(raw['existingM2Writes']==raw['productionPomChanges']==raw['productTestsExecuted']==0)
    require(raw['targetClassLoaded'] is False and raw['targetClassInitialized'] is False)
    require(raw['vendorSignatureVerified'] is False and raw['generalEffectivePomClaim'] is False)
    require(raw['formalUpdated'] is False and raw['newAccepted']==0 and raw['effortPercent'] is None)
    require(raw['repository']=='https://repo.maven.apache.org/maven2/')
    keys=set(raw['downloaded'])|set(raw['reused'])
    require(set(raw['directCompileRuntimeGraph'])==set(raw['downloaded']))
    for dependencies in raw['directCompileRuntimeGraph'].values():
        require(all(':'.join(item['coordinate']) in keys and item['scope'] in ('compile','runtime') for item in dependencies))


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists() and sha(RAW)==RAW_SHA)
    raw=json.loads(RAW.read_bytes())
    assess(raw)
    jars=[]
    for row in raw['downloaded'].values():
        for kind in ('pom','jar'):
            item=row[kind]
            file=Path(item['path'])
            require(file.is_file() and not file.is_symlink() and sha(file)==item['sha256'])
            require(sha(file,'sha1')==item['repositorySha1'])
            require(sha(Path(item['checksumPath']))==item['checksumSha256'])
        jars.append(Path(row['jar']['path']))
    for row in raw['reused'].values():
        file=Path(row['path'])
        require(file.is_file() and not file.is_symlink() and sha(file)==row['sha256'])
        jars.append(file)
    names={}
    modules=[]
    for jar in jars:
        with zipfile.ZipFile(jar) as archive:
            for name in archive.namelist():
                if not name.endswith('.class'):
                    continue
                if name.endswith('module-info.class'):
                    modules.append(dict(jar=str(jar),entry=name,role='LIBRARY_MODULE_DESCRIPTOR_NOT_PRODUCTION_COUNTER_EXCLUSION'))
                    continue
                require(name not in names)
                names[name]=str(jar)
    require(len(names)==1824 and sum(j.stat().st_size for j in jars)==3688470)
    rejected=[]
    for name,change in (
        ('count-inflation',lambda x:x.update(newJarCount=11)),
        ('class-initialized',lambda x:x.update(targetClassInitialized=True)),
        ('m2-write-hidden',lambda x:x.update(existingM2Writes=1)),
        ('unresolved-runtime',lambda x:next(iter(x['directCompileRuntimeGraph'].values())).append(
            dict(coordinate=['not.reviewed','unknown','1'],scope='runtime'))),
        ('vendor-signature-inferred',lambda x:x.update(vendorSignatureVerified=True)),
        ('formal-inflation',lambda x:x.update(formalUpdated=True))):
        candidate=copy.deepcopy(raw)
        change(candidate)
        try:
            assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('metadata mutation must not qualify')
    verify(invocation)
    value=dict(actualExit=0,source=raw['source'],invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalManifestSha256=RAW_SHA,
        newJarCount=10,existingJarCount=5,totalJarBytes=3688470,distinctPhysicalClassNames=1824,
        duplicatePhysicalClassNames=0,libraryModuleMetadata=modules,negativeReceiptGuards=rejected,
        originalRepositoryChecksumsAndAllBytesVerified=True,targetClassLoaded=False,
        targetClassInitialized=False,javaJobsIssued=0,downloadJobsIssued=0,
        actualVmActions=0,actualDatabaseActions=0,actualDaemonActions=0,targetNetworkActions=0,
        productTestsExecuted=0,formalUpdated=False,newAccepted=0,effortPercent=None,whole451Accepted=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')
    print(json.dumps(dict(actualExit=0,jarCount=15,classes=1824,negativeGuards=len(rejected),
                         manifestSha256=sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
