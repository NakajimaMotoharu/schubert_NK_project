"""Independent exact delta/case/history reconstruction; no Product or old successful tools executed."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16088_current2133_canonical_aad_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, NAMES, FIXTURE, FIXTURE_SHA, require, read

PIN = 'b6e7dc918a723fd30965322bc8400e51a786872204ea72a99f3e9b18534e30b7'
OUT = data.BASE / 'PG16090-current2133-canonical-aad-registry-post-v1'

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation = capture(__file__)
    require(not OUT.exists(),'new-only')
    old,prior,p,q,current=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT,('PG16088-current2133-canonical-aad-registry-v1',PIN))]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q,current))
            and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1]
            and (q['semanticNegativeVectors'],q['independentOracleNegativeVectors'])==(25,5),'exact qualified chain')
    local=[]
    for file,h in p['xmlHashes'].items():
        raw=(data.BASE/POST[0]/file).read_bytes();require(data.sha(raw)==h,'XML hash')
        root=ET.fromstring(raw);require(all(root.get(k)=='0' for k in ('failures','errors','skipped')),'all8 pass')
        for node in root.findall('testcase'):
            require(not list(node),'not failed/skipped');local.append((node.get('classname'),node.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']}
    require(len(local)==len(set(local))==8 and not set(local)&old_cases,'only8 new cases')
    expected=copy.deepcopy(old);expected['invocation']=current['invocation']
    expected['previousUniqueRegistryReference']=list(PREV);expected['previousRegistryPostReference']=list(PREV_POST)
    cases=old_cases|set(local)
    expected['cases']=[dict(classname=c,name=n) for c,n in sorted(cases)]
    expected['suiteNames']=sorted({c for c,n in cases})
    for key,amount in [('tests',8),('suites',1),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',8),
                       ('four100SourcePrograms',2),('four100Physical',2),('four100ExecutablePhysical',2),('incompleteSourcePrograms',-2)]:
        expected[key]=old[key]+amount
    expected.update(uniqueProductMethodDelta=8,newTestIds=8,sourceProgramDelta=0)
    for name in NAMES:
        before=old['fullSourceUnits'][name];measured=p['fullSourceUnits'][name]
        require(before['physical']==measured['physical']==[name] and before['four100'] is False and name not in old['qualificationReplacedUnitHistory'],'old exact partial Source')
        counters=measured['totals']
        require(counters==p['executable'][name]['counters'] and all(type(c[k]) is int and c['missed']==0 and c['covered']>0 for c in counters.values() for k in ('covered','missed')),'strict counter')
        require(all(counters[k]['covered']==sum(before['counters'][k].values()) for k in counters),'same denominator')
        expected['qualificationReplacedUnitHistory'][name]=copy.deepcopy(before)
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=[name],counters=copy.deepcopy(counters),
            four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    expected['valueFixtureQualificationReferences'].append(dict(post=list(POST),independentPost=list(INDEPENDENT),source=SOURCE,
        fixture=FIXTURE,fixtureSha256=FIXTURE_SHA,tests=8,newUniqueMethods=8,necessaryRepeatedMethods=0,
        normalOrdinaryTestSourceDomain=False,wholeSourcesReplaced=sorted(NAMES),countedInOriginalExecs=True,coverageExecUnion=False))
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=1,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope='NEW_PUBLIC_BYTE_VALUE_FIXTURE8_TWO_COMPLETE_SOURCES_NOT_NORMAL_DECLARATIONS'))
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);decl['existingQualityFixtureCases']=17
    expected['currentOrdinaryTestDeclarationReference']=decl
    require((expected['tests'],expected['suites'],expected['four100SourcePrograms'],expected['four100Physical'],
             expected['incompleteSourcePrograms'],expected['totalProductExecs'],expected['totalMethodExecutions'])==
             (2133,285,258,376,37,128,2265),'finite technical count increments')
    def contract(v):
        require(wire(v)==wire(expected),'all exact delta/old fields/corrections/domain/history')
    contract(current)
    vectors=[('tests','tests',2125),('Source-added','sourceProgramDelta',2),('physical-added','measuredPhysical',664),
        ('four-erased','four100SourcePrograms',256),('four-double','four100Physical',378),('code','four100ExecutablePhysical',363),
        ('pending','incompleteSourcePrograms',0),('JVM','totalProductExecs',129),('methods','totalMethodExecutions',2273),
        ('repeat','totalRepeatedOriginalMethods',140),('history','qualificationReplacedUnitHistory',{}),
        ('joint-history','jointQualificationReplacedUnitHistory',{}),('joint-reference','jointQualificationReferences',[]),
        ('fixture-reference','valueFixtureQualificationReferences',[]),('Catalog','additionalQualificationReferences',[]),
        ('disclosure','postDisclosureCorrections',{}),('resource','resourceOnlyReferences',[]),('JS','javascriptResourceDomain',{}),
        ('owners','owners',{}),('natural','naturalZeroBranchSourcePrograms',178),('NoCode','metadataPhysical',0),
        ('unique','uniqueProductMethodDelta',0),('bool','newTestIds',True),('transfer','priorSource0061TestsTransferred',True),
        ('union','coverageExecUnion',True),('formal','formalUpdated',True),('accepted','newAccepted',1),
        ('effort','effortPercent',100),('cases','cases',old['cases']),('units','fullSourceUnits',old['fullSourceUnits'])]
    labels=[]
    for label,key,value in vectors:
        bad=copy.deepcopy(current);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false registry accepted '+label)
    for key,value in [('ordinaryCaseReferences',2124),('existingQualityFixtureCases',9),('ordinaryWithoutCurrentCaseReference',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(current);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('quality fixtures mixed with ordinary declarations')
    require(len(labels)==34,'finite34 metadata checks')
    for v in (old,prior,p,q,current):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,
        summary={k:current[k] for k in prior['summary']},metadataNegativeVectors=34,negativeLabels=labels,
        newSourcePrograms=0,twoSourcesReplaced=sorted(NAMES),originalMethodsReexecutedByRegistry=0,
        currentOrdinaryTestDeclarationReference=decl,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
