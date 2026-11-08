"""Verify the zero-target-role outcome independently; do not fetch any source object."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import importlib.util
import json
import re

R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001'
P=B/'evidence/PG23962-g07-public-test-source-digest-v1'
O=B/'evidence/PG23964-g07-public-test-source-independent-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
SCHEMA_MAPS={'sourceHashes','testSourceHashes','inputHashes','dependencyHashes','dependencyJarHashes',
             'jarHashes','xmlHashes','allPhysicalMainSha256','classHashes','sourceHash','testHashes'}


def parent_map(lines,line):
    target=lines[line-1]
    indent=len(target)-len(target.lstrip(' '))
    for previous in reversed(lines[:line-1]):
        if not previous.strip():continue
        width=len(previous)-len(previous.lstrip(' '))
        if width<indent:
            match=re.fullmatch(r'\s*"([A-Za-z][A-Za-z0-9_]*)": \{\s*',previous)
            return match[1] if match and match[1] in SCHEMA_MAPS else 'OTHER_OR_NONOBJECT_SCHEMA_CONTEXT'
    return 'NO_PARENT_SCHEMA_CONTEXT'


def zero_result(m):
    for name,value in [('newFalsePositives',0),('remainingUnclassified',3315),('actualDistinctGitSourceObjectsRead',0),('candidateRows',73),('productTestsExecuted',0)]:
        assert type(m[name]) is int and m[name]==value
    for name in ['capturedValuesWritten','captureValueHashesWritten','sourceBodiesWritten','protectedSourceObjectsRead',
                 'actualCredentialOrKeyFilesRead','compilerOrJvmExecuted','wholeG07Accepted','whole451Accepted',
                 'currentOrHistoricalTestExecutionQualified']:
        assert m[name] is False
    assert m['actualSecretCount'] is None


def main():
    assert not O.exists()
    m=load(P/'manifest.json');assert m['actualExit']==0;zero_result(m)
    cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp)
    op=R/cfg['originalMetadata']['path'];assert sha(op)==cfg['originalMetadata']['sha256'];original=load(op)
    prior=[]
    for ref in m['priorUpdateRefs']:
        p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
    assert len(original)==4493 and len(prior)==1178
    old=Counter(map(key,prior));remaining=Counter(map(key,original))-old
    assert sum(remaining.values())==3315
    for filename,digest in [('updates.json',m['updatesSha256']),('retained.json',m['retainedSha256']),('public-source-readset.json',m['sourceReadsetSha256'])]:
        assert sha(P/filename)==digest
    assert load(P/'updates.json')==[] and load(P/'public-source-readset.json')==[]
    retained=load(P/'retained.json')
    expected=[v for v in original if v['path'] in cfg['inputFiles'] and not old[key(v)]]
    assert len(expected)==73 and Counter(map(key,retained))==Counter(map(key,expected))
    context_counts=Counter();target_role_rows=0;format_counts=Counter()
    for path,pin in cfg['inputFiles'].items():
        p=R/path;assert sha(p)==pin;lines=p.read_text().splitlines()
        for f in [v for v in expected if v['path']==path]:
            assert f['inputSha256']==pin
            if f['shape']!='ALL_HEX64' or f['ruleId']!='generic-api-key' or f['startLine']!=f['endLine']:
                format_counts['UNSUPPORTED_SHAPE_OR_MULTILINE']+=1;continue
            pair=re.fullmatch(r'\s+"(?:\\.|[^"\\])*": "[a-f0-9]{64}",?',lines[f['startLine']-1])
            if pair is None:
                format_counts['NOT_STANDALONE_STRING_PAIR']+=1;continue
            role=parent_map(lines,f['startLine']);context_counts[role]+=1
            target_role_rows+=role in ['sourceHashes','testSourceHashes']
    assert target_role_rows==0
    assert len(retained)==72+1 and m['retainedStatusCounts']=={'UNKNOWN_OUTSIDE_TYPED_PUBLIC_SOURCE_MAP':72,'UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE':1}
    tool=R/'evidence/01_PT/018_NK-OPS-001/input/596_g07_public_test_source_digest.py'
    spec=importlib.util.spec_from_file_location('source_normalizer_definitions_only',tool)
    definitions=importlib.util.module_from_spec(spec);spec.loader.exec_module(definitions)
    good='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/PasswordHasherTest.java'
    assert definitions.source_name(good,cfg)==good
    assert definitions.source_name(str(R)+'/'+good,cfg)==good
    forbidden=[good.replace('PasswordHasherTest.java',v) for v in cfg['protectedSourceBasenames']]
    forbidden += ['../'+good,good.replace('/security/','/security/../security/'),'/private/key.java',good.replace('/src/test/','/src/main/'),None]
    for name in forbidden:assert definitions.source_name(name,cfg) is None
    negative=[]
    for field,value in [('newFalsePositives',1),('newFalsePositives',False),('remainingUnclassified',0),('actualDistinctGitSourceObjectsRead',1),
                        ('capturedValuesWritten',True),('captureValueHashesWritten',True),('protectedSourceObjectsRead',True),
                        ('currentOrHistoricalTestExecutionQualified',True),('actualSecretCount',0)]:
        altered=deepcopy(m);altered[field]=value
        try:zero_result(altered)
        except AssertionError:negative.append(field)
        else:raise AssertionError('invalid zero-result mutation accepted')
    O.mkdir()
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],
                producerManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),
                inputFiles=68,candidateRows=73,targetSourceRoleCandidates=0,sourceObjectsRead=0,
                observedNearestSchemaMapCounts=dict(context_counts),unsupportedFormattingCounts=dict(format_counts),
                newFalsePositives=0,cumulativeClassified=1178,remainingUnclassified=3315,binaryOrContainerLimited=22,
                actualSecretCount=None,selectionOutcome='NEW_TEST_WITNESS_HAS_NO_TARGET_CAPTURE_ROLE_IN_THIS_EXHAUSTED_SCOPE',
                selectionRework=True,originalPlanClassificationDelta=0,metadataNegativeChecks=negative,
                sourceNormalizerRejectedBeforeIO=len(forbidden),capturedValuesWritten=False,captureValueHashesWritten=False,
                protectedSourceObjectsRead=False,actualCredentialOrKeyFilesRead=False,
                productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,
                newAcceptance=0,formalUpdated=False,effortRate=None,wholeG07Accepted=False,whole451Accepted=False,
                verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,newFalsePositives=0,remaining=3315,targetRoleCandidates=0,roleCounts=dict(context_counts),formatCounts=dict(format_counts),manifestSha256=sha(O/'manifest.json'))))


if __name__=='__main__':
    main()
