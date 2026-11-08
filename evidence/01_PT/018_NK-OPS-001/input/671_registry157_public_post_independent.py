"""Reverse public-post to source-declaration comparison. Metadata only, no runtime or original test replay."""
from pathlib import Path
from collections import Counter
import copy
import datetime
import hashlib
import json

B=Path('evidence/01_PT/018_NK-OPS-001')
C=B/'input/668_registry157_public_post_scope.json'
P=B/'evidence/PG24198-registry157-public77-post-bindings-v1'
O=B/'evidence/PG24200-registry157-public77-post-independent-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def changed_metadata(before,after):
    return json.dumps(before,sort_keys=True,separators=(',',':'))!=json.dumps(after,sort_keys=True,separators=(',',':'))


def verify(source_rows,post_rows,declared,posts,current,pins):
    assert len(source_rows)==157 and len({r['mainPath'] for r in source_rows})==157
    assert len(post_rows)==77 and len({r['postName'] for r in post_rows})==77
    by_path={r['mainPath']:r for r in source_rows};by_post={r['postName']:r for r in post_rows}
    assert set(by_path)=={r['mainPath'] for r in declared} and set(by_post)==set(posts)
    for name,m in posts.items():
        r=by_post[name];pin=pins[name]
        assert r['sha256']==pin['sha256'] and r['path']==pin['path']
        assert r['historicalSource']==m['source']
        assert type(r['originalExit']) is type(m['actualExit']) and r['originalExit']==m['actualExit']
        assert r['exitIsIntegerZero'] is (type(m['actualExit']) is int and m['actualExit']==0)
        assert r['originalSessionReferenceMatches'] is (m.get('sessionIdentity')==pin['originalSessionIdentity'])
        assert r['originalExecReferenceMatches'] is (m.get('execSha256')==pin['originalExecSha256'])
        cases=m.get('cases')
        expected='UNSUPPORTED_CASE_SCHEMA'
        if type(cases) is list and cases and all(type(v) is dict and v.get('result')=='PASS' and v.get('nonPass')==[] for v in cases):expected='PASS_METADATA_ONLY'
        elif type(cases) is list and any(type(v) is dict and v.get('result') not in [None,'PASS'] for v in cases):expected='NON_PASS_REPORTED'
        assert r['historicalCaseState']==expected
        assert r['historicalCaseRows']==(len(cases) if type(cases) is list else None)
        assert r['historicalReferenceOnly'] is True and r['currentRunQualified'] is False
        targets=[d for d in declared if d['declaredPostReference']['postName']==name]
        for d in targets:
            row=by_path[d['mainPath']]
            assert row['postName']==name and row['historicalPostSource']==m['source']
            assert row['historicalReferenceOnly'] is True and row['currentRunQualified'] is False and row['newAcceptance']==0
            unit_keys=[key for key,value in m['fullSourceUnits'].items() if sorted(value['physical'])==sorted(d['registryPhysical'])]
            assert len(unit_keys)==1
            expected_counters=m['fullSourceUnits'][unit_keys[0]]['totals']
            assert row['originalUnitRoot']==unit_keys[0] and row['historicalCounters']==expected_counters==d['originalCounters']
            assert row['counterReferenceState']=='DECLARED_COUNTERS_MATCH_PINNED_POST'
            descriptor=[v for v in current if v['sourcePath']==d['mainPath']]
            names=sorted(v['physicalKey'].split(':',1)[1][:-6] for v in descriptor)
            assert names==row['currentPhysicalNames']==sorted(d['registryPhysical'])
            assert row['originalPhysicalNames']==d['registryPhysical']
            assert all(v['classSha256'] is not None for v in descriptor)
            same=all(m['physicalClasses'][v['physicalKey'].split(':',1)[1][:-6]]==v['classSha256'] for v in descriptor)
            assert row['currentByteState']==('EXACT_CURRENT_PHYSICAL_BYTES' if same else 'DIFFERENT_CURRENT_PHYSICAL_BYTES')
            expected_ref='MATCH' if r['originalSessionReferenceMatches'] and r['originalExecReferenceMatches'] else 'SOURCE_RUN_REFERENCE_MISMATCH'
            assert row['runReferenceState']==expected_ref
            assert row['sourceDeclarationStatus']==d['status'] and row['originalDeclaredCounterKind']==d['declaredOriginalCounterKind']
            assert row['currentSourceDeclarationHashMatches'] is d['registryAndCurrentSourceHashEqual']
            assert row['currentPhysicalDeclarationNamesMatch'] is d['completePhysicalNamesEqual']


