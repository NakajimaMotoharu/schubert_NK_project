"""Resource-only Node/V8 evidence verification; never invent zero-scope Java coverage."""
import copy
import json
import re
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
import scoped_prometheus_post as validator
import pg14778_web_four_script_resources_pt as original

RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14778-web-four-script-resources-pt-v1'
OUT=data.BASE/'PG14780-web-four-script-resources-post-v1'
RAW='5f4205513895cd2ea19ca369d5bffe6d1a752cc959a5ed04913a028ab247d7f8'
ROWS={
 'log-search-validation':('pt-log-script',8,'PT-SCR092'),
 'operation-post-submit':('pt-operation-script',6,'PT-WEB-OPSJS2646'),
 'search-speaker-submit':('pt-search-script',8,'PT-SCR025'),
 'question-input-validation':('pt-question-script',8,'PT-QST-JS001')}

def require(ok,message):
    if not ok:raise ValueError(message)

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)
    stage=raw['stages'][1]
    require(stage['ownedSourceCopies']==original.COPY_INPUTS and stage['nodeBinary']==dict(path=str(original.NODE),sha256=original.NODE_PIN),'exact resource-only fixture and Node pins')
    require('-Dnk.pt.node='+str(original.NODE) in stage['command'],'original JVM used fixed absolute Node, not arbitrary PATH')

