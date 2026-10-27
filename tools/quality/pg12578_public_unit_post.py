"""Independent whole13 XML, public-only resource resolution and physical/Main identity; no PT replay."""
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts as class_parts, selftest

SOURCE='2efcd4ac8e1b7681fdba0862f7392bbbba5d3f68'
OUT=data.BASE/'PG12578-public-unit-post-v1'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg12575-public-unit-host-v2'
STATIC_SHA='7ab10e270524f200cf1bd53597127f4709f0df92fe0a26ee3211e0a4e62b3806'


def main():
    invocation=capture(__file__);assert not OUT.exists()
    n=data.read_checked(data.BASE/'PG12572-public-unit-six-compile-v1/manifest.json','fe361f6c8fb14008feb760c5b0437f7fc68777a776eb39ca7febc8ec49a27c1a')
    old=data.read_checked(data.BASE/'PG12551-monitoring-main-six-compile-v2/manifest.json','a51e4812b19c20f1ef673b35278a9c4ef75e08100e785360033bbd5c1afdc5e0')
    h=data.read_checked(data.BASE/'PG12575-public-unit-host-v2/manifest.json','52616e3280b26d21f53db04ac1ba1bc0ae5ffaaa5bb5ae8784b501a1d5a3e70d')
    s=data.read_checked(data.BASE/'PG12576-public-unit-static-v1/manifest.json',STATIC_SHA)
    plan=data.read_checked(data.BASE/'PG12570-public-unit-plan-v1/manifest.json','5ec7235434a5c8ce0c379da9decc85975dd2db1e7c60a2252e56eb6f121ae9e4')
    assert n['source']==h['source']==s['source']==SOURCE and n['actualExit']==n['testsExecuted']==h['actualExit']==s['actualExit']==0
    assert h['observedTestExecutions']==13 and h['mainCoverage']=='NOT_APPLICABLE_CONFIGURATION' and h['execSha256'] is None and not h['oldExecUnion']
    assert all(x['actualExit']==0 and not x['timedOut'] for x in h['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles'],**h['begin']['fixtureResourceFiles']}.items())
    expected=Counter((r['className'],r['method']) for r in h['begin']['cases']);observed=[];xmls={}
    for f in (RUN/'xml').glob('TEST-*.xml'):
        root=ET.parse(f).getroot();assert all(root.get(k)=='0' for k in ['failures','errors','skipped'])
        assert all(not list(r) for r in root.findall('testcase'));observed.extend((r.get('classname'),r.get('name')) for r in root.findall('testcase'));xmls[f.name]=data.sha(f.read_bytes())
    assert len(xmls)==3 and len(observed)==13 and Counter(observed)==expected and xmls==h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text()=='found=13;started=13;succeeded=13;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    loadraw=(RUN/'classload-metadata.log').read_bytes();assert data.sha(loadraw)==h['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadraw.decode()));permitted={r['className'] for r in h['begin']['cases']}
    product=[x for x in loaded if x.startswith('dev.codex.schubert.nk.')]
    assert product and all(any(x==p or x.startswith(p+'$') for p in permitted) for x in product)
    assert not h['begin']['productJarsInExecutionClasspath'] and not set(h['begin']['classPathEntries'])&{v['path'] for v in n['jars'].values()}
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.'))]
    assert jar_classes(old)==jar_classes(n) and len(jar_classes(n))==1843
    a,b=test_classes(old),test_classes(n);assert set(a)==set(b) and len(b)==1962
    changed={key for key in b if b[key]!=a[key]};source_files={Path(r['path']).name for r in plan['sourceChanges']};metadata={}
    for role,entry in sorted(changed):
        before=class_parts((Path(old['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        after=class_parts((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role=='batch' and after['model']['sourceFile']==before['model']['sourceFile'] and after['model']['sourceFile'] in source_files
        metadata[entry]=dict(sourceFile=after['model']['sourceFile'],beforeSha256=a[(role,entry)],sha256=b[(role,entry)],rawCodeSame=before['rawCodeRepresentationSha256']==after['rawCodeRepresentationSha256'],debugSame=before['debugTablesSha256']==after['debugTablesSha256'])
    assert {r['sourceFile'] for r in metadata.values()}==source_files
    resources=[]
    for row in h['begin']['publicResources']:
        path=row['path'];assert data.sha((Path(h['begin']['normalSnapshot'])/path).read_bytes())==n['begin']['inputHashes'][path]==old['begin']['inputHashes'][path]==row['sha256']
        if 'resourcePath' in row:
            locations=[]
            for entry in h['begin']['classPathEntries']:
                p=Path(entry)
                if p.is_dir():
                    if (p/row['resourcePath']).is_file():
                        assert data.sha((p/row['resourcePath']).read_bytes())==row['sha256'];locations.append(str(p))
                elif p.suffix=='.jar':
                    with zipfile.ZipFile(p) as jar:
                        if row['resourcePath'] in jar.namelist():locations.append(str(p))
            assert locations==row['classPathDefinition'];resources.append(dict(path=path,sha256=row['sha256'],uniqueDefinition=locations))
    assert len(resources)==len(h['begin']['fixtureResourceFiles'])==4
    for label,v in s['reports'].items():
        assert v['findings']==v['processingErrors']==0 and data.sha((data.BASE/'PG12576-public-unit-static-v1'/(label+'.xml')).read_bytes())==v['sha256']
    assert all(x['actualExit']==0 and not x['timedOut'] for x in s['stages'].values())
    assert not list(Path(h['begin']['testCwd']).iterdir())
    helper=Path(h['begin']['helperPath']);assert data.sha(helper.read_bytes())==h['begin']['helperSha256']
    verify(invocation);OUT.mkdir();data.write(OUT/'physical-test-metadata.json',dict(source=SOURCE,classes=metadata,readerVectors=selftest()))
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,observedTestExecutions=13,suites=3,xmlHashes=xmls,originalHostManifestSha256='52616e3280b26d21f53db04ac1ba1bc0ae5ffaaa5bb5ae8784b501a1d5a3e70d',allMainClassesUnchanged=1843,changedTestPhysical=len(changed),otherTestPhysicalUnchanged=1962-len(changed),changedSourceFiles=3,physicalTestMetadataSha256=data.sha((OUT/'physical-test-metadata.json').read_bytes()),publicResourceInputs=len(h['begin']['publicResources']),independentUniqueClasspathResources=resources,actualProductMainClassesLoaded=0,productJarsInExecutionClasspath=0,rawStatic=0,coverage=None,mainCoverage='NOT_APPLICABLE_CONFIGURATION',productTestsExecutedByPost=0,oldExecUnion=False,wholeC02Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False)
    data.write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=0,changedTestPhysical=len(changed),otherTestPhysicalUnchanged=1962-len(changed),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__=='__main__':main()
