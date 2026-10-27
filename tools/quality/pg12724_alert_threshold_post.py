"""Independent original14 XML/CRC and complete Batch645/physical source-bound artifacts; no replay."""
from collections import Counter
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts as class_parts, selftest
import pg9346_direct_companion_jdk_post as steps

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
NORMAL_SHA='5433fb79732be52686b99e8ec665a0ebb02752a90004cc777eedb3b4d31ba1c7'
HOST_SHA='ccb4a097f17f8e40779ca3f01f3ab79a876f0c33eccb94d27c31f54661562513'
STATIC_SHA='2cd61dcada2767e9c62b6e580d0e5e2215758471408d6e69833e9d6452996707'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12724-alert-threshold-post-v1'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg12720-alert-threshold-host-v1'
OUT=data.BASE/'PG12724-alert-threshold-post-v1'


def main():
    invocation=capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12718-alert-threshold-six-compile-v1/manifest.json',NORMAL_SHA)
    h=data.read_checked(data.BASE/'PG12720-alert-threshold-host-v1/manifest.json',HOST_SHA)
    s=data.read_checked(data.BASE/'PG12722-alert-threshold-static-v1/manifest.json',STATIC_SHA)
    old=data.read_checked(data.BASE/'PG12686-scenario-writer-six-compile-v1/manifest.json','20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d')
    assert n['source']==h['source']==s['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==0 and s['actualExit']==1
    assert h['observedTestExecutions']==14 and not h['oldExecUnion'] and all(r['actualExit']==0 and not r['timedOut'] for r in h['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles']}.items())
    actual=[];xmls={}
    for path in (RUN/'xml').glob('TEST-*.xml'):
        node=ET.parse(path).getroot()
        assert all(node.get(k)=='0' for k in ['failures','errors','skipped']) and all(not list(row) for row in node.findall('testcase'))
        actual.extend((row.get('classname'),row.get('name')) for row in node.findall('testcase'))
        xmls[path.name]=data.sha(path.read_bytes())
    assert len(xmls)==1 and len(actual)==14 and Counter(actual)==Counter((row['className'],row['method']) for row in h['begin']['cases']) and xmls==h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text()=='found=14;started=14;succeeded=14;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes())==h['execSha256']
    loadedraw=(RUN/'classload-metadata.log').read_bytes()
    assert data.sha(loadedraw)==h['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()))
    roots=['dev.codex.schubert.nk.batch.monitoring.'+name for name in ['AlertThresholds','AlertLifecycle','AlertThresholdsTest']]
    assert not [name for name in loaded if name.startswith('dev.codex.schubert.nk.') and not any(name==root or name.startswith(root+'$') for root in roots)]
    assert not [name for name in loaded if name.startswith(('org.postgresql.','org.apache.activemq.'))]
    previous,current=jar_classes(old),jar_classes(n)
    assert set(previous)==set(current) and len(current)==1843
    main_changed={key for key in current if current[key]!=previous[key]}
    root='dev/codex/schubert/nk/batch/monitoring/'
    assert main_changed=={('batch',root+'AlertThresholds.class')}
    before_tests,after_tests=test_classes(old),test_classes(n)
    assert set(before_tests)==set(after_tests) and len(after_tests)==1962
    test_changed={key for key in after_tests if before_tests[key]!=after_tests[key]}
    assert test_changed=={('batch',root+'AlertThresholdsTest.class')}
    models={}
    for role,entry in [*main_changed,*test_changed]:
        is_test=entry.endswith('Test.class')
        def content(normal):
            if is_test:
                return (Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes()
            with zipfile.ZipFile(normal['jars'][role]['path']) as jar:
                return jar.read(entry)
        a,b=[class_parts(content(normal),entry) for normal in [old,n]]
        assert a['model']['sourceFile']==b['model']['sourceFile']==entry.rpartition('/')[2].replace('.class','.java')
        models[entry]=dict(sourceFile=b['model']['sourceFile'],rawCodeSame=a['rawCodeRepresentationSha256']==b['rawCodeRepresentationSha256'],debugSame=a['debugTablesSha256']==b['debugTablesSha256'])
    metadata_vectors=selftest()
    for label,row in s['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(4 if label=='pmd' else 0)
        assert data.sha((data.BASE/'PG12722-alert-threshold-static-v1'/(label+'.xml')).read_bytes())==row['sha256']
    warnings=[row for row in ET.parse(data.BASE/'PG12722-alert-threshold-static-v1/pmd.xml').getroot().iter() if row.tag.rpartition('}')[2]=='violation']
    assert len(warnings)==4 and all(row.get('rule')=='DoNotUseThreads' for row in warnings)
    assert s['spotbugsSixExit']==0 and all(row['actualExit']==(4 if key=='pmd' else 0) and not row['timedOut'] for key,row in s['stages'].items())
    SLOT.mkdir();reader=SLOT/'reader';reader.mkdir();steps.SLOT=SLOT;tc=data.ROOT.parent/'toolchain'
    helper=data.ROOT/'tools/quality/architecture/AlertThresholdArtifactCoverageMeasure.java'
    libraries=[tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[tc/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ['asm','asm-tree','asm-commons']]]
    toolhashes={str(path):data.sha(path.read_bytes()) for path in [helper,*libraries]}
    cp=os.pathsep.join(map(str,libraries))
    stages=[steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    classes=SLOT/'complete-batch-main';classes.mkdir()
    with zipfile.ZipFile(n['jars']['batch']['path']) as jar:
        physical={name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')}
        assert len(physical)==645
        for name in physical:
            target=classes/name;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                stream.write(jar.read(name))
    catalog=SLOT/'complete-main-catalog.txt'
    with catalog.open('x') as stream:
        stream.write(''.join(name+'\n' for name in sorted(physical)))
    stages.append(steps.step('measure-batch',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],'batch']))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'measure-batch.stdout').read_text().splitlines()
    assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1]=='FORBIDDEN_PROBE_HITS\t0'
    units={};packages=[];bundle=None;cursor=None
    for line in lines[2:]:
        fields=line.split('\t')
        if fields[0]=='PACKAGE_METADATA_ONLY':
            packages.append(fields[1]+'.class')
        elif fields[0]=='CLASS':
            name=fields[1]+'.class';assert name not in units
            cursor=dict(classCrc64=fields[2],counters={});units[name]=cursor
        elif fields[0]=='BUNDLE':
            assert fields==['BUNDLE','COMPLETE_BATCH_ARTIFACT'] and bundle is None
            bundle={};cursor=dict(counters=bundle)
        else:
            assert len(fields)==4 and fields[0]=='COUNTER' and fields[1] not in cursor['counters']
            cursor['counters'][fields[1]]=dict(missed=int(fields[2]),covered=int(fields[3]))
    assert set(units)|set(packages)==set(physical) and not set(units)&set(packages)
    target=units[root+'AlertThresholds.class']
    assert all(row['missed']==0 for row in target['counters'].values())
    # Only the Severity enum is used; no outer lifecycle state-machine execution is claimed.
    lifecycle=units[root+'AlertLifecycle.class']
    assert all(row['covered']==0 for row in lifecycle['counters'].values())
    assert all(sum(row['counters'][kind][key] for row in units.values())==bundle[kind][key] for kind in ['METHOD','CLASS','BRANCH'] for key in ['missed','covered'])
    assert not list(Path(h['begin']['testCwd']).iterdir())
    assert all(data.sha(Path(path).read_bytes())==digest for path,digest in toolhashes.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],units=units,packageMetadata=packages,completeBatchCounters=bundle,thresholdMain=target,lifecycleOuter=lifecycle,oldExecUnion=False,manualExclusionsAdded=False))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,originalHostManifestSha256=HOST_SHA,staticManifestSha256=STATIC_SHA,observedTestExecutions=14,suites=1,xmlHashes=xmls,execSha256=h['execSha256'],allMainPhysical=1843,changedMainPhysical=sorted(main_changed),otherMainUnchanged=1842,allTestPhysical=1962,changedTestPhysical=sorted(test_changed),otherTestsUnchanged=1961,physicalCodeDebug=models,metadataVectors=metadata_vectors,thresholdMainCounters=target['counters'],completeBatchCounters=bundle,completeBatchCoverage100=False,rawStatic=4,spotbugsSixExit=0,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),toolHashes=toolhashes,stages=stages,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,externalActions=0))
    print(dict(actualExit=0,thresholdMainCounters=target['counters'],completeBatchCounters=bundle,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()
