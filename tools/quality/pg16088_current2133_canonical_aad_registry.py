"""Same-source two incomplete value units replaced by a complete new exec; all old cases retained."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16086_public_canonical_aad_eight_independent import SOURCE, POST, NAMES, FIXTURE, FIXTURE_SHA, require, read

PREV = ('PG16048-current2125-backup-request-registry-v1', '1481270818c601b5881b4f6e9fe55a9d4ac18e17e8a3698bf683161affdb71a9')
PREV_POST = ('PG16050-current2125-backup-request-registry-post-v1', '0ecbf93e058edbd4576a4234fd4d26843576e65acf007f9661847bd04a4359d9')
INDEPENDENT = ('PG16086-public-canonical-aad-eight-independent-v1', 'ebe1d1efaa5b89021a92e9d837bcaec0033446f57f59a8cc9169fcbb04c33f15')
OUT = data.BASE / 'PG16088-current2133-canonical-aad-registry-v1'

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation = capture(__file__)
    require(not OUT.exists(),'new-only')
    old,prior,p,q = [read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q))
            and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1]
            and (q['semanticNegativeVectors'],q['independentOracleNegativeVectors'])==(25,5),'qualified own source references')
    require(p['targetUnitFour100'] is True and p['singleSession'] is True and p['crcMismatch']==0
            and p['normalOrdinaryTestSourceDomain'] is False and set(p['fullSourceUnits'])==NAMES,'exact two value units')
    result = copy.deepcopy(old)
    before = {(r['classname'],r['name']) for r in old['cases']}
    added = {(r['classname'],r['name']) for r in p['cases']}
    require(len(added)==8 and not added & before and {c for c,n in added}=={'dev.codex.schubert.nk.api.idempotency.PublicCanonicalAadValueTest'},'eight new quality cases only')
    for name in sorted(NAMES):
        previous = old['fullSourceUnits'][name]
        unit = p['fullSourceUnits'][name]
        require(previous['physical']==unit['physical']==[name] and not previous['four100']
                and name not in old['qualificationReplacedUnitHistory'] and unit['four100'] is True,'exact old incomplete unit')
        for kind in ('LINE','METHOD','CLASS','BRANCH'):
            a,b=previous['counters'][kind],unit['totals'][kind]
            require(a['covered']+a['missed']==b['covered'] and b['missed']==0 and b['covered']>0,'same complete denominator')
        result['qualificationReplacedUnitHistory'][name]=copy.deepcopy(previous)
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=[name],
            counters=copy.deepcopy(unit['totals']),four100=True,execSha256=p['execSha256'],
            sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    require(all(path in old['owners'] and old['owners'][path]==row for path,row in p['owners'].items()),'same original owner/cost')
    ref=dict(post=list(POST),independentPost=list(INDEPENDENT),source=SOURCE,fixture=FIXTURE,fixtureSha256=FIXTURE_SHA,
        tests=8,newUniqueMethods=8,necessaryRepeatedMethods=0,normalOrdinaryTestSourceDomain=False,
        wholeSourcesReplaced=sorted(NAMES),countedInOriginalExecs=True,coverageExecUnion=False)
    result['valueFixtureQualificationReferences'].append(ref)
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=1,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope='NEW_PUBLIC_BYTE_VALUE_FIXTURE8_TWO_COMPLETE_SOURCES_NOT_NORMAL_DECLARATIONS'))
    cases=before|added;units=result['fullSourceUnits']
    four={c for u in units.values() if u['four100'] for c in u['physical']}
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),
        cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),
        suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,
        totalMethodExecutions=old['totalMethodExecutions']+8,uniqueProductMethodDelta=8,newTestIds=8,sourceProgramDelta=0,
        four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),
        four100ExecutablePhysical=len(four-result['metadataClasses'].keys()),
        incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()))
    require((result['tests'],result['suites'],len(units),result['measuredPhysical'],result['four100SourcePrograms'],
             len(four),result['four100ExecutablePhysical'],result['incompleteSourcePrograms'],
             result['totalProductExecs'],result['totalMethodExecutions'],result['totalRepeatedOriginalMethods'])==
             (2133,285,477,662,258,376,365,37,128,2265,132),'exact technical counts not effort')
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json'])
    keys={(v['className'],v['method']) for v in bindings}
    require(len(cases&keys)==2116 and len(cases-keys)==17 and not added&keys,'ordinary 2116 unchanged, fixtures9+8')
    decl.update(existingQualityFixtureCases=17);result['currentOrdinaryTestDeclarationReference']=decl
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites',
        'originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta',
        'four100SourcePrograms','four100Physical','four100ExecutablePhysical','incompleteSourcePrograms','fullSourceUnits',
        'qualificationReplacedUnitHistory','originalPostReferences','currentOrdinaryTestDeclarationReference','valueFixtureQualificationReferences'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed)
            and all(result['fullSourceUnits'][n]==u for n,u in old['fullSourceUnits'].items() if n not in NAMES)
            and all(result['qualificationReplacedUnitHistory'][n]==u for n,u in old['qualificationReplacedUnitHistory'].items())
            and result['valueFixtureQualificationReferences'][:-1]==old['valueFixtureQualificationReferences'],'all old histories corrections costs preserved')
    require(result['ownerStatusCounts']==dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),'owners preserved')
    for v in (old,prior,p,q):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result)
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
