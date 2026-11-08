"""Fixed public JSON post binding only. No private evidence, bytecode, tests, runtime or backend operations."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re

B=Path('evidence/01_PT/018_NK-OPS-001')
C=B/'input/668_registry157_public_post_scope.json'
O=B/'evidence/PG24198-registry157-public77-post-bindings-v1'
sha=lambda data:hashlib.sha256(data).hexdigest()
load=lambda p:json.loads(p.read_bytes())


def counter_shape(value):
    return (type(value) is dict and set(value)=={'LINE','METHOD','CLASS','BRANCH'}
            and all(type(v) is dict and set(v)=={'covered','missed'}
                    and all(type(x) is int and x>=0 for x in v.values()) for v in value.values()))


def row_assessment(row,post,current):
    physical=row['registryPhysical']
    candidates=[]
    units=post.get('fullSourceUnits')
    if type(units) is dict and type(physical) is list:
        for name,unit in units.items():
            if type(unit) is dict and type(unit.get('physical')) is list and sorted(unit['physical'])==sorted(physical):
                candidates.append((name,unit))
    root,unit=candidates[0] if len(candidates)==1 else (None,None)
    totals=unit.get('totals') if unit is not None else None
    if not counter_shape(totals):
        counter_state='UNSUPPORTED_OR_NO_EXACT_PHYSICAL_UNIT'
        totals=None
    elif totals!=row['originalCounters']:
        counter_state='DECLARED_COUNTERS_DIFFER_FROM_PINNED_POST'
    else:
        counter_state='DECLARED_COUNTERS_MATCH_PINNED_POST'
    now=[v for v in current if v['sourcePath']==row['mainPath']]
    names={v['physicalKey'].split(':',1)[1].removesuffix('.class') for v in now}
    hashes=post.get('physicalClasses')
    if not now:
        byte_state='NO_CURRENT_CLASS_DESCRIPTOR'
    elif any(v['classSha256'] is None for v in now):
        byte_state='HELD_CURRENT_MEMBER_METADATA'
    elif type(physical) is not list or names!=set(physical):
        byte_state='CURRENT_PHYSICAL_SET_DIFFERS'
    elif type(hashes) is not dict or any(type(hashes.get(n)) is not str or not re.fullmatch('[a-f0-9]{64}',hashes[n]) for n in names):
        byte_state='MISSING_OR_UNSUPPORTED_POST_CLASS_DIGESTS'
    elif all(hashes[v['physicalKey'].split(':',1)[1].removesuffix('.class')]==v['classSha256'] for v in now):
        byte_state='EXACT_CURRENT_PHYSICAL_BYTES'
    else:
        byte_state='DIFFERENT_CURRENT_PHYSICAL_BYTES'
    ref=row['declaredPostReference']
    state='MATCH' if post.get('sessionIdentity')==ref['originalSessionIdentity'] and post.get('execSha256')==ref['originalExecSha256'] else 'SOURCE_RUN_REFERENCE_MISMATCH'
    return dict(mainPath=row['mainPath'],postName=ref['postName'],historicalPostSource=post.get('source'),
                originalDeclaredCounterKind=row['declaredOriginalCounterKind'],sourceDeclarationStatus=row['status'],
                originalUnitRoot=root,counterReferenceState=counter_state,historicalCounters=totals,
                runReferenceState=state,currentByteState=byte_state,currentPhysicalNames=sorted(names),
                originalPhysicalNames=physical,currentSourceDeclarationHashMatches=row['registryAndCurrentSourceHashEqual'],
                currentPhysicalDeclarationNamesMatch=row['completePhysicalNamesEqual'],
                historicalReferenceOnly=True,currentRunQualified=False,newAcceptance=0)


assert not O.exists()
c=load(C)
for key in ['assessment','currentMethodMetadata']:
    ref=c[key];assert sha(Path(ref['path']).read_bytes())==ref['sha256']
rows=[r for r in load(Path(c['assessment']['path'])) if r['declaredPostReference'] and r['declaredPostReference']['postName']!=c['excludedAlreadyBoundPost']]
current=load(Path(c['currentMethodMetadata']['path']))
assert len(rows)==157 and len({r['mainPath'] for r in rows})==157
posts={};post_rows=[]
for ref in c['publicPostPins']:
    name=ref['path'];p=Path(name)
    assert name.startswith('evidence/01_PT/018_NK-OPS-001/evidence/provisional/') and name.endswith('/manifest.json')
    assert '..' not in p.parts and '/private' not in name and p.parent.name==ref['postName'] and not p.is_symlink()
    raw=p.read_bytes();assert len(raw)<=c['maxManifestBytes'] and sha(raw)==ref['sha256']
    m=json.loads(raw);posts[ref['postName']]=m
    cases=m.get('cases')
    if type(cases) is list and cases and all(type(v) is dict and v.get('result')=='PASS' and v.get('nonPass')==[] for v in cases):case_state='PASS_METADATA_ONLY'
    elif type(cases) is list and any(type(v) is dict and v.get('result') not in [None,'PASS'] for v in cases):case_state='NON_PASS_REPORTED'
    else:case_state='UNSUPPORTED_CASE_SCHEMA'
    post_rows.append(dict(postName=ref['postName'],path=name,sha256=ref['sha256'],historicalSource=m.get('source'),
                          originalExit=m.get('actualExit'),exitIsIntegerZero=type(m.get('actualExit')) is int and m['actualExit']==0,
                          sourceIsCommit=type(m.get('source')) is str and re.fullmatch('[a-f0-9]{40}',m['source']) is not None,
                          originalSessionReferenceMatches=m.get('sessionIdentity')==ref['originalSessionIdentity'],
                          originalExecReferenceMatches=m.get('execSha256')==ref['originalExecSha256'],
                          historicalCaseRows=len(cases) if type(cases) is list else None,historicalCaseState=case_state,
                          fullSourceUnitsShape=type(m.get('fullSourceUnits')).__name__,physicalClassesShape=type(m.get('physicalClasses')).__name__,
                          historicalReferenceOnly=True,currentRunQualified=False))
assert len(posts)==77 and {r['declaredPostReference']['postName'] for r in rows}==set(posts)
results=[row_assessment(r,posts[r['declaredPostReference']['postName']],current) for r in rows]
O.mkdir()
for name,value in [('public-post-bindings.json',post_rows),('source-reference-bindings.json',results)]:
    (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=c['source'],config={'path':str(C),'sha256':sha(C.read_bytes())},sourceDeclarations=157,publicPostManifests=77,sourceCounterReferenceStates=dict(Counter(r['counterReferenceState'] for r in results)),currentClassByteStates=dict(Counter(r['currentByteState'] for r in results)),sourceRunReferenceStates=dict(Counter(r['runReferenceState'] for r in results)),postCaseSchemaStates=dict(Counter(r['historicalCaseState'] for r in post_rows)),postIntegerZeroExits=sum(r['exitIsIntegerZero'] for r in post_rows),postValidCommitSources=sum(r['sourceIsCommit'] for r in post_rows),alreadyBound15460Reread=False,sourceIdentityRecomputed=False,originalXmlExecArchiveClassByteRead=False,privateRuntimeEvidenceRead=False,originalTestsReexecuted=False,historicalReferenceOnly=True,currentRunQualified=False,wholeWbsAccepted=False,compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,files={p.name:sha(p.read_bytes()) for p in O.iterdir()},tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__).read_bytes())})
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['actualExit','sourceDeclarations','publicPostManifests','sourceCounterReferenceStates','currentClassByteStates','sourceRunReferenceStates','postCaseSchemaStates','postIntegerZeroExits']},ensure_ascii=False))
