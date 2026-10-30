"""Independently reconstruct unique cases, actual Source replacements and single-exec history."""
import copy
from collections import Counter
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,PREV,PREV_POST,JOINT,JOINT_POST,REPLACED,read,require

PIN='aa7344e8b7996e235239ca529c71b523b3f2d1bcf155ce49ffe38ebc48ebb33c'
OUT=data.BASE/'PG14752-current860-joint-registry-post-v1'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only joint registry post')
    old,prior,p,proof,m=[read(v) for v in [PREV,PREV_POST,JOINT,JOINT_POST,('PG14750-current860-joint-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof,m]),'all genuine current source references')
    require(prior['registryManifestSha256']==PREV[1] and proof['postSha256']==JOINT[1] and proof['semanticNegativeVectors']==18 and proof['rawInvocationRoleNegativeVectors']==4,'actual independent prior/joint qualifications')
    local=[]
    for filename,pin in p['xmlHashes'].items():
        raw=(data.BASE/JOINT[0]/filename).read_bytes();require(data.sha(raw)==pin,'actual returned original XML hash')
        tree=ET.fromstring(raw);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all XML cases and FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'non-PASS forbidden');local.append((case.get('classname'),case.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']};new=set(local)-old_cases;repeated=set(local)&old_cases;cases=old_cases|set(local)
    require(len(local)==len(set(local))==34 and len(new)==18 and len(repeated)==16 and len({c for c,n in local})==5,'actual unique34/new18/necessary16')
    require(new=={(v['classname'],v['name']) for v in proof['newCases']} and repeated=={(v['classname'],v['name']) for v in proof['repeatedCases']},'independent actual overlap identity')
    expected=copy.deepcopy(old);units=expected['fullSourceUnits'];history={n:copy.deepcopy(units[n]) for n in REPLACED}
    require(set(units)&set(p['fullSourceUnits'])==REPLACED and p['singleSession'] is True and p['crcMismatch']==0 and p['forbiddenProductProbeHits']==0,'only two Request proofs replaced by one CRC-verified exec')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==[name] and set(u['totals'])=={'LINE','METHOD','CLASS','BRANCH'},'actual whole one-class Source')
        measured={k:dict(covered=p['executable'][name]['counters'][k]['covered'],missed=p['executable'][name]['counters'][k]['missed']) for k in u['totals']}
        require(wire(measured)==wire(u['totals']),'Source totals bound to actual measured executable counters')
        four=all(v['covered']>0 and v['missed']==0 for v in measured.values());require(u['four100'] is four,'actual four counters')
        if name in REPLACED:require(not history[name]['four100'] and four and history[name]['physical']==u['physical'],'only strictly full current proof replaces old incomplete one')
        units[name]=dict(post=JOINT[0],postSha256=JOINT[1],physical=u['physical'],counters=measured,four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    for path,value in p['owners'].items():
        require(path not in expected['owners'] or expected['owners'][path]==value,'shared known/candidate/UNKNOWN owner unchanged');expected['owners'][path]=value
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=expected['metadataClasses']
    expected['originalPostReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],tests=34,suites=5,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='JOINT_ORIGINAL18_AND_NECESSARY_QUALIFICATION16_NOT_WHOLE_451'))
    reference=dict(post=list(JOINT),independentPost=list(JOINT_POST),originalMethods=34,newUniqueMethods=18,necessaryRepeatedMethods=16,originalProductJvms=1,countedInOriginalExecs=True,coverageExecUnion=False,purpose='CURRENT_REQUEST_QUERY_METHOD_COMPLETE_SOURCE_CLOSURE')
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(local),uniqueProductMethodDelta=len(new),sourceProgramDelta=len(units)-len(old['fullSourceUnits']),jointQualificationReferences=[reference],jointQualificationReplacedUnitHistory=history,necessaryJointRepeatedMethods=len(repeated),totalRepeatedOriginalMethods=old['totalMethodExecutions']-old['tests']+len(repeated))
    def contract(v):require(wire(v)==wire(expected),'all independently derived counts, Source proofs and histories')
    contract(m)
    require((m['tests'],m['suites'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(860,121,208,279,129,194,53,932,72),'observed exact unique/exec/physical accounting')
    require(all(units[n]==v for n,v in old['fullSourceUnits'].items() if n not in REPLACED) and m['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'] and m['additionalQualificationReferences']==old['additionalQualificationReferences'],'all other and Catalog proofs retained')
    vectors=[('new-as-all34','tests',876),('repeat-erased','necessaryJointRepeatedMethods',0),('repeat-inflated','totalRepeatedOriginalMethods',90),('JVM-double','totalProductExecs',54),('original-JVM-double','originalExecs',53),('method-exec','totalMethodExecutions',916),('history-erased','jointQualificationReplacedUnitHistory',{}),('joint-proof-erased','jointQualificationReferences',[]),('Catalog-history','qualificationReplacedUnitHistory',{}),('Catalog-proof','additionalQualificationReferences',[]),('physical','measuredPhysical',278),('four-physical','four100Physical',193),('four-code','four100ExecutablePhysical',183),('pending-erased','incompleteSourcePrograms',0),('unknown-erased','unknownOwnerPaths',0),('old-transfer','priorSource0061TestsTransferred',True),('union','coverageExecUnion',True),('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',50),('bool','originalTestsReexecutedByRegistry',False)]
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false joint registry accepted '+label)
    keys=['tests','suites','originalExecs','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','generatedMetadataPhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','metadataSourcePrograms','incompleteSourcePrograms','unknownOwnerPaths','ownerStatusCounts','additionalQualificationExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','sourceProgramDelta','necessaryJointRepeatedMethods','totalRepeatedOriginalMethods']
    for value in [old,prior,p,proof,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,jointPostSha256=JOINT[1],jointIndependentSha256=JOINT_POST[1],summary={k:m[k] for k in keys},metadataNegativeVectors=len(labels),negativeLabels=labels,allOldCasesAndUnrelatedProofsPreserved=True,singleExecRequestReplacements=2,newRepositorySourceScopes=2,necessaryRepeatMethods=16,originalMethodsReexecutedByRegistry=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
