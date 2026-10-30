"""Resource DOM postv2: honest no-trace receipts/static JS, not expanded Product runtime permission."""
import copy
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validator
from trace_owner_join import canonical


def require(ok,message):
    if not ok:raise ValueError(message)

def assess(raw,original,run_path):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)
    stage=raw['stages'][1]
    require(stage['reviewedMainResourceHashes']==original.RESOURCES,'all exact reviewed Main resources')
    require(stage['ownedResourceReadCopies']=={str(run_path/'src/main/resources'/p):original.RESOURCES[p] for p in original.READ_COPIES},'only declared own exact read copies')
    if original.TRACE is None:require('ownedSyntheticTrace' not in stage,'trace-free original has no invented trace')
    else:require(stage['ownedSyntheticTrace']==dict(path=str(run_path/original.TRACE),sha256=data.sha(original.EXPECTED_TRACE.encode())),'fixed public own trace, not business output')

def validate_profile(original,profile):
    require(isinstance(profile,dict) and set(profile)=={'rawFolder','rawSha256','postFolder','resourceOwners'},'closed resource evidence profile')
    require(all(isinstance(profile[k],str) and re.fullmatch(r'PG[0-9]{4,6}-[a-z0-9-]+-v[1-9][0-9]*',profile[k]) for k in ['rawFolder','postFolder']) and profile['rawFolder']!=profile['postFolder'],'different canonical new-only paths')
    require(isinstance(profile['rawSha256'],str) and re.fullmatch(r'[0-9a-f]{64}',profile['rawSha256']),'frozen original receipt pin')
    require(isinstance(profile['resourceOwners'],dict) and profile['resourceOwners'] and all(k in original.RESOURCES and isinstance(v,str) and re.fullmatch(r'WBS-[A-Z][0-9]{3}-[0-9]{2}',v) for k,v in profile['resourceOwners'].items()),'explicit baseline resource owners')
    require(original.COMPILE_SHA=='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3','fixed qualified normal input')
    require(all(isinstance(p,str) and not Path(p).is_absolute() and '..' not in Path(p).parts and p.startswith(('templates/','static/css/','static/js/')) for p in original.RESOURCES),'reviewed Web resource paths only')
    if original.TRACE is None:require(original.EXPECTED_TRACE is None,'no trace means no expected trace text')
    else:require(isinstance(original.TRACE,str) and re.fullmatch(r'target/scenario-screen-traces/PT-SCR-[0-9]+\.txt',original.TRACE) and isinstance(original.EXPECTED_TRACE,str) and original.EXPECTED_TRACE,'own fixed public screen trace only')
    require(set(original.READ_COPIES)<=original.RESOURCES.keys() and len(original.READ_COPIES)==len(set(original.READ_COPIES)),'exact unique read-copy scope')
    require(original.COUNTS and all(type(n) is int and n>0 for n in original.COUNTS.values()) and original.FIXTURES=={} and original.SOURCE=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c','reviewed nonempty original scope')
    return True

def duplicate_case(value):
    if len(value['cases'])>1:value['cases'][1]=copy.deepcopy(value['cases'][0])
    else:value['cases'].append(copy.deepcopy(value['cases'][0]))

def verify_profile(original,profile):
    validate_profile(original,profile)
    raw_pin=profile['rawSha256'];run_path=data.ROOT.parent/'pgpt-runs/PG379'/profile['rawFolder'].lower();out=data.BASE/profile['postFolder'];total=sum(original.COUNTS.values())
    invocation=capture(__file__);require(not out.exists(),'new-only resource DOM post')
    raw=data.read_checked(data.BASE/profile['rawFolder']/'manifest.json',raw_pin)
    require(data.sha((run_path/'manifest.safe.json').read_bytes())==raw_pin,'original owned terminal receipt')
    assess(raw,original,run_path);normal=original.resource_inputs()
    hashes=normal['begin']['inputHashes'];require(raw['begin']['sourceHashes']==hashes,'all fixed normal inputs')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((original.COMPILE/'snapshot'/p).read_bytes())==h for p,h in hashes.items()),'whole normal current source unchanged')
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        require(all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][key].items()),'all original '+key+' unchanged')
    require(data.sha((run_path/'jacoco.exec').read_bytes())==raw['execSha256'],'owned actual exec retained but not coverage qualification')
    stage=raw['stages'][1]
    require(all(data.sha(Path(p).read_bytes())==h for p,h in stage['ownedResourceReadCopies'].items()),'resource read copies unchanged')
    if original.TRACE is not None:require((run_path/original.TRACE).read_text()==original.EXPECTED_TRACE,'literal own public trace matches frozen expected content')
    environment=[]
    with (run_path/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):environment.append(line.strip().split('=',1))
    require(len(environment)==len(dict(environment))==4 and dict(environment)==stage['reportedEnvironment'],'actual original JVM environment')
    declarations=set()
    for name,path in original.TESTS.items():
        text=path.read_text();require(data.sha(path.read_bytes())==original.PINS[name],'whole original Test pin')
        package=re.search(r'^package ([A-Za-z0-9_.]+);',text).group(1)
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text)
        require(len(methods)==original.COUNTS[name],'all original methods');declarations.update((package+'.'+name,m) for m in methods)
    actual=[]
    for name,digest in raw['xmlHashes'].items():
        value=(run_path/'xml'/name).read_bytes();require(data.sha(value)==digest,'actual XML hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'actual XML FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'all cases actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==total and len({c for c,n in actual})==len(original.COUNTS) and set(actual)==declarations=={(v['classname'],v['name']) for v in raw['cases']},'exact whole original methods, not selected subset')
    labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('failure',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',duplicate_case),('resource',lambda v:v['stages'][1]['reviewedMainResourceHashes'].pop(next(iter(original.RESOURCES)))),('read-copy',lambda v:v['stages'][1]['ownedResourceReadCopies'].update({'/other':'0'*64})),('trace',lambda v:v['stages'][1].update(ownedSyntheticTrace=dict(path='/other',sha256='0'*64))),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('old',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad,original,run_path)
        except ValueError:labels.append(label)
        else:raise ValueError('false resource XML receipt accepted '+label)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-web/src/main/resources/'+p for p in original.RESOURCES]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    require(all(owners['src/schubert-nk-web/src/main/resources/'+path]['canonicalOwner']==owner for path,owner in profile['resourceOwners'].items()),'canonical resource owners, not cost reassignment')
    require('invocation' not in raw and isinstance(raw['begin']['invocation'],dict),'raw invocation only in begin')
    verify(raw['begin']['invocation']);verify(invocation);out.mkdir()
    for name,digest in raw['xmlHashes'].items():
        shutil.copyfile(run_path/'xml'/name,out/name);require(data.sha((out/name).read_bytes())==digest,'returned XML unmodified')
    if original.TRACE is not None:shutil.copyfile(run_path/original.TRACE,out/Path(original.TRACE).name)
    data.write(out/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,rawSha256=raw_pin,normalSha256=original.COMPILE_SHA,tests=total,suites=len(original.COUNTS),cases=raw['cases'],xmlHashes=raw['xmlHashes'],failures=0,errors=0,skipped=0,reruns=0,reportedEnvironment=dict(environment),reviewedResourceHashes=original.RESOURCES,owners=owners,ownedSyntheticTrace=stage.get('ownedSyntheticTrace'),javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,coverageExecRetainedSha256=raw['execSha256'],actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,onlyReviewedHostResourcesAndOwnedMockMvc=True,originalStages=raw['stages'],metadataNegativeVectors=len(labels),negativeLabels=labels,productTestsReexecutedByPost=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((out/'manifest.json').read_bytes()))
