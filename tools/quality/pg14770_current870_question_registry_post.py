"""Independent controlled Question replacement, exact new10/repeat8, metadata and old histories."""
import copy
from collections import Counter
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14768_current870_question_registry import SOURCE,PREV,PREV_POST,JOINT,JOINT_POST,REQUEST,REPO,MAPPER,read,require

PIN='fe795c59b97c818fdfceaef5963586a28439143f87b782ede4c74375b83fa814'
OUT=data.BASE/'PG14770-current870-question-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only Question registry post')
    old,prior,p,proof,m=[read(v) for v in [PREV,PREV_POST,JOINT,JOINT_POST,('PG14768-current870-question-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof,m]),'all same current source actual witnesses')
    require(prior['registryManifestSha256']==PREV[1] and proof['postSha256']==JOINT[1] and proof['semanticNegativeVectors']==20 and proof['rawInvocationRoleNegativeVectors']==4,'independent prior and new qualified scope')
    local=[]
    for filename,h in p['xmlHashes'].items():
        value=(data.BASE/JOINT[0]/filename).read_bytes();require(data.sha(value)==h,'actual returned original XML hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'exact XML/FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'non-PASS forbidden');local.append((case.get('classname'),case.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']};new=set(local)-old_cases;repeated=set(local)&old_cases;cases=old_cases|set(local)
    require(len(local)==len(set(local))==18 and len(new)==10 and len(repeated)==8 and new=={(v['classname'],v['name']) for v in proof['newCases']} and repeated=={(v['classname'],v['name']) for v in proof['repeatedCases']},'actual new10/necessary repeat8 without duplicate newcredit')
    expected=copy.deepcopy(old);units=expected['fullSourceUnits'];old_request=copy.deepcopy(units[REQUEST]);require(not old_request['four100'] and set(units)&set(p['fullSourceUnits'])=={REQUEST} and p['singleSession'] is True and p['crcMismatch']==0,'one declared incomplete Request replacement from one exec')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==([REQUEST] if name==REQUEST else [REPO,MAPPER]),'whole Source closure includes noCode mapper')
        counters={k:dict(covered=sum(p['executable'][n]['counters'][k]['covered'] for n in u['physical'] if n in p['executable']),missed=sum(p['executable'][n]['counters'][k]['missed'] for n in u['physical'] if n in p['executable'])) for k in ['LINE','METHOD','CLASS','BRANCH']}
        require(wire(counters)==wire(u['totals']),'actual executable counter sum, noCode has no invented hit')
        four=all(v['covered']>0 and v['missed']==0 for v in counters.values());require(u['four100'] is four and (name!=REQUEST or four),'Request truly complete')
        units[name]=dict(post=JOINT[0],postSha256=JOINT[1],physical=u['physical'],counters=counters,four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    info=p['sourcePhysicalInventory'][MAPPER]
    require(info==proof['trueNoCodeMetadata'][MAPPER] and info==dict(sha256='64041f2bfa092b6440952bd1bfcbc9794ecceca64017d3288df8f04264ae63b9',flags=1536,sourceFile='QuestionQueryRepository.java',methods=[dict(name='read',descriptor='(Ljava/sql/ResultSet;)Ljava/lang/Object;',flags=1025,hasCode=False,codeLength=0)]) and p['metadataClasses']==[MAPPER],'exact true abstract noCode, not generated executable')
    require(MAPPER not in expected['metadataClasses'],'not already accounted metadata');expected['metadataClasses'][MAPPER]=dict(kind='NO_CODE',sha256=info['sha256'],postSha256=JOINT[1])
    for path,owned in p['owners'].items():
        require(path not in expected['owners'] or expected['owners'][path]==owned,'shared owners unchanged');expected['owners'][path]=owned
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=expected['metadataClasses']
    expected['originalPostReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],tests=18,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='JOINT_ORIGINAL10_AND_NECESSARY_QUALIFICATION8_NOT_WHOLE_451'))
    expected['jointQualificationReferences'].append(dict(post=list(JOINT),independentPost=list(JOINT_POST),originalMethods=18,newUniqueMethods=10,necessaryRepeatedMethods=8,originalProductJvms=1,countedInOriginalExecs=True,coverageExecUnion=False,purpose='CURRENT_QUESTION_REQUEST_QUERY_METHOD_COMPLETE_SOURCE_CLOSURE'))
    expected['jointQualificationReplacedUnitHistory'][REQUEST]=old_request
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(local),uniqueProductMethodDelta=len(new),sourceProgramDelta=len(units)-len(old['fullSourceUnits']),necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods']+len(repeated),totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods']+len(repeated))
    def contract(value):require(wire(value)==wire(expected),'all independently derived cases/proofs/history/counts')
    contract(m)
    require((m['tests'],m['suites'],len(units),len(physical),m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(870,122,209,281,12,130,195,54,950,80),'observed exact counts')
    vectors=[('all18-as-new','tests',878),('repeat-erased','necessaryJointRepeatedMethods',16),('total-repeat-erased','totalRepeatedOriginalMethods',72),('method-exec','totalMethodExecutions',942),('JVM-double','totalProductExecs',55),('joint-erased','jointQualificationReferences',[]),('joint-overwritten','jointQualificationReferences',[m['jointQualificationReferences'][-1]]),('old-history-erased','jointQualificationReplacedUnitHistory',{REQUEST:old_request}),('Catalog-erased','qualificationReplacedUnitHistory',{}),('metadata-erased','metadataClasses',old['metadataClasses']),('noCode-count','metadataPhysical',11),('code-count','executablePhysical',270),('four-physical','four100Physical',194),('pending-erased','incompleteSourcePrograms',0),('unknown-erased','unknownOwnerPaths',0),('old-transfer','priorSource0061TestsTransferred',True),('union','coverageExecUnion',True),('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',50),('bool','originalTestsReexecutedByRegistry',False)]
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false Question registry accepted '+label)
    keys=['tests','suites','originalExecs','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','generatedMetadataPhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','metadataSourcePrograms','incompleteSourcePrograms','unknownOwnerPaths','ownerStatusCounts','additionalQualificationExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','sourceProgramDelta','necessaryJointRepeatedMethods','totalRepeatedOriginalMethods']
    for value in [old,prior,p,proof,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,jointPostSha256=JOINT[1],jointIndependentSha256=JOINT_POST[1],summary={k:m[k] for k in keys},metadataNegativeVectors=len(labels),negativeLabels=labels,allOldCasesAndUnrelatedProofsPreserved=True,singleExecRequestReplacements=1,newRepositorySourceScopes=1,newTrueNoCodeMetadata=1,necessaryRepeatMethods=8,originalMethodsReexecutedByRegistry=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
