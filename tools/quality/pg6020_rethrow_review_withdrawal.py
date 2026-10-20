"""BUG1523: refine pure-root alternatives,withdraw six false necessity reasons;no Main/PT change."""
import copy
import hashlib
import json
import os
import re
import subprocess
from collections import Counter,defaultdict
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6010_api15_public import SOURCE
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load

ANCESTORS={'java.lang.RuntimeException':{'java.lang.RuntimeException','java.lang.Exception','java.lang.Throwable'},
           'java.lang.Error':{'java.lang.Error','java.lang.Throwable'}}
IDENTITY=('begincolumn','beginline','diagnosticTextSha256','endcolumn','endline','findingId','identitySchema','legacyFindingId','priority','rawXmlOrdinal','rule','sourcePath','sourceSha256')


def is_error_diagnostic(text,row):
    return fragment(text,row).strip()=='Error' and row['diagnosticTextSha256']==hashlib.sha256(b'Avoid catching Error in try-catch block').hexdigest()


def same_raw_identity(raw,rows):
    if len(raw)!=len(rows)or len({r['findingId']for r in raw})!=len(raw)or [r['findingId']for r in raw]!=[r['findingId']for r in rows]:
        raise ValueError('exact unique raw occurrence identities and original order')
    for original,classified in zip(raw,rows):
        if set(original)!=set(IDENTITY)|{'status'}or original['status']!='NOT_REVIEWED_CURRENT_SOURCE'or any(original[k]!=classified[k]for k in IDENTITY):
            raise ValueError('all immutable raw fields exact;only classified status may intentionally differ')


def refine(rows):
    groups=defaultdict(list);actions=[];protected=[]
    for row in rows:groups[row['path'],row['tryStart']].append(row)
    for siblings in groups.values():
        total=int(siblings[0]['catchTotal'])
        if len(siblings)!=total or {int(r['catchIndex'])for r in siblings}!=set(range(total)):raise ValueError('complete one actual Try catch identity set')
        for row in siblings:
            if row['pureSingleRethrow']!='true'or row['exactUncheckedRoots']!='true':continue
            caught=row['type'].split('|')
            if not set(caught)<=set(ANCESTORS):raise ValueError('only exact JDK unchecked root alternatives')
            following={t for r in siblings if int(r['catchIndex'])>int(row['catchIndex'])for t in r['type'].split('|')}
            kept=[t for t in caught if ANCESTORS[t]&following];removed=[t for t in caught if t not in kept]
            if (row['laterCatchOverlap']=='true')!=bool(kept):raise ValueError('independent JDK hierarchy table must equal actual Javac subtype result')
            if not removed:
                protected.append(dict(path=row['path'],method=row['method'],keptTypes=kept,followingTypes=sorted(following)));continue
            if not kept and row['residualTryStable']!='true':continue
            actions.append(dict(row,kind='NARROW_PURE_CATCH'if kept else'REMOVE_PURE_CATCH',keptTypes=kept,removedTypes=removed,followingTypes=sorted(following),sourceCodeApplied=False))
    return actions,protected


