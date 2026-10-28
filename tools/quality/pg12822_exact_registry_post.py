"""Independent same-source whole10 XML, complete six artifacts and unchanged Main, no PT replay."""
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

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
NORMAL_SHA='8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89'
HOST_SHA='867b79efaed54d92217ba9ef57f40365886022531735e6c37f6f5d727a869721'
STATIC_SHA='90c12edb90d3380de96ab28d71ac28d3445500890a49627be852eee106dd136b'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12822-exact-registry-post-v1'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg12818-exact-registry-host-v1'
OUT=data.BASE/'PG12822-exact-registry-post-v1'
COUNTS={'api':467,'web':358,'batch':645,'protocol':176,'storage':80,'bootstrap':117}


def main():
    invocation=capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12819-exact-registry-six-compile-v2/manifest.json',NORMAL_SHA)
    h=data.read_checked(data.BASE/'PG12818-exact-registry-host-v1/manifest.json',HOST_SHA)
    s=data.read_checked(data.BASE/'PG12820-exact-registry-static-v1/manifest.json',STATIC_SHA)
    old=data.read_checked(data.BASE/'PG12792-api-policy-six-compile-v1/manifest.json','c1b8967f460264fae3194e799ed8f486711472c36b142ad28f0ae05dfd978d85')
    plan=data.read_checked(data.BASE/'PG12817-exact-registry-plan-v3/manifest.json','88a9d3eebc46f473fdc492e5ecdd8806b380aae78701312631019e40eb41e978')
    assert n['source']==h['source']==s['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==0 and s['actualExit']==1
    assert h['observedTestExecutions']==10 and not h['oldExecUnion'] and all(row['actualExit']==0 and not row['timedOut'] for row in h['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles']}.items())
    assert all(n['begin']['inputHashes'][p]==digest for p,digest in plan['eligibilityClosureSourceHashes'].items())
    actual=[];xmls={}
    for path in (RUN/'xml').glob('TEST-*.xml'):
        node=ET.parse(path).getroot()
        assert all(node.get(key)=='0' for key in ['failures','errors','skipped']) and all(not list(row) for row in node.findall('testcase'))
        actual.extend((row.get('classname'),row.get('name')) for row in node.findall('testcase'))
        xmls[path.name]=data.sha(path.read_bytes())
    assert len(xmls)==1 and len(actual)==10 and Counter(actual)==Counter((row['className'],row['method']) for row in h['begin']['cases']) and xmls==h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text()=='found=10;started=10;succeeded=10;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes())==h['execSha256']
    loadedraw=(RUN/'classload-metadata.log').read_bytes()
    assert data.sha(loadedraw)==h['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()))
    roots={path.split('/java/',1)[1][:-5].replace('/','.') for path in plan['eligibilityClosureSourceHashes']}|{row['className'] for row in h['begin']['cases']}
    assert len(roots)==27
    assert not [name for name in loaded if name.startswith('dev.codex.schubert.nk.') and not any(name==root or name.startswith(root+'$') for root in roots)]
    assert not [name for name in loaded if name.startswith(('org.postgresql.','org.apache.activemq.'))]
    assert jar_classes(old)==jar_classes(n) and len(jar_classes(n))==1843
    a,b=test_classes(old),test_classes(n)
    assert set(a)==set(b) and len(b)==1962
    changed={key for key in b if a[key]!=b[key]}
    scope={row['path'].split('/java/',1)[1][:-5]:(row['path'],row['path'].split('schubert-nk-',1)[1].split('/',1)[0]) for row in plan['sourceChanges']}
    physical_scope={key for key in b if any(key[0]==role and (key[1]==name+'.class' or key[1].startswith(name+'$')) for name,(_,role) in scope.items())}
    assert changed and changed<=physical_scope
    models={}
    for role,entry in sorted(changed):
        before=class_parts((Path(old['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        after=class_parts((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        name=entry.split('$',1)[0].removesuffix('.class')
        assert name in scope and role==scope[name][1] and before['model']['sourceFile']==after['model']['sourceFile']==Path(scope[name][0]).name
        models[role+':'+entry]=dict(sourceFile=after['model']['sourceFile'],beforeSha256=a[(role,entry)],sha256=b[(role,entry)],rawCodeSame=before['rawCodeRepresentationSha256']==after['rawCodeRepresentationSha256'],debugSame=before['debugTablesSha256']==after['debugTablesSha256'])
    assert {row['sourceFile'] for row in models.values()}=={Path(path).name for path,_ in scope.values()}
    metadata_vectors=selftest()
    for label,row in s['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(3 if label=='pmd' else 0)
        assert data.sha((data.BASE/'PG12820-exact-registry-static-v1'/(label+'.xml')).read_bytes())==row['sha256']
    warnings=[row for row in ET.parse(data.BASE/'PG12820-exact-registry-static-v1/pmd.xml').getroot().iter() if row.tag.rpartition('}')[2]=='violation']
    assert len(warnings)==3 and Counter(row.get('rule') for row in warnings)==Counter(AvoidSynchronizedStatement=2,DoNotUseThreads=1)
    assert s['spotbugsSixExit']==0 and all(row['actualExit']==0 and not row['timedOut'] for key,row in s['stages'].items() if key!='pmd')
    SLOT.mkdir();reader=SLOT/'reader';reader.mkdir();steps.SLOT=SLOT;tc=data.ROOT.parent/'toolchain'
    helper=data.ROOT/'tools/quality/architecture/ExactRegistryArtifactCoverageMeasure.java'
    libraries=[tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[tc/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ['asm','asm-tree','asm-commons']]]
    toolhashes={str(path):data.sha(path.read_bytes()) for path in [helper,*libraries]}
    cp=os.pathsep.join(map(str,libraries))
    stages=[steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    measurements={}
    for role,count in COUNTS.items():
        classes=SLOT/('complete-'+role+'-main');classes.mkdir()
        with zipfile.ZipFile(n['jars'][role]['path']) as jar:
            physical={name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')}
            assert len(physical)==count
            for name in physical:
                target=classes/name;target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(jar.read(name))
        catalog=SLOT/('complete-'+role+'-main-catalog.txt')
        with catalog.open('x') as stream:
            stream.write(''.join(name+'\n' for name in sorted(physical)))
        stages.append(steps.step('measure-'+role,[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],role]))
        assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
        lines=(SLOT/('measure-'+role+'.stdout')).read_text().splitlines()
        assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1]=='FORBIDDEN_PROBE_HITS\t0'
        units={};packages=[];bundle=None;cursor=None;method_details={}
        for line in lines[2:]:
            fields=line.split('\t')
            if fields[0]=='PACKAGE_METADATA_ONLY':
                packages.append(fields[1]+'.class')
            elif fields[0]=='CLASS':
                name=fields[1]+'.class';assert name not in units
                cursor=dict(classCrc64=fields[2],counters={});units[name]=cursor
            elif fields[0]=='METHOD_DETAIL':
                method_key=fields[1]+fields[2];assert method_key not in method_details
                cursor=dict(counters={});method_details[method_key]=cursor
            elif fields[0]=='BUNDLE':
                assert fields==['BUNDLE','COMPLETE_'+role.upper()+'_ARTIFACT'] and bundle is None
                bundle={};cursor=dict(counters=bundle)
            else:
                assert len(fields)==4 and fields[0]=='COUNTER' and fields[1] not in cursor['counters']
                cursor['counters'][fields[1]]=dict(missed=int(fields[2]),covered=int(fields[3]))
        assert set(units)|set(packages)==set(physical) and not set(units)&set(packages)
        assert all(sum(row['counters'][kind][key] for row in units.values())==bundle[kind][key] for kind in ['METHOD','CLASS','BRANCH'] for key in ['missed','covered'])
        measurements[role]=dict(physicalClasses=count,physicalHashes=physical,units=units,packageMetadata=packages,completeCounters=bundle,methodDetails=method_details)
    selected=measurements['api']['units']['dev/codex/schubert/nk/api/monitoring/ExactDurationMeterRegistry.class']
    inner=measurements['api']['units']['dev/codex/schubert/nk/api/monitoring/ExactDurationMeterRegistry$ExactSummary.class']
    assert all(row['missed']==0 for row in inner['counters'].values())
    methods=measurements['api']['methodDetails']
    assert all(row['missed']==0 for row in selected['counters'].values()) and methods and all(row['missed']==0 for value in methods.values() for row in value['counters'].values())
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(path).read_bytes())==digest for path,digest in toolhashes.items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,selectedRegistryMain=selected,selectedRegistryInner=inner,selectedMethodDetails=methods,oldExecUnion=False,manualExclusionsAdded=False))
    data.write(OUT/'physical-test-metadata.json',dict(source=SOURCE,changed=sorted(changed),models=models,expectedScope=sorted(physical_scope),allPhysical=1962,allOtherUnchanged=1962-len(changed),metadataVectors=metadata_vectors))
    complete={role:value['completeCounters'] for role,value in measurements.items()}
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_SHA,originalHostManifestSha256=HOST_SHA,staticManifestSha256=STATIC_SHA,observedTestExecutions=10,suites=1,xmlHashes=xmls,execSha256=h['execSha256'],allMainClassesUnchanged=1843,allTestPhysical=1962,changedTestPhysical=len(changed),otherTestPhysicalUnchanged=1962-len(changed),metadataVectors=metadata_vectors,selectedRegistryMain=selected,selectedRegistryInner=inner,selectedMethodDetails=methods,completeArtifactCounters=complete,wholeArtifactCoverage100=False,rawStatic=3,spotbugsSixExit=0,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),physicalTestMetadataSha256=data.sha((OUT/'physical-test-metadata.json').read_bytes()),toolHashes=toolhashes,stages=stages,forbiddenProbeHits=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,externalActions=0))
    print(dict(actualExit=0,selectedRegistryMain=selected,selectedRegistryInner=inner,selectedMethodDetails=methods,completeArtifactCounters=complete,changedTestPhysical=len(changed),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__=='__main__':
    main()