assert not O.exists()
c=load(C);m=load(P/'manifest.json')
for key in ['assessment','currentMethodMetadata']:assert sha(Path(c[key]['path']))==c[key]['sha256']
for name,pin in m['files'].items():assert sha(P/name)==pin
all_rows=load(Path(c['assessment']['path']));declared=[r for r in all_rows if r['declaredPostReference'] and r['declaredPostReference']['postName']!=c['excludedAlreadyBoundPost']]
current=load(Path(c['currentMethodMetadata']['path']));pins={r['postName']:r for r in c['publicPostPins']};posts={}
for name,ref in pins.items():
    path=Path(ref['path']);assert path.as_posix().startswith('evidence/01_PT/018_NK-OPS-001/evidence/provisional/') and path.name=='manifest.json'
    assert sha(path)==ref['sha256'];posts[name]=load(path)
source_rows=load(P/'source-reference-bindings.json');post_rows=load(P/'public-post-bindings.json')
verify(source_rows,post_rows,declared,posts,current,pins)
negatives=[]
for before,after in [(0,False),(1,True),(0,0.0),({'a':0},{'a':False})]:
    assert changed_metadata(before,after)
assert not changed_metadata({'a':0,'b':False},{'b':False,'a':0})
for label,mutate in [('source-missing',lambda s,p:s.pop()),('source-duplicate',lambda s,p:s.__setitem__(0,copy.deepcopy(s[1]))),
                       ('post-missing',lambda s,p:p.pop()),('fake-current-run',lambda s,p:s[0].update(currentRunQualified=True)),
                       ('counter-gap',lambda s,p:s[0]['historicalCounters']['LINE'].update(missed=1)),
                       ('counter-covered',lambda s,p:s[0]['historicalCounters']['METHOD'].update(covered=99999)),
                       ('byte-mismatch-hidden',lambda s,p:next(r for r in s if r['currentByteState']=='DIFFERENT_CURRENT_PHYSICAL_BYTES').update(currentByteState='EXACT_CURRENT_PHYSICAL_BYTES')),
                       ('unknown-case-as-pass',lambda s,p:next(r for r in p if r['historicalCaseState']=='UNSUPPORTED_CASE_SCHEMA').update(historicalCaseState='PASS_METADATA_ONLY')),
                       ('run-mismatch-hidden',lambda s,p:next(r for r in s if r['runReferenceState']!='MATCH').update(runReferenceState='MATCH')),
                       ('post-original-source-rewritten',lambda s,p:p[0].update(historicalSource=c['source'])),
                       ('post-original-exit-type',lambda s,p:p[0].update(originalExit=False)),
                       ('case-count',lambda s,p:p[0].update(historicalCaseRows=999999)),
                       ('post-fake-runtime',lambda s,p:p[0].update(currentRunQualified=True))]:
    a,b=copy.deepcopy(source_rows),copy.deepcopy(post_rows);mutate(a,b);assert changed_metadata((source_rows,post_rows),(a,b))
    try:verify(a,b,declared,posts,current,pins)
    except AssertionError:negatives.append(label)
    else:raise AssertionError(label)
O.mkdir()
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=c['source'],producerManifest={'path':str(P/'manifest.json'),'sha256':sha(P/'manifest.json')},sourceDeclarations=157,publicPostManifests=77,sourceCounterReferenceStates=dict(Counter(r['counterReferenceState'] for r in source_rows)),currentClassByteStates=dict(Counter(r['currentByteState'] for r in source_rows)),sourceRunReferenceStates=dict(Counter(r['runReferenceState'] for r in source_rows)),postCaseSchemaStates=dict(Counter(r['historicalCaseState'] for r in post_rows)),metadataNegativeChecks=negatives,metadataReferenceQualificationOnly=True,alreadyBound15460Reread=False,sourceIdentityRecomputed=False,originalXmlExecArchiveClassByteRead=False,privateRuntimeEvidenceRead=False,historicalReferenceOnly=True,currentRunQualified=False,individualMethodFilterOrOracleIndependentlyVerified=False,wholeWbsAccepted=False,compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sourceDeclarations=157,publicPosts=77,metadataNegatives=len(negatives),manifestSha256=sha(O/'manifest.json'))))
