"""Independent returned XML/TAP/resource qualification, no Product execution."""
import copy
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg14778_web_four_script_resources_pt as original

OUT=data.BASE/'PG14782-web-four-script-resources-independent-v1'
POST=data.BASE/'PG14780-web-four-script-resources-post-v1'
PIN='93523a10ae49e619195a4a228a528a822c32184adb218cb78268eb998752ef05'
ROWS={
 'log-search-validation':('pt-log-script',8),
 'operation-post-submit':('pt-operation-script',6),
 'search-speaker-submit':('pt-search-script',8),
 'question-input-validation':('pt-question-script',8)}

def require(ok,message):
    if not ok:raise ValueError(message)

def tap_contract(text,name,count):
    lines=text.splitlines()
    totals={}
    for key in ['tests','pass','fail','cancelled','skipped','todo']:
        hits=[int(m.group(1)) for line in lines if (m:=re.fullmatch('# '+key+r' ([0-9]+)',line))]
        require(len(hits)==1,'one actual total per Node role');totals[key]=hits[0]
    require(totals['tests']==totals['pass']==count and all(totals[k]==0 for k in ['fail','cancelled','skipped','todo']),'Node children all PASS')
    cases=[(int(m.group(1)),m.group(2)) for line in lines if (m:=re.fullmatch(r'ok ([0-9]+) - (.+)',line))]
    require([i for i,n in cases]==list(range(1,count+1)) and not any(line.startswith('not ok ') for line in lines),'complete original child sequence')
    rows=[line[2:].split('|') for line in lines if line.startswith('# ') and '|' in line]
    headers=[r for r in rows if r[0].strip()=='file']
    require(len(headers)==1 and [v.strip() for v in headers[0]]==['file','line %','branch %','funcs %','uncovered lines'],'actual V8 roles')
    matches=[r for r in rows if r[0].strip()==name+'.js']
    require(len(matches)==1 and len(matches[0])==5 and [v.strip() for v in matches[0][1:]]==['100.00','100.00','100.00',''],'exact nonempty Production resource all three100')
    return [n for i,n in cases]

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent resource receipt')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14778-web-four-script-resources-pt-v1/manifest.json','5f4205513895cd2ea19ca369d5bffe6d1a752cc959a5ed04913a028ab247d7f8')
    normal=original.inputs()
    require(raw['begin']['sourceHashes']==normal['begin']['inputHashes'] and raw['source']==p['source']==original.SOURCE and raw['actualExit']==p['actualExit']==0,'fixed source and genuine raw terminal')
    require(all(s['actualExit']==0 and s['timedOut'] is False for s in raw['stages']),'own compile and Product stages terminated0')
    declarations=set()
    for name,path in original.TESTS.items():
        require(data.sha(path.read_bytes())==original.PINS[name],'whole original wrapper frozen')
        text=path.read_text();package=re.search(r'^package ([A-Za-z0-9_.]+);',text).group(1)
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text)
        require(len(methods)==original.COUNTS[name],'whole wrapper count');declarations.update((package+'.'+name,m) for m in methods)
    actual=[]
    for name,digest in p['xmlHashes'].items():
        value=(POST/name).read_bytes();require(data.sha(value)==digest==raw['xmlHashes'][name],'original returned XML hash')
        tree=ET.fromstring(value)
        require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all wrappers PASS')
        for case in tree.findall('testcase'):
            require(not list(case),'no wrapper failure/skipped');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==5 and len({c for c,n in actual})==4 and set(actual)==declarations=={(v['classname'],v['name']) for v in raw['cases']},'five original methods, four suites')
    children=[];resource_rows={}
    for name,(folder,count) in ROWS.items():
        rel='target/'+folder+'/node.tap';value=(POST/rel).read_bytes()
        require(data.sha(value)==p['outputHashes'][rel],'actual returned TAP hash')
        ids=tap_contract(value.decode(),name,count)
        cjs=data.ROOT/'src/schubert-nk-web/src/test/javascript'/(name+'.test.cjs')
        require(ids==re.findall(r'^test\("([^"\n]+)"',cjs.read_text(),re.MULTILINE),'independent frozen literal case IDs')
        for filename in ['version.txt','syntax.txt']:
            path='target/'+folder+'/'+filename;require(data.sha((POST/path).read_bytes())==p['outputHashes'][path],'actual version/syntax output hash')
        require((POST/'target'/folder/'version.txt').read_text().strip()=='v24.19.0' and not (POST/'target'/folder/'syntax.txt').read_text().strip(),'actual fixed Node/version syntax')
        child=p['productionJavascriptResources'][name]
        require(child['nodeCases']==ids and child['nodeTests']==count and child['tapSha256']==data.sha(value) and child['actualBrowser'] is False,'actual children not Browser success')
        resource_rows[name]=dict(path=child['path'],sha256=child['sha256'],nodeCases=ids,tapSha256=data.sha(value),linePercent=100,functionPercent=100,branchPercent=100)
        children.extend(ids)
    require(len(children)==len(set(children))==30,'thirty child cases, not thirty Java methods')
    fixed={k:p[k] for k in ['source','cases','xmlHashes','productionJavascriptResources','copiedSourceResources','owners','reportedEnvironment','nodeBinary','originalStages','outputHashes']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual source/outputs/resources/owners/environment fixed')
        require(v['actualExit']==0 and v['tests']==v['javaWrapperMethods']==5 and v['suites']==4 and v['nodeSubcases']==30 and v['nodeSubcasesNotAddedToJavaMethods'] is True,'separate Java and Node domains')
        require(v['resourcePrograms']==4 and v['resourceLineFunctionBranch100'] is True and v['javaSourceProgramsQualified']==0 and v['javaCoverageGate']=='NOT_APPLICABLE_TO_RESOURCE_ONLY_SCOPE','resource-only coverage, no vacuous Java credit')
        require(all(v[k]==0 for k in ['actualBrowserActions','actualNetworkActions','actualVmActions','actualDatabaseActions','actualServiceActions','productTestsReexecutedByPost','newTestIds','newAccepted']),'no external/replay/new acceptance')
        require(v['formalUpdated'] is v['wholeF03Accepted'] is v['whole451Accepted'] is False and v['effortPercent'] is None,'no formal/whole/effort promotion')
    contract(p);labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('children-as-java',lambda v:v.update(tests=35)),('children-role',lambda v:v.update(nodeSubcasesNotAddedToJavaMethods=False)),('Java-qualification',lambda v:v.update(javaSourceProgramsQualified=4)),('Java-gate',lambda v:v.update(javaCoverageGate='PASS')),('missing-resource',lambda v:v.update(resourcePrograms=3)),('Browser',lambda v:v.update(actualBrowserActions=1)),('network',lambda v:v.update(actualNetworkActions=1)),('formal',lambda v:v.update(formalUpdated=True)),('acceptance',lambda v:v.update(newAccepted=1)),('effort',lambda v:v.update(effortPercent=25)),('environment',lambda v:v.update(reportedEnvironment={})),('outputs',lambda v:v.update(outputHashes={})),('coverage',lambda v:v['productionJavascriptResources']['operation-post-submit']['coverage'].update(branchPercent=99))]:
        bad=copy.deepcopy(p);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false resource receipt accepted '+label)
    sample=(POST/'target/pt-log-script/node.tap').read_text();tap_labels=[]
    for label,text in [('failure',sample.replace('# fail 0','# fail 1')),('skip',sample.replace('# skipped 0','# skipped 1')),('missing-case',sample.replace('ok 1 - ','missing 1 - ',1)),('line',sample.replace('100.00','99.99',1)),('wrong-file',sample.replace('log-search-validation.js','other.js'))]:
        try:tap_contract(text,'log-search-validation',8)
        except ValueError:tap_labels.append(label)
        else:raise ValueError('false TAP accepted '+label)
    require('invocation' not in raw and isinstance(raw['begin']['invocation'],dict),'raw invocation only in begin')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation)
    OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,rawSha256='5f4205513895cd2ea19ca369d5bffe6d1a752cc959a5ed04913a028ab247d7f8',postSha256=PIN,originalJavaMethods=5,originalJavaSuites=4,nodeChildCases=30,nodeChildrenNotAddedToJavaMethods=True,resources=resource_rows,javaSourceProgramsQualified=0,resourcePrograms=4,resourceLineFunctionBranch100=True,semanticNegativeVectors=len(labels),negativeLabels=labels,tapNegativeVectors=len(tap_labels),tapNegativeLabels=tap_labels,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
