"""Independent same-source21 XML/exec/CRC, complete Batch645 and all physical input delta."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
import pg9346_direct_companion_jdk_post as steps
from pg11929_storage_fixture_class_metadata import parts as class_parts, selftest

SOURCE='fb1a22da2433c7909ceba05c7eeb07c879e52325'
NORMAL_SHA='a51e4812b19c20f1ef673b35278a9c4ef75e08100e785360033bbd5c1afdc5e0'
HOST_SHA='f8f5e46ed801d295b269f33e64e81881c6628af5ae4ba63cff692acb0978dfed'
STATIC_SHA='fb2fe41cab40003c4a052244dacd1d3036f48c0d6178066e4d576145ac08c812'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12560-monitoring-main-post-v3'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg12552-monitoring-main-host-v1'
OUT=data.BASE/'PG12560-monitoring-main-post-v3'


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12551-monitoring-main-six-compile-v2/manifest.json',NORMAL_SHA)
    h=data.read_checked(data.BASE/'PG12552-monitoring-main-host-v1/manifest.json',HOST_SHA)
    s=data.read_checked(data.BASE/'PG12554-monitoring-main-static-v1/manifest.json',STATIC_SHA)
    old=data.read_checked(data.BASE/'PG12528-public-record-six-compile-v1/manifest.json','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735')
    assert n['source']==h['source']==s['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==s['actualExit']==0
    assert h['observedTestExecutions']==21 and h['oldExecUnion'] is False and not h['whole451Accepted'] and h['newAccepted']==0
    assert all(x['actualExit']==0 and not x['timedOut'] for x in [*h['stages'],*s['stages'].values()])
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles']}.items())
    expected=Counter((x['className'],x['method']) for x in h['begin']['cases']);actual=[];xmls={}
    for f in (RUN/'xml').glob('TEST-*.xml'):
        root=ET.parse(f).getroot();assert all(root.get(k)=='0' for k in ['failures','errors','skipped'])
        actual.extend((r.get('classname'),r.get('name')) for r in root.findall('testcase'))
        assert all(not list(r) for r in root.findall('testcase'))
        xmls[f.name]=data.sha(f.read_bytes())
    assert len(xmls)==3 and len(actual)==21 and Counter(actual)==expected and xmls==h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text()=='found=21;started=21;succeeded=21;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes())==h['execSha256']
    loadedraw=(RUN/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==h['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()))
    prefixes=['dev.codex.schubert.nk.batch.monitoring.'+x for x in ['MetricContract','MonitoringModePolicy','MetricContractTest','MonitoringModePolicyTest','MonitoringRetentionConfigurationTest']]
    assert not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not any(x==p or x.startswith(p+'$') for p in prefixes)]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.'))]
    previous,current=jar_classes(old),jar_classes(n);assert set(previous)==set(current) and len(current)==1843
    changed={k for k in current if current[k]!=previous[k]}
    root='dev/codex/schubert/nk/batch/monitoring/'
    assert changed=={('batch',root+'MetricContract.class'),('batch',root+'MetricContract$Kind.class'),('batch',root+'MonitoringModePolicy.class')}
    metadata={}
    with zipfile.ZipFile(old['jars']['batch']['path']) as priorjar,zipfile.ZipFile(n['jars']['batch']['path']) as newjar:
        for _,entry in sorted(changed):
            before,after=class_parts(priorjar.read(entry),entry),class_parts(newjar.read(entry),entry)
            metadata[entry]=dict(rawCodeSame=before['rawCodeRepresentationSha256']==after['rawCodeRepresentationSha256'],debugSame=before['debugTablesSha256']==after['debugTablesSha256'],beforeRawCodeSha256=before['rawCodeRepresentationSha256'],rawCodeSha256=after['rawCodeRepresentationSha256'],beforeDebugSha256=before['debugTablesSha256'],debugSha256=after['debugTablesSha256'])
    assert metadata[root+'MetricContract$Kind.class']['rawCodeSame'] and not metadata[root+'MetricContract$Kind.class']['debugSame']
    classfile_vectors=selftest();assert classfile_vectors['positiveVectors']==3 and classfile_vectors['negativeVectors']==4
    assert test_classes(old)==test_classes(n) and len(test_classes(n))==1962
    for name,v in s['reports'].items():
        assert v['findings']==v['processingErrors']==0 and data.sha((data.BASE/'PG12554-monitoring-main-static-v1'/(name+'.xml')).read_bytes())==v['sha256']
    assert s['spotbugsSixExit']==0
    SLOT.mkdir();reader=SLOT/'reader';reader.mkdir();steps.SLOT=SLOT;tc=data.ROOT.parent/'toolchain'
    helper=data.ROOT/'tools/quality/architecture/MonitoringMainArtifactCoverageMeasure.java'
    libs=[tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[tc/f'm2/repository/org/ow2/asm/{x}/9.10.1/{x}-9.10.1.jar' for x in ['asm','asm-tree','asm-commons']]]
    tools={str(p):data.sha(p.read_bytes()) for p in [helper,*libs]};cp=os.pathsep.join(map(str,libs))
    stages=[steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    classes=SLOT/'complete-batch-main';classes.mkdir()
    with zipfile.ZipFile(n['jars']['batch']['path']) as jar:
        physical={name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')};assert len(physical)==645
        for name in physical:
            p=classes/name;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(jar.read(name))
    catalog=SLOT/'complete-main-catalog.txt'
    with catalog.open('x') as f:f.write(''.join(x+'\n' for x in sorted(physical)))
    stages.append(steps.step('measure-batch',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],'batch']))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'measure-batch.stdout').read_text().splitlines();assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1]=='FORBIDDEN_PROBE_HITS\t0'
    units={};packages=[];bundle=None;current=None
    for line in lines[2:]:
        parts=line.split('\t')
        if parts[0]=='PACKAGE_METADATA_ONLY':packages.append(parts[1]+'.class')
        elif parts[0]=='CLASS':
            name=parts[1]+'.class';assert name not in units
            current=dict(classCrc64=parts[2],counters={});units[name]=current
        elif parts[0]=='BUNDLE':
            assert parts==['BUNDLE','COMPLETE_BATCH_ARTIFACT'] and bundle is None
            bundle={};current=dict(counters=bundle)
        else:
            assert len(parts)==4 and parts[0]=='COUNTER' and parts[1] not in current['counters']
            current['counters'][parts[1]]=dict(missed=int(parts[2]),covered=int(parts[3]))
    assert set(units)|set(packages)==set(physical) and not set(units)&set(packages)
    targets=[root+x+'.class' for x in ['MetricContract','MetricContract$Kind','MonitoringModePolicy','MonitoringModePolicy$DetailService','MonitoringModePolicy$RetentionConfiguration']]
    assert set(targets)<=set(units)
    selected={p:units[p] for p in targets};totals={k:dict(missed=sum(v['counters'][k]['missed'] for v in selected.values()),covered=sum(v['counters'][k]['covered'] for v in selected.values())) for k in ['LINE','METHOD','CLASS','BRANCH']}
    assert all(sum(v['counters'][kind][key] for v in units.values())==bundle[kind][key] for kind in ['METHOD','CLASS','BRANCH'] for key in ['missed','covered'])
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(p).read_bytes())==digest for p,digest in tools.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    verify(invocation);OUT.mkdir()
    measurement=dict(source=SOURCE,session=h['sessionId'],units=units,packageMetadata=packages,completeBatchCounters=bundle,selectedFiveClasses=selected,selectedFiveCounters=totals,oldExecUnion=False,manualExclusionsAdded=False)
    data.write(OUT/'measurement.json',measurement)
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,originalHostManifestSha256=HOST_SHA,staticManifestSha256=STATIC_SHA,observedTestExecutions=21,suites=3,xmlHashes=xmls,execSha256=h['execSha256'],allMainPhysical=1843,changedMainPhysical=sorted(changed),otherMainUnchanged=1840,classfileMetadata=metadata,classfileMetadataVectors=classfile_vectors,allTestPhysicalUnchanged=1962,selectedFiveCounters=totals,completeBatchCounters=bundle,selectedFiveMissedZero=all(v['missed']==0 for v in totals.values()),completeBatchCoverage100=all(v['missed']==0 for v in bundle.values()),rawStatic=0,spotbugsSixExit=0,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),tools=tools,stages=stages,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,externalActions=0)
    data.write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=0,selectedFiveCounters=totals,completeBatchCounters=bundle,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__=='__main__':main()
