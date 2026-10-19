"""Historical296 analysis versus failed0ea only on byte-identical classes; no result union."""
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
from pg5700_failed_native_diagnostic import ROOT,W,MODULES

SLOT='pg5704-historical-failure-comparison-v1'


def resolve_roles(manifest,hashes):
    if set(hashes)!=set(MODULES):raise ValueError('every actual old module hash')
    prefixes={'protocol':'api/lib/','storage':'api/lib/','bootstrap':'api/lib/','api':'api/','web':'web/','batch':'operations/'}
    result={}
    for module in MODULES:
        matches=[r['path']for r in manifest['artifacts']if r['sha256']==hashes[module]and r['path'].startswith(prefixes[module])and r['path'].endswith('.jar')]
        if len(matches)!=1:raise ValueError('one canonical signed BOM role/hash, never guessed filename')
        path=PurePosixPath(matches[0])
        if path.is_absolute()or'..'in path.parts or str(path)!=matches[0]:raise ValueError('signed role path cannot escape')
        result[module]=matches[0]
    return result


def parse(path):
    lines={}
    for raw in path.read_text().splitlines():
        a=raw.split('\t')
        if a[0]=='LINE':lines[(a[1],int(a[2]))]=tuple(map(int,a[3:]))
    return lines


def main():
    old_execs=[p for p in(W/'pg5510-current-native-qualified-v1').glob('*.exec')if hashlib.sha256(p.read_bytes()).hexdigest()=='14dcd6c8f1567a0cfffa4987bfe1bc13feda1f446ba55582ce298a4ab8709c51']
    if len(old_execs)!=1:raise ValueError('one original historical successful parent point, not current source')
    old=json.loads((W/'pg5416-ownership-whole-qualified-v2/manifest.safe.json').read_bytes())['result']
    current=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5588-current3905-cases/qualification.json').read_bytes())
    release=W/'pg5430-release-v1';bom=(release/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(bom).hexdigest()!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('original signed old187 manifest')
    paths=resolve_roles(json.loads(bom),old['jarHashes'])
    jars=[release/paths[m]for m in MODULES]
    if old['productionSource']!='29612b2a484a5ab7418e02a491c4360af7444626'or any(p.is_symlink()or not p.resolve(strict=True).is_relative_to(release)or hashlib.sha256(p.read_bytes()).hexdigest()!=old['jarHashes'][m]for m,p in zip(MODULES,jars)):raise ValueError('actual old1664 Jar bytes remain old source')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    proof=json.loads((W/'pg5700-failed-native-diagnostic-v2/manifest.safe.json').read_bytes());libs=[Path(p)for p in proof['libraryHashes']]
    if any(hashlib.sha256(p.read_bytes()).hexdigest()!=proof['libraryHashes'][str(p)]for p in libs):raise ValueError('fixed analysis library bytes')
    classes=W/'pg5702-expanded-failed-native-v1/classes';jdk=ROOT.parent/'toolchain/jdk-25.0.4/bin';cp=os.pathsep.join(map(str,[classes,*libs]))
    command=[str(jdk/'java'),'-Xmx512m','-cp',cp,'FailedRootCoverageDiagnostic',str(old_execs[0]),*map(str,jars),'ALL_SOURCE']
    env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    with(out/'historical-only.private.log').open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=90)
    if r.returncode:raise ValueError('old bytes must match old point; never auto-rebind')
    before=parse(out/'historical-only.private.log');after=parse(W/'pg5702-expanded-failed-native-v1/phase-1.private.log');changes=[];changed_source=[]
    for key,a in after.items():
        cls,line=key;module=cls.split('/')[4];physical=module+':'+cls+'.class'
        if old['allPhysicalMainSha256'].get(physical)!=current['allPhysicalMainSha256'].get(physical):
            changed_source.append(physical);continue
        b=before.get(key)
        if b is not None and a[2]>b[2]and cls.endswith(('RootStartupContext','MorningServiceReadiness','MorningParentBudget','MorningStartupLaunchOwner')):
            file=ROOT/('src/schubert-nk-'+module+'/src/main/java')/(cls.split('$')[0]+'.java');source=file.read_text().splitlines()[line-1].strip()
            changes.append({'class':cls,'line':line,'source':source,'historical':b,'currentFailed':a})
    value={'actualExit':0,'historicalSource':old['productionSource'],'currentFailedSource':current['productionSource'],
      'historicalPointSha256':'14dcd6c8f1567a0cfffa4987bfe1bc13feda1f446ba55582ce298a4ab8709c51',
      'failedPointSha256':proof['nativeSha256'],'oldSignedBomRoles':paths,'allSixOriginalJarHashesVerified':True,'sameByteBranchDifferences':changes,'differentByteClassesNotComparable':sorted(set(changed_source)),
      'oldSuccessfulResultImported':False,'coverageUnionPerformed':False,'vmOperations':0,'normalNativeQualified':False,'wholeMorningAccepted':False,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sameByteBranchDifferences':changes,'currentRunStillFailed':True,'coverageUnionPerformed':False}))


if __name__=='__main__':main()
