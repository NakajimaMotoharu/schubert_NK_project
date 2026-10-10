"""Read-only D5 current ten+six host coordinates; no native capture or exclusions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
R=Path(__file__).resolve().parent
SOURCE='d5b00104280028d9ea81b44c1d1c805f3c2861ed'
NATIVE_SHA='9dffc95124120b63299467f4066aeea306b0cc35a38012fee66a2e090cdb04db'
HOST_SHA='c94cf95cddaef9fae4d3db02d3a732ee17a5ffdcc700714b14b4694fb077aab1'
COUNTERS=('LINE','METHOD','CLASS','BRANCH')


def require(value):
    if not value:raise ValueError('fixed current same-byte gap proof refused')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def coordinates(raw, expected):
    require(type(raw)is bytes and type(expected)is dict)
    root=ET.fromstring(raw);require(root.tag=='report')
    counter={n.attrib['type']:{'missed':int(n.attrib['missed']),'covered':int(n.attrib['covered'])}for n in root.findall('counter')}
    require(all(counter[k]==expected[k]for k in COUNTERS))
    families=[]
    for package in root.findall('package'):
        for cls in package.findall('class'):
            missed={n.attrib['type']:int(n.attrib['missed'])for n in cls.findall('counter')}
            if not any(missed.get(k,0)for k in COUNTERS):continue
            methods=[]
            for method in cls.findall('method'):
                mc={n.attrib['type']:int(n.attrib['missed'])for n in method.findall('counter')}
                if any(mc.get(k,0)for k in ('LINE','METHOD','BRANCH')):methods.append(dict(method.attrib,missed=mc))
            source=cls.attrib.get('sourcefilename')
            lines=[]
            for sf in package.findall('sourcefile'):
                if sf.attrib['name']==source:
                    lines=[{k:int(v)for k,v in n.attrib.items()}for n in sf.findall('line')if int(n.attrib['mi'])>0 or int(n.attrib['mb'])>0]
            families.append({'class':cls.attrib['name'],'source':source,'missed':missed,'methods':methods,'sourceFileMissedLines':lines})
    return families


def main():
    os.umask(0o077)
    require(not subprocess.check_output(['git','status','--porcelain']))
    require(not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']))
    cohort=W/'pg1258-fresh-ten-native-v1';host=W/'pg1018-stream-six-host-v2'
    require(sha(cohort/'manifest.safe.json')==NATIVE_SHA and sha(host/'manifest.safe.json')==HOST_SHA)
    record=json.loads((cohort/'manifest.safe.json').read_bytes());h=json.loads((host/'manifest.safe.json').read_bytes())
    require(record['actualExit']==0 and record['productionSource']==SOURCE and record['qualifiedCurrentNativeSubcampaign']is True and record['currentNativeStreams']==10 and h['candidateSource']==SOURCE and h['actualExit']==0)
    modules=('protocol','storage','bootstrap','api','web','batch');data=[]
    for module in modules:
        p=host/module/'jacoco.exec';require(sha(p)==record['hostExecHashes'][module]==h['moduleResults'][module]['execSha256']);data.append(p)
    require(len(record['selected'])==10)
    for i,v in enumerate(record['selected']):
        p=cohort/(str(i)+'.exec');require(p.stat().st_size==v['bytes']and sha(p)==v['sha256']);data.append(p)
    require(len(data)==16)
    target=W/'pg1271-current-native-gap-v1';require(not os.path.lexists(target))
    capacity=os.statvfs(W);require(capacity.f_bavail*capacity.f_frsize>=268435456+536870912)
    target.mkdir(mode=0o700);classes=target/'classes';classes.mkdir(mode=0o700)
    cp=[];repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths=list(repo.glob(pattern));require(len(paths)==1);cp.append(str(paths[0]))
    build=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(classes),str(R/'NativeCoverageXml471.java')],capture_output=True,timeout=30)
    require(build.returncode==0 and not build.stdout and not build.stderr)
    cp.insert(0,str(classes));gaps={};xml_hashes={};start=datetime.datetime.now(datetime.timezone.utc)
    for module in ('bootstrap','api','batch'):
        jar=host/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');require(sha(jar)==h['moduleResults'][module]['jarSha256'])
        xml=target/(module+'.xml')
        result=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverageXml471',str(jar),str(xml),*[str(p)for p in data]],capture_output=True,timeout=45)
        with(target/(module+'.private.log')).open('xb')as f:f.write(result.stdout);f.write(result.stderr);f.flush();os.fsync(f.fileno())
        require(result.returncode==0 and not result.stderr and b'classMismatch0=true'in result.stdout)
        raw=xml.read_bytes();gaps[module]=coordinates(raw,record['moduleCounters'][module]);xml_hashes[module]=sha(xml)
    safe={'actualExit':0,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parentManifestSha256':NATIVE_SHA,'hostManifestSha256':HOST_SHA,'hostExecCount':6,'currentNativeExecCount':10,'oldNativeImports0':True,'xmlHashes':xml_hashes,'gaps':gaps,'moduleCounters':record['moduleCounters'],'coverage100':False,'formalAccepted':False,'exclusions0':True,'sourceChanged0':True,'newVmOperations0':True}
    with(target/'gap.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'gapFamilies':{k:len(v)for k,v in gaps.items()},'missedMethods':{k:sum(len(x['methods'])for x in v)for k,v in gaps.items()},'gapSha256':sha(target/'gap.safe.json'),'formalAccepted':False,'newVmOperations0':True}))
    return 0


if __name__=='__main__':raise SystemExit(main())
