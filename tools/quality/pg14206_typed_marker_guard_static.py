"""Static source contract only: typed marker guard order and exact four-site diff, never execute Product."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX,close
from host_tool_invocation import capture,verify

BASE='0061d178cda80c2ce3926290619c64db125dbcfc'
NORMAL='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
PREFIX='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
# Method roles and receivers are independent manual Source/SS312 review, not Product execution.
ROLES={
'admin/UserMutationApplicationService':[('execute','AuthenticationContextException','failure'),('execute','InboxException','failure')],
'admin/UserQueryApplicationService':[('inspect','AuthenticationContextException','failure'),('inspect','InboxException','failure'),('complete','AuthenticationContextException','failure'),('persist','InboxException','failure')],
'log/LogQueryApplicationService':[('inspect','AuthenticationContextException','failure'),('inspect','InboxException','failure'),('complete','AuthenticationContextException','failure'),('persist','InboxException','failure')],
'media/MediaApplicationService':[('transaction','AuthenticationContextException | AccessRejected','failure'),('transaction','InboxException','failure')],
'question/QuestionMutationApplicationService':[('execute','AuthenticationContextException','invalid'),('execute','InboxException','conflict')],
'question/QuestionQueryApplicationService':[('inspect','AuthenticationContextException','failure'),('inspect','InboxException','failure'),('complete','AuthenticationContextException','failure'),('persist','InboxException','failure')],
'question/QuestionWorkerService':[],
'scenario/ScenarioApplicationService':[('transaction','AuthenticationContextException | AccessRejected','failure'),('transaction','InboxException','failure')],
'question/QuestionSubmissionService':[('execute','AuthenticationContextException','invalid'),('executeCanonical','InboxException','conflict')],
'question/QuestionCommandService':[]}
PATHS={name:PREFIX+name+'.java' for name in ROLES}
INBOX_COMMENT='// BUG2092/YKT1840; SS312/324 SSC329: inspect fatal graph before mismatch.'
AUTH_COMMENT='// BUG2093/YKT1840; SS312 SSC329: inspect fatal graph before SESSION_INVALID.'
PATCHES={}
for name in ['admin/UserQueryApplicationService','log/LogQueryApplicationService','question/QuestionQueryApplicationService']:
    old='      } catch (InboxException failure) {\n        if (messageMismatch(failure)) return invalid(connection, request, actor);'
    inserted='        '+INBOX_COMMENT+'\n        TemporaryInfrastructureException.preserveFatal(failure);\n'
    new='      } catch (InboxException failure) {\n'+inserted+'        if (messageMismatch(failure)) return invalid(connection, request, actor);'
    identity=name+':persist:InboxException'
    PATCHES[identity]=dict(path=PATHS[name],old=old,new=new,inserted=inserted)
name='question/QuestionQueryApplicationService'
old='    } catch (AuthenticationContextException failure) {\n      return reject(connection, request, Optional.empty(), Rejection.SESSION_INVALID);'
inserted='      '+AUTH_COMMENT+'\n      TemporaryInfrastructureException.preserveFatal(failure);\n'
new='    } catch (AuthenticationContextException failure) {\n'+inserted+'      return reject(connection, request, Optional.empty(), Rejection.SESSION_INVALID);'
PATCHES[name+':complete:AuthenticationContextException']=dict(path=PATHS[name],old=old,new=new,inserted=inserted)

def require(ok,message):
    if not ok:raise ValueError(message)

def assess(texts):
    require(set(texts)==set(PATHS.values()),'exact declared public Source scope')
    rows=[]
    for name,roles in ROLES.items():
        text=texts[PATHS[name]]
        tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        found=[]
        for i,(token,offset) in enumerate(tokens):
            if token!='catch':continue
            ending=close(tokens,i+1,'(',')');header=[t for t,_ in tokens[i+2:ending]]
            if not ({'InboxException','AuthenticationContextException'}&set(header)):continue
            require(tokens[ending+1][0]=='{','typed catch body required')
            body_end=close(tokens,ending+1,'{','}')
            body=[t for t,_ in tokens[ending+2:body_end]]
            receiver=header[-1];types=' '.join(header[:-1])
            guard=['TemporaryInfrastructureException','.','preserveFatal','(',receiver,')',';']
            found.append(dict(headerTypes=types,receiver=receiver,catchLine=text.count('\n',0,offset)+1,firstStatementIsRequiredGuard=body[:7]==guard,bodyTokenSha256=data.sha(json.dumps(body).encode())))
        require(len(found)==len(roles),'all typed headers, including zero-eligible Source')
        for row,(method,types,receiver) in zip(found,roles):
            require(row['headerTypes']==types and row['receiver']==receiver,'manual exact type/receiver order')
            rows.append(dict(path=PATHS[name],methodRoleFromManualReview=method,siteId=name+':'+method+':'+types.split(' | ')[0],**row))
    require(len(rows)==len({r['siteId'] for r in rows})==22,'no slot loss or duplication')
    return rows

def missing(rows):
    return {r['siteId'] for r in rows if not r['firstStatementIsRequiredGuard']}

def patched(original):
    value=dict(original)
    for patch in PATCHES.values():
        require(value[patch['path']].count(patch['old'])==1,'one reviewed pre-fix catch only')
        value[patch['path']]=value[patch['path']].replace(patch['old'],patch['new'],1)
    return value

def run(phase, before_manifest_sha=None):
    require((phase=='before' and before_manifest_sha is None) or (phase=='after' and re.fullmatch('[0-9a-f]{64}',before_manifest_sha or '')),'pinned prior observation required only after')
    invocation=capture(__file__)
    out=data.BASE/('PG14206-typed-marker-guard-before-v1' if phase=='before' else 'PG14208-typed-marker-guard-after-v1')
    require(not out.exists(),'new-only static observation')
    normal=data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json',NORMAL)
    require(normal['source']==BASE and normal['actualExit']==normal['testsExecuted']==0,'fixed baseline normal input, never old PT transfer')
    hashes=normal['begin']['inputHashes']
    original={p:subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT).decode() for p in PATHS.values()}
    require(all(data.sha(v.encode())==hashes[p] for p,v in original.items()),'exact baseline public Source')
    baseline=assess(original);require(missing(baseline)==set(PATCHES),'four code-only baseline contract inconsistencies, not runtime reproduction')
    expected=original if phase=='before' else patched(original)
    actual={p:(data.ROOT/p).read_text() for p in PATHS.values()}
    require(actual==expected,'exact four guards/comments only; preserve every other byte')
    changed={p for p in original if original[p]!=expected[p]}
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items() if p not in changed),'all other normal Source/POM/Test/config bytes unchanged')
    observed=assess(actual);require(missing(observed)==(set(PATCHES) if phase=='before' else set()),'exact expected static guard state')
    labels=[]
    if phase=='after':
        before=data.read_checked(data.BASE/'PG14202-typed-marker-guard-before-v1/manifest.json',before_manifest_sha)
        require(before['baselineSource']==BASE and before['staticConformance'] is False and before['missingSites']==sorted(PATCHES) and before['productTestsExecuted']==0,'genuine pre-fix static observation, not a PASS')
        for identity,patch in PATCHES.items():
            p=patch['path'];needle=patch['inserted'];call='TemporaryInfrastructureException.preserveFatal(failure);'
            require(actual[p].count(needle)==1,'one intended inserted guard')
            for label,replacement in [('removed',''),('comment-only','// '+call),('string-only',json.dumps(call)+';'),('wrong-receiver','TemporaryInfrastructureException.preserveFatal(other);')]:
                bad=dict(actual);new_part=needle.replace(call,replacement,1);bad[p]=bad[p].replace(needle,new_part,1)
                require(missing(assess(bad))=={identity},'nonexecutable/missing/wrong guard must not pass')
                labels.append(identity+':'+label)
    verify(invocation);out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,phase=phase,baselineSource=BASE,candidateGitSource=None,candidateIsUnfrozenWorktree=phase=='after',invocation=invocation,normalManifestSha256=NORMAL,beforeManifestSha256=before_manifest_sha,baselineHashes={p:data.sha(v.encode()) for p,v in original.items()},observedHashes={p:data.sha(v.encode()) for p,v in actual.items()},changedProductionPaths=sorted(changed),staticConformance=not missing(observed),codeConformanceGateExit=1 if missing(observed) else 0,baselineMissingSites=sorted(PATCHES),missingSites=sorted(missing(observed)),typedSites=observed,typedSiteCount=22,requiredGuard='first executable statement uses exact caught receiver',metadataNegativeVectors=len(labels),negativeLabels=labels,otherInputBytesUnchanged=True,originalEightSourceWholeBodyReviewed=True,additionalSubmissionScope='execute/executeCanonical method-local only',additionalCommandScope='typed-marker eligibility only; not whole Source review',fullJavaParserSemanticBinding=False,wholeJavaUnicodeTranslationValidated=False,javaCompilerBindingVerified=False,productTestsExecuted=0,newProductTestIds=0,coverage=None,dynamicConformance=None,originalActualDatabasePt='HOLD_NOT_EXECUTED',heldGraph9='HOLD_NOT_EXECUTED_NO_SUBSTITUTE',actualExternalOperations=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,bugs=['BUG2092','BUG2093'],horizontal='YKT1840'))
    print(data.sha((out/'manifest.json').read_bytes()))
if __name__=='__main__':run('before')