def parse_tap(text,name,count):
    lines=text.splitlines()
    for expected in ['# tests '+str(count),'# pass '+str(count),'# fail 0','# cancelled 0','# skipped 0','# todo 0']:
        require(lines.count(expected)==1,'each actual TAP count exactly once')
    require(not any(line.startswith('not ok ') for line in lines),'no failed nested case')
    cases=[(int(m.group(1)),m.group(2)) for line in lines if (m:=re.fullmatch(r'ok ([0-9]+) - (.+)',line))]
    require([v[0] for v in cases]==list(range(1,count+1)),'all declared Node cases, no missing/skipped case')
    headers=[line for line in lines if line.startswith('# file') and '|' in line]
    require(len(headers)==1 and [v.strip() for v in headers[0][2:].split('|')]==['file','line %','branch %','funcs %','uncovered lines'],'explicit V8 column roles')
    rows=[line[2:].split('|') for line in lines if line.startswith('# ') and '|' in line and line[2:].split('|')[0].strip()==name+'.js']
    require(len(rows)==1 and len(rows[0])==5 and all(v.strip()=='100.00' for v in rows[0][1:4]) and not rows[0][4].strip(),'nonempty exact production file, L/B/F all100 and no uncovered lines')
    return [v[1] for v in cases],dict(linePercent=100,branchPercent=100,functionPercent=100,classCounter='NOT_APPLICABLE_JAVASCRIPT_RESOURCE')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only resource post')
    raw=data.read_checked(data.BASE/'PG14778-web-four-script-resources-pt-v1/manifest.json',RAW);require(data.sha((RUN/'manifest.safe.json').read_bytes())==RAW,'original own run receipt')
    assess(raw);normal=original.inputs();require(raw['begin']['sourceHashes']==normal['begin']['inputHashes'],'entire fixed normal input identity')
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes']:
        require(all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][key].items()),'all original '+key+' unchanged')
    require(all(data.sha((RUN/p).read_bytes())==h for p,h in original.COPY_INPUTS.items()),'all own copies exactly normal/Jar resources')
    prefix=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):prefix.append(line.strip().split('=',1))
    require(len(prefix)==len(dict(prefix))==4 and dict(prefix)==raw['stages'][1]['reportedEnvironment'],'actual original JVM environment, not current host substitution')
    actual=[]
    for filename,h in raw['xmlHashes'].items():
        value=(RUN/'xml'/filename).read_bytes();require(data.sha(value)==h,'original XML exact hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'Java wrapper XML FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'no non-PASS wrapper');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==5 and len({c for c,n in actual})==4 and set(actual)=={(v['classname'],v['name']) for v in raw['cases']},'all original wrapper methods5/suites4')
    artifacts={};resources={};node_cases=[]
    for name,(folder,count,prefix_id) in ROWS.items():
        root=RUN/'target'/folder;require((root/'version.txt').read_text().strip()=='v24.19.0' and not (root/'syntax.txt').read_text().strip(),'actual Nodeversion and successful syntax stdout')
        tap=(root/'node.tap').read_text();cases,counters=parse_tap(tap,name,count)
        source=data.ROOT/'src/schubert-nk-web/src/test/javascript'/(name+'.test.cjs')
        expected=re.findall(r'^test\("([^"\n]+)"',source.read_text(),re.MULTILINE)
        require(cases==expected and len(cases)==count and all(v.startswith(prefix_id+'-') for v in cases),'actual Node IDs equal frozen original CJS declarations')
        node_cases.extend(cases)
        for filename in ['version.txt','syntax.txt','node.tap']:
            rel=str((root/filename).relative_to(RUN));artifacts[rel]=data.sha((root/filename).read_bytes())
        resources[name]=dict(path='src/schubert-nk-web/src/main/resources/static/js/'+name+'.js',sha256=original.COPY_INPUTS['src/main/resources/static/js/'+name+'.js'],nodeTests=count,nodeCases=cases,coverage=counters,tapPath='target/'+folder+'/node.tap',tapSha256=artifacts['target/'+folder+'/node.tap'],actualBrowser=False)
    require(len(node_cases)==len(set(node_cases))==30,'thirty child Node cases, not extra Java methods')
    labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('failure',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('fixture',lambda v:v['stages'][1]['ownedSourceCopies'].update({'src/other':'0'*64})),('node-pin',lambda v:v['stages'][1]['nodeBinary'].update(sha256='0'*64)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('old',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false resource receipt accepted '+label)
    sample=(RUN/'target/pt-log-script/node.tap').read_text();tap_labels=[]
    for label,text in [('failed-count',sample.replace('# fail 0','# fail 1')),('missing-production-file',sample.replace('log-search-validation.js','unknown.js')),('line-not100',sample.replace('100.00','99.99',1)),('skipped',sample.replace('# skipped 0','# skipped 1'))]:
        try:parse_tap(text,'log-search-validation',8)
        except ValueError:tap_labels.append(label)
        else:raise ValueError('false TAP accepted '+label)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-web/'+p for p in original.COPY_INPUTS]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=normal['begin']['inputHashes'][p],**canonical(p,logical)) for p in paths}
    require(all(owners[v['path']]['canonicalOwner']=='WBS-P016-25' for v in resources.values()),'baseline resource owners retained, not cost parents')
    original.inputs();verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);require(data.sha((OUT/filename).read_bytes())==h,'returned XML copy unchanged')
    for relative,h in artifacts.items():
        target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(RUN/relative,target);require(data.sha(target.read_bytes())==h,'public resource output unchanged')
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,rawManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,tests=5,suites=4,cases=raw['cases'],xmlHashes=raw['xmlHashes'],failures=0,errors=0,skipped=0,reruns=0,javaWrapperMethods=5,nodeSubcases=30,nodeSubcasesNotAddedToJavaMethods=True,productionJavascriptResources=resources,resourcePrograms=4,resourceLineFunctionBranch100=True,javaSourceProgramsQualified=0,javaCoverageGate='NOT_APPLICABLE_TO_RESOURCE_ONLY_SCOPE',owners=owners,nodeBinary=dict(path=str(original.NODE),sha256=original.NODE_PIN,version='v24.19.0'),reportedEnvironment=dict(prefix),originalStages=raw['stages'],outputHashes=artifacts,copiedSourceResources=original.COPY_INPUTS,metadataNegativeVectors=len(labels),negativeLabels=labels,tapNegativeVectors=len(tap_labels),tapNegativeLabels=tap_labels,actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,productTestsReexecutedByPost=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
