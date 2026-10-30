"""Returned original Music DOM/CSS6 proof; no new Main counters or actual Browser claim."""
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
import pg14790_music_hierarchy_template_six_pt as original

RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14790-music-hierarchy-template-six-pt-v1'
OUT=data.BASE/'PG14792-music-hierarchy-template-six-post-v1'
RAW='8ae7f78147a1d9d81a593a4534348caef007b305a0b991d513321833b26874a8'

def require(ok,message):
    if not ok:raise ValueError(message)

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)
    stage=raw['stages'][1]
    require(stage['reviewedMainResourceHashes']==original.RESOURCES,'four exact reviewed Main resources')
    require(stage['ownedResourceReadCopies']=={str(RUN/'src/main/resources'/p):original.RESOURCES[p] for p in original.READ_COPIES},'only three own exact read copies')
    require(stage['ownedSyntheticTrace']==dict(path=str(RUN/original.TRACE),sha256=data.sha(original.EXPECTED_TRACE.encode())),'fixed public own trace, not business output')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only resource DOM post')
    raw=data.read_checked(data.BASE/'PG14790-music-hierarchy-template-six-pt-v1/manifest.json',RAW)
    require(data.sha((RUN/'manifest.safe.json').read_bytes())==RAW,'original owned terminal receipt')
    assess(raw);normal=original.resource_inputs()
    hashes=normal['begin']['inputHashes'];require(raw['begin']['sourceHashes']==hashes,'all fixed normal inputs')
    require(all(data.sha((data.ROOT/p).read_bytes())==data.sha((original.COMPILE/'snapshot'/p).read_bytes())==h for p,h in hashes.items()),'whole normal current source unchanged')
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        require(all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][key].items()),'all original '+key+' unchanged')
    require(data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'],'owned actual exec retained but not coverage qualification')
    stage=raw['stages'][1]
    require(all(data.sha(Path(p).read_bytes())==h for p,h in stage['ownedResourceReadCopies'].items()),'resource read copies unchanged')
    require((RUN/original.TRACE).read_text()==original.EXPECTED_TRACE,'literal own public trace matches64renders/20/100 bounds')
    environment=[]
    with (RUN/'selected-junit.log').open() as stream:
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
        value=(RUN/'xml'/name).read_bytes();require(data.sha(value)==digest,'actual XML hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'actual XML FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'all cases actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==6 and len({c for c,n in actual})==1 and set(actual)==declarations=={(v['classname'],v['name']) for v in raw['cases']},'exact original six, not selected subset')
    labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('failure',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('resource',lambda v:v['stages'][1]['reviewedMainResourceHashes'].pop('templates/music.html')),('read-copy',lambda v:v['stages'][1]['ownedResourceReadCopies'].update({'/other':'0'*64})),('trace',lambda v:v['stages'][1]['ownedSyntheticTrace'].update(sha256='0'*64)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('old',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false resource XML receipt accepted '+label)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-web/src/main/resources/'+p for p in original.RESOURCES]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    require(owners['src/schubert-nk-web/src/main/resources/templates/music.html']['canonicalOwner']=='WBS-P016-11' and owners['src/schubert-nk-web/src/main/resources/templates/music-sections.html']['canonicalOwner']=='WBS-P016-12','canonical template owners, additional cost0')
    require('invocation' not in raw and isinstance(raw['begin']['invocation'],dict),'raw invocation only in begin')
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for name,digest in raw['xmlHashes'].items():
        shutil.copyfile(RUN/'xml'/name,OUT/name);require(data.sha((OUT/name).read_bytes())==digest,'returned XML unmodified')
    shutil.copyfile(RUN/original.TRACE,OUT/'PT-SCR-071.txt')
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,rawSha256=RAW,normalSha256=original.COMPILE_SHA,tests=6,suites=1,cases=raw['cases'],xmlHashes=raw['xmlHashes'],failures=0,errors=0,skipped=0,reruns=0,reportedEnvironment=dict(environment),reviewedResourceHashes=original.RESOURCES,owners=owners,ownedSyntheticTrace=stage['ownedSyntheticTrace'],javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,coverageExecRetainedSha256=raw['execSha256'],actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,onlyReviewedHostResourcesAndOwnedMockMvc=True,originalStages=raw['stages'],metadataNegativeVectors=len(labels),negativeLabels=labels,productTestsReexecutedByPost=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
