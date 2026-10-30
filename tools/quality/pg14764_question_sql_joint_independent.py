"""Independent18/new10/repeat8, whole Question Request and true-noCode mapper closure."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg14760_question_sql_joint_eighteen_pt as original

OUT=data.BASE/'PG14764-question-sql-joint-independent-v1'
PIN='9653028e361d41a2b0793e485797ff93c00c4500acf9a06249a54c2f1179c84e'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def raw_invocation(value):
    require(isinstance(value,dict) and 'invocation' not in value and isinstance(value.get('begin'),dict) and isinstance(value['begin'].get('invocation'),dict),'raw invocation only in begin')
    verify(value['begin']['invocation'])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent Question post')
    p=data.read_checked(data.BASE/'PG14762-question-sql-joint-eighteen-post-v1/manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14760-question-sql-joint-eighteen-pt-v1/manifest.json','d5d823d884167cb19f9c7c5124d3fe39d152cf6cab309059b54f13a98b212327')
    prior=data.read_checked(data.BASE/'PG14750-current860-joint-registry-v1/manifest.json','aa7344e8b7996e235239ca529c71b523b3f2d1bcf155ce49ffe38ebc48ebb33c')
    require(all(v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,prior]),'genuine same source references')
    declarations=set()
    for name,path in original.TESTS.items():
        text=path.read_text();require(data.sha(path.read_bytes())==original.PINS[name],'frozen whole Test source')
        package=re.search(r'^package ([A-Za-z0-9_.]+);',text).group(1);methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text)
        require(len(methods)==original.COUNTS[name],'whole original method count');declarations.update((package+'.'+name,m) for m in methods)
    actual=[]
    for filename,digest in p['xmlHashes'].items():
        value=(data.BASE/'PG14762-question-sql-joint-eighteen-post-v1'/filename).read_bytes();require(data.sha(value)==digest,'returned XML hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all actual XML cases/FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'non-PASS forbidden');actual.append((case.get('classname'),case.get('name')))
    old={(v['classname'],v['name']) for v in prior['cases']};current=set(actual);new=current-old;repeated=current&old
    require(len(actual)==len(current)==18 and len({c for c,n in current})==2 and current==declarations=={(v['classname'],v['name']) for v in raw['cases']},'all original18 exact declarations/XML')
    require(len(new)==10 and len(repeated)==8 and all(c.endswith('.QuestionSqlContractTest') for c,n in new) and all(c.endswith('.QuestionQueryPlainContractTest') for c,n in repeated),'actual new10/necessary8')
    request='dev/codex/schubert/nk/api/application/question/QuestionQueryRequest';repo='dev/codex/schubert/nk/api/persistence/QuestionQueryRepository';mapper=repo+'$RowMapper'
    require(set(p['fullSourceUnits'])=={request,repo} and set(p['physicalClasses'])=={request,repo,mapper} and p['metadataClasses']==[mapper],'all two Source/three physical closures')
    metadata=p['sourcePhysicalInventory'][mapper]
    require(metadata==dict(sha256='64041f2bfa092b6440952bd1bfcbc9794ecceca64017d3288df8f04264ae63b9',flags=1536,sourceFile='QuestionQueryRepository.java',methods=[dict(name='read',descriptor='(Ljava/sql/ResultSet;)Ljava/lang/Object;',flags=1025,hasCode=False,codeLength=0)]),'true private abstract noCode, not a filtered executable')
    require(p['fullSourceUnits'][request]['four100'] is True and p['fullSourceUnits'][repo]['four100'] is False and p['fullSourceUnits'][repo]['physical']==[repo,mapper] and set(p['executable'])=={request,repo},'Request complete, Repo incomplete with included noCode interface')
    slot=data.ROOT.parent/'pgpt-runs/PG379/pg14762-question-sql-joint-eighteen-post-v1'
    require(len(p['stages'])==5 and all(s['actualExit']==0 and s['timedOut'] is False for s in p['stages']),'all own tool stages actual0')
    require((slot/'held-probe-self-test.stdout').read_text().strip()=='TOOL_METADATA_CHECKS=10' and (slot/'held-probe-audit.stdout').read_text().strip()=='FORBIDDEN_PROBE_HITS=0','actual held4 probe0/tool10metadata')
    expected={k:p[k] for k in ['source','tests','suites','cases','xmlHashes','execSha256','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','physicalClasses','executable','totals','owners','reportedEnvironment','sessionIdentity','crcMismatch','metadataClasses','metadataKind']}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in expected.items()),'verified actual counters/whole closure/environment/owner/XML fixed')
        require(v['tests']==18 and v['newCurrentSourceOriginalMethods']==10 and v['necessaryPreviouslyCountedOriginalMethods']==8,'method roles, not all new')
        require(v['onlyReviewedPureValueSuites'] is False and v['onlyReviewedPublicJdbcInterfaceContracts'] is True and v['backendReceiverConstructed'] is True and v['actualJdbcBackendConnected'] is False,'real repository interface, no real backend')
        require(type(v['forbiddenProductProbeHits']) is int and v['forbiddenProductProbeHits']==0 and v['heldProbeToolMetadataChecks']==10,'actual held-probe0 and tool metadata')
        require(v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True and v['oldCoverageTransferred'] is v['priorProductResultsReused'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['formalUpdated'] is False and v['effortPercent'] is None,'no exclusion/old/whole/formal promotion')
        require(v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False,'incomplete Repo not passed')
    contract(p);labels=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('all-as-new',lambda v:v.update(newCurrentSourceOriginalMethods=18)),('repeat-erased',lambda v:v.update(necessaryPreviouslyCountedOriginalMethods=0)),('mapper-erased',lambda v:v.update(metadataClasses=[])),('mapper-code-faked',lambda v:v['sourcePhysicalInventory'][mapper]['methods'][0].update(hasCode=True)),('whole-closure',lambda v:v.update(completeSourceUnitClosure={})),('natural-noCode-as-tested',lambda v:v.update(metadataKind='FOUR100')),('probe1',lambda v:v.update(forbiddenProductProbeHits=1)),('probe-bool',lambda v:v.update(forbiddenProductProbeHits=False)),('backend',lambda v:v.update(actualJdbcBackendConnected=True)),('pure-label',lambda v:v.update(onlyReviewedPureValueSuites=True)),('XML',lambda v:v.update(xmlHashes={})),('environment',lambda v:v.update(reportedEnvironment={})),('request-incomplete',lambda v:v['fullSourceUnits'][request].update(four100=False)),('repo-passed',lambda v:v['fullSourceUnits'][repo].update(four100=True)),('old',lambda v:v.update(oldCoverageTransferred=True)),('exclusion',lambda v:v.update(manualCounterExclusions=[mapper])),('formal',lambda v:v.update(formalUpdated=True)),('effort',lambda v:v.update(effortPercent=50)),('strict',lambda v:v.update(strictFour100GateExit=0))]:
        bad=copy.deepcopy(p);change(bad)
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false Question post accepted '+label)
    raw_invocation(raw);role_labels=[]
    for label,change in [('missing',lambda v:v['begin'].pop('invocation')),('moved',lambda v:v.update(invocation=v['begin'].pop('invocation'))),('ambiguous',lambda v:v.update(invocation=v['begin']['invocation'])),('wrong-type',lambda v:v.update(begin=None))]:
        bad=copy.deepcopy(raw);change(bad)
        try:raw_invocation(bad)
        except ValueError:role_labels.append(label)
        else:raise ValueError('wrong raw role accepted')
    for v in [p,prior]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,rawSha256='d5d823d884167cb19f9c7c5124d3fe39d152cf6cab309059b54f13a98b212327',previousRegistrySha256='aa7344e8b7996e235239ca529c71b523b3f2d1bcf155ce49ffe38ebc48ebb33c',originalXmlMethods=18,originalXmlSuites=2,newUniqueMethods=10,necessaryRepeatedMethods=8,newCases=[dict(classname=c,name=n) for c,n in sorted(new)],repeatedCases=[dict(classname=c,name=n) for c,n in sorted(repeated)],fullRequestSourcePrograms=[request],incompleteRepositorySourcePrograms=[repo],trueNoCodeMetadata={mapper:metadata},forbiddenProductProbeHits=0,heldProbeToolMetadataChecks=10,semanticNegativeVectors=len(labels),negativeLabels=labels,rawInvocationRoleNegativeVectors=len(role_labels),rawInvocationRoleNegativeLabels=role_labels,coverageExecUnion=False,oldSourceTransferred=False,productTestsReexecutedByPost=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
