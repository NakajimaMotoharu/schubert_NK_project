"""Independent whole20 actual XML/CRC, source delta and complete three-artifact counters; no replay."""
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
from pg11929_storage_fixture_class_metadata import parts as class_parts, selftest
import pg9346_direct_companion_jdk_post as steps

SOURCE='e353b1f49a740a426031fdc199f7ce8b26081971'
OUT=data.BASE/'PG12693-scenario-writer-post-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12693-scenario-writer-post-v2'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg12688-scenario-writer-host-v1'


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n=data.read_checked(data.BASE/'PG12686-scenario-writer-six-compile-v1/manifest.json','20ef6bfc17fb7fdb9a7cab61c1d927bcb480ec36dffadbd0e5e7fc5c0ed23a9d')
    h=data.read_checked(data.BASE/'PG12688-scenario-writer-host-v1/manifest.json','6c1805f0ee828d482aa89190460811c30514422beec074b2ff604214990caff8')
    s=data.read_checked(data.BASE/'PG12690-scenario-writer-static-v1/manifest.json','17b8482c9fa40b627242b21a418ac385a925ecd66fe68ec57752ca7d0a666692')
    old=data.read_checked(data.BASE/'PG12666-transfer-verifier-six-compile-v1/manifest.json','138b454a9eb9d3d00f6ac2579d6f76b36afbc340b745375d53dfa8383bf59e10')
    plan=data.read_checked(data.BASE/'PG12684-scenario-writer-plan-v1/manifest.json','71ae38137584d347696953a2ae460d1bb825a05a97dd1cbbb37ac794b4f58075')
    assert n['source']=='e353b1f49a740a426031fdc199f7ce8b26081971' and h['begin']['normalSourceResolved']==h['source']==s['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==0 and s['actualExit']==1
    assert h['observedTestExecutions']==8 and not h['oldExecUnion'] and all(x['actualExit']==0 and not x['timedOut'] for x in h['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles']}.items())
    expected=Counter((r['className'],r['method']) for r in h['begin']['cases']);actual=[];xmls={}
    for f in (RUN/'xml').glob('TEST-*.xml'):
        node=ET.parse(f).getroot();assert all(node.get(k)=='0' for k in ['failures','errors','skipped']) and all(not list(r) for r in node.findall('testcase'))
        actual.extend((r.get('classname'),r.get('name')) for r in node.findall('testcase'));xmls[f.name]=data.sha(f.read_bytes())
    assert len(xmls)==2 and len(actual)==8 and Counter(actual)==expected and xmls==h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text()=='found=8;started=8;succeeded=8;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes())==h['execSha256']
    loadedraw=(RUN/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==h['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()))
    extra='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/scenario/ScenarioEntryRecord.java'
    extra_hash=n['begin']['inputHashes'][extra];assert data.sha((data.ROOT/extra).read_bytes())==data.sha((Path(h['begin']['normalSnapshot'])/extra).read_bytes())==extra_hash
    reviewed={**h['begin']['eligibilityClosureSourceHashes'],extra:extra_hash};assert len(reviewed)==57
    by_binary={p.split('/java/',1)[1][:-5].replace('/','.') for p in reviewed}
    direct_imports={}
    for path in [*reviewed,*{c['path'] for c in h['begin']['cases']}]:
        text=(data.ROOT/path).read_text();imports=re.findall(r'^import (dev\.codex\.schubert\.nk\.[\w.]+);',text,re.M)
        assert set(imports)<=by_binary;direct_imports[path]=imports
    target=extra.split('/java/',1)[1][:-5]+'.class';locations=[]
    for entry in h['begin']['classpath'].split(os.pathsep):
        path=Path(entry)
        if path.is_dir():
            if (path/target).is_file():locations.append(entry)
        elif path.suffix=='.jar':
            with zipfile.ZipFile(path) as jar:
                if target in jar.namelist():locations.append(entry)
    assert locations==[n['jars']['protocol']['path']]
    allowed=[p.split('/java/',1)[1][:-5].replace('/','.') for p in reviewed]+[r['className'] for r in h['begin']['cases']]
    assert not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not any(x==p or x.startswith(p+'$') for p in allowed)]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.'))]
    assert jar_classes(old)==jar_classes(n) and len(jar_classes(n))==1843
    a,b=test_classes(old),test_classes(n);assert set(a)==set(b) and len(a)==len(b)==1962
    changed={key for key in b if a[key]!=b[key]};assert len(changed)==2
    source_files={Path(r['path']).name for r in plan['sourceChanges']};code_debug={}
    for role,entry in sorted(changed):
        before=class_parts((Path(old['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        after=class_parts((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role=='api' and after['model']['sourceFile']==before['model']['sourceFile'] and after['model']['sourceFile'] in source_files
        code_debug[entry]=dict(sourceFile=after['model']['sourceFile'],beforeSha256=a[(role,entry)],sha256=b[(role,entry)],rawCodeSame=before['rawCodeRepresentationSha256']==after['rawCodeRepresentationSha256'],debugSame=before['debugTablesSha256']==after['debugTablesSha256'])
    assert {r['sourceFile'] for r in code_debug.values()}==source_files
    for label,v in s['reports'].items():
        assert v['processingErrors']==0 and v['findings']==(2 if label=='pmd' else 0)
        assert data.sha((data.BASE/'PG12690-scenario-writer-static-v1'/(label+'.xml')).read_bytes())==v['sha256']
    warnings=[x for x in ET.parse(data.BASE/'PG12690-scenario-writer-static-v1/pmd.xml').getroot().iter() if x.tag.rpartition('}')[2]=='violation']
    assert len(warnings)==2 and all(x.get('rule')=='DoNotUseThreads' for x in warnings)
    SLOT.mkdir();reader=SLOT/'reader';reader.mkdir();steps.SLOT=SLOT;tc=data.ROOT.parent/'toolchain'
    helper=data.ROOT/'tools/quality/architecture/ScenarioWriterArtifactCoverageMeasureV2.java'
    libs=[tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[tc/f'm2/repository/org/ow2/asm/{x}/9.10.1/{x}-9.10.1.jar' for x in ['asm','asm-tree','asm-commons']]]
    tools={str(p):data.sha(p.read_bytes()) for p in [helper,*libs]};cp=os.pathsep.join(map(str,libs))
    stages=[steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    measurements={}
    for role in ['api','protocol','storage']:
        classes=SLOT/('complete-'+role+'-main');classes.mkdir()
        with zipfile.ZipFile(n['jars'][role]['path']) as jar:
            physical={name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')};assert len(physical)=={'api':467,'protocol':176,'storage':80}[role]
            for name in physical:
                f=classes/name;f.parent.mkdir(parents=True,exist_ok=True)
                with f.open('xb') as stream:stream.write(jar.read(name))
        catalog=SLOT/('complete-'+role+'-catalog.txt')
        with catalog.open('x') as f:f.write(''.join(name+'\n' for name in sorted(physical)))
        stages.append(steps.step('measure-'+role,[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],role]))
        assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
        lines=(SLOT/('measure-'+role+'.stdout')).read_text().splitlines();assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1]=='FORBIDDEN_PROBE_HITS\t0'
        units={};packages=[];bundle=None;current=None
        for line in lines[2:]:
            row=line.split('\t')
            if row[0]=='PACKAGE_METADATA_ONLY':packages.append(row[1]+'.class')
            elif row[0]=='CLASS':
                name=row[1]+'.class';assert name not in units;current=dict(classCrc64=row[2],counters={});units[name]=current
            elif row[0]=='BUNDLE':
                assert row==['BUNDLE','COMPLETE_'+role.upper()+'_ARTIFACT'] and bundle is None;bundle={};current=dict(counters=bundle)
            else:
                assert len(row)==4 and row[0]=='COUNTER' and row[1] not in current['counters'];current['counters'][row[1]]=dict(missed=int(row[2]),covered=int(row[3]))
        assert set(units)|set(packages)==set(physical) and not set(units)&set(packages)
        assert all(sum(v['counters'][kind][key] for v in units.values())==bundle[kind][key] for kind in ['METHOD','CLASS','BRANCH'] for key in ['missed','covered'])
        measurements[role]=dict(units=units,packageMetadata=packages,bundleCounters=bundle,wholeArtifactCoverage100=all(v['missed']==0 for v in bundle.values()))
    targets={'api':['dev/codex/schubert/nk/api/storage/ScenarioRecordStream.class','dev/codex/schubert/nk/api/storage/TransferContentVerifier.class'],'protocol':['dev/codex/schubert/nk/protocol/file/LargeResultContent.class'],'storage':['dev/codex/schubert/nk/storage/StorageIoException.class','dev/codex/schubert/nk/storage/StorageIoException$Reason.class']}
    direct={p:measurements[role]['units'][p] for role,paths in targets.items() for p in paths}
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(p).read_bytes())==digest for p,digest in tools.items())
    temp=Path(h['begin']['ownedTempRoot']);assert h['ownedTempRootEmptyAfter'] and h['begin']['ownedTempCleanupMode']=='ALWAYS' and not temp.is_symlink() and not list(temp.iterdir())
    assert dict(device=temp.stat().st_dev,inode=temp.stat().st_ino,mode=temp.stat().st_mode & 0o777)==h['begin']['ownedTempRootIdentity']
    verify(invocation);OUT.mkdir();data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,directWriterVerifierClasses=direct,oldExecUnion=False,manualCoverageExclusionsAdded=False));data.write(OUT/'physical-test-metadata.json',dict(source=SOURCE,classes=code_debug,readerVectors=selftest()))
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,observedTestExecutions=8,suites=2,originalHostManifestSha256='6c1805f0ee828d482aa89190460811c30514422beec074b2ff604214990caff8',allMainClassesUnchanged=1843,changedTestPhysical=len(changed),otherTestPhysicalUnchanged=1962-len(changed),measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),physicalTestMetadataSha256=data.sha((OUT/'physical-test-metadata.json').read_bytes()),rawStatic=2,staticActualExit=1,rawStaticRules=['DoNotUseThreads'],checkstyle=0,directWriterVerifierClasses=direct,wholeArtifactsCoverage100=False,forbiddenProbeHits=0,ownedTempRootEmptyAfter=True,ownedTempIdentityUnchanged=True,extraReviewedSourceHashes={extra:extra_hash},directImportsBySource=direct_imports,extraRecordClassDefinition=locations,productTestsExecutedByPost=0,oldExecUnion=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,tools=tools,stages=stages)
    data.write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=0,changedTestPhysical=len(changed),directWriterVerifierClasses=direct,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__=='__main__':main()