def main():
    fp=W/'pg6018-pure-rethrow-facts-v1/manifest.safe.json'
    if sha(fp)!='a41aa68e00e35d3430b10043d9e7db5f8bfb9ef35add69630dfc80686185178e':raise ValueError('actual Main-only1094/8511666 immutable AST facts')
    facts=json.loads(fp.read_bytes())
    if facts['source']!=SOURCE or any(type(facts.get(k))is not int or facts[k]!=0 for k in('actualExit','compileExit','independentFixtureExit')):raise ValueError('same source/compile/independent fixture individually0')
    command=[str(TC/'jdk-25.0.4/bin/javap'),'-public','java.lang.Error','java.lang.RuntimeException','java.lang.Exception','java.lang.Throwable']
    hierarchy=subprocess.check_output(command,text=True,timeout=30)
    parents=dict(re.findall(r'^public class ([\w.]+)(?: extends ([\w.]+))?',hierarchy,re.MULTILINE))
    expected={'java.lang.Error':'java.lang.Throwable','java.lang.RuntimeException':'java.lang.Exception','java.lang.Exception':'java.lang.Throwable','java.lang.Throwable':''}
    if parents!=expected:raise ValueError('independent actual fixed JDK Error/Runtime/Exception/Throwable hierarchy')
    actions,protected=refine(facts['rows'])
    if Counter(a['kind']for a in actions)!=Counter(NARROW_PURE_CATCH=5,REMOVE_PURE_CATCH=1)or len({a['path']for a in actions})!=2 or len(protected)!=1 or not protected[0]['path'].endswith('/LinuxSystemdSession.java'):
        raise ValueError('exact six Error alternatives/two owners;native Throwable catch still protected')
    bp=BASE/'PG6012-api-bounds-dispositions-v1/manifest.json';bsha='b572d5e56da464c69df5db416441bab7977cf15d5ba7c736a513fe5af99b7e35';rows=load(bp,bsha,SOURCE)
    raw=json.loads((BASE/'PG6008-api-bounds-static-v1/findings.json').read_bytes());byid={r['findingId']:r for r in raw}
    same_raw_identity(raw,rows)
    withdrew={};links=[]
    for action in actions:
        path=action['path'];text=(ROOT/path).read_text()
        if sha(ROOT/path)!=facts['identity']['sourceHashes'][path]or action['removedTypes']!=['java.lang.Error']:raise ValueError('same current source and only redundant Error component')
        matches=[r for r in rows if r['sourcePath']==path and r['rule']=='AvoidCatchingGenericException'and int(action['firstLine'])<=int(r['beginline'])<=int(action['lastLine'])and is_error_diagnostic(text,r)]
        if len(matches)!=1:raise ValueError('one exact actual Error diagnostic per reviewed source catch')
        old=matches[0]
        if old['findingId']in withdrew or old['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'or old['priorDisposition']!='REQUIRED_CONTRACT':raise ValueError('only six existing mistaken necessity reasons,not arbitrary reclassification')
        value=copy.deepcopy(byid[old['findingId']]);value.update(reviewWithdrawn=True,withdrawalBug='BUG-1523',withdrawalYkt='YKT-1283',
            withdrawnReview=dict(manifestSha256=bsha,priorStatus=old['status'],priorDisposition=old['priorDisposition'],priorReason=old['priorReason']),
            withdrawalReason='Error is not an Exception subtype. This pure rethrow has no state/cleanup effects;the later Exception catch cannot normalize Error. The existing required-necessity rationale was incorrect. Main remains unchanged until active whole is preserved.',rawWarningRetained=True)
        withdrew[old['findingId']]=value;links.append(dict(action,findingId=old['findingId'],sourceSha256=sha(ROOT/path)))
    if len(withdrew)!=6:raise ValueError('all and only six prior Error necessity claims withdrawn')
    result=[withdrew.get(r['findingId'],r)for r in rows];counts=Counter(r['status']for r in result)
    if counts!=Counter(SOURCE_REBOUND_CURRENT_WHOLE_PENDING=630,NOT_REVIEWED_CURRENT_SOURCE=718):raise ValueError('actual corrected630pending/718unreviewed;raw1348 unchanged')
    out=BASE/'PG6020-rethrow-review-withdrawal-v1';os.umask(0o077);out.mkdir()
    for name,data in(('findings.json',result),('actions.json',links)):
        with(out/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=SOURCE,priorReviewManifestSha256=bsha,inventoryFile='findings.json',inventorySha256=sha(out/'findings.json'),actionsSha256=sha(out/'actions.json'),
        statusCounts=dict(counts),dispositionsWithdrawn=6,newIndividualDispositions=0,rawFindings=1348,typedFactsSha256=sha(fp),jdkHierarchyCommand=command,jdkHierarchy=parents,
        protectedRootScopes=protected,sourceCodeChanged=False,activeWholeSourceUnchanged=True,currentWholeJoinPending=True,executedPtAdded=0,ptAlternativeCompleted=0,F03Accepted=False,formalAccepted=False,vmActions=0)
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,withdrawnReasons=6,pendingWhole=630,unreviewed=718,raw=1348,candidateEdits=6,candidateSources=2,sourceCodeChanged=False,manifestSha256=sha(out/'manifest.json'),inventorySha256=sha(out/'findings.json'),actionsSha256=sha(out/'actions.json'))))


if __name__=='__main__':main()
