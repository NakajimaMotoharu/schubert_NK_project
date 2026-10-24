"""Actual caller15 metadata validator positive/negative checks, Production PT0."""
import copy
import datetime
import json
from pathlib import Path
import pg8884_caller_static_review_fixed_join as review
from host_tool_invocation import capture,verify

def main():
    invocation=capture(Path(__file__))
    out=review.host.BASE/'PG8883-caller-static-review-guards-v1'
    assert not out.exists() and review.host.sha(review.MANUAL)==review.MANUAL_SHA
    expected,_=review.inputs();manual=json.loads(review.MANUAL.read_text())
    review.validate(manual,expected)
    mutations=[('missing-row',lambda value:value['rows'].pop()),('altered-raw',lambda value:value['rows'][0]['raw'].update(rule='UnknownRule')),('changed-source',lambda value:value['rows'][0].update(sourceSha256='0'*64)),('false-pass',lambda value:value['rows'][0].update(qualityGatePass=True)),('false-runtime',lambda value:value['rows'][2].update(actualRuntimeProven=True)),('false-xml',lambda value:value['rows'][2].update(currentXmlQualified=True)),('pt-alternative',lambda value:value.update(ptAlternativeCompleted=1)),('wrong-web-status',lambda value:value['rows'][2].update(status='CONTEXT_NOT_APPLICABLE_J2EE_RULE')),('missing-test',lambda value:value['rows'][2]['testReference'].update(method='notADeclaredTest')),('source-span',lambda value:value['rows'][0]['sourceSpan'].append('altered')),('suppressed-warning',lambda value:value['rows'][0].update(rawWarningRetained=False))]
    rejected=[]
    for name,mutate in mutations:
        changed=copy.deepcopy(manual);mutate(changed)
        try: review.validate(changed,expected)
        except (AssertionError,KeyError,ValueError): rejected.append(name)
        else: raise AssertionError('every malformed review must reject')
    formal=b'RootServiceLauncher ExecStart /usr/bin/java '+ 'shellなし'.encode()
    unit='ExecStart=!/usr/bin/java -cp fixed dev.codex.schubert.nk.batch.file.RootServiceLauncher API'
    review.formal_contract(formal,unit)
    for name,changed_formal,changed_unit in [('missing-formal-launcher',formal.replace(b'RootServiceLauncher',b'Unknown'),unit),('missing-unit-syntax',formal,unit.replace('ExecStart=','ExecStart',1))]:
        try: review.formal_contract(changed_formal,changed_unit)
        except AssertionError: rejected.append(name)
        else: raise AssertionError('document and Unit contract mutations must reject')
    verify(invocation);out.mkdir()
    review.host.write(out/'manifest.json',dict(actualExit=0,source=review.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,manualSha256=review.MANUAL_SHA,validatorSha256=review.host.sha(Path(review.__file__)),metadataNegativeChecks=rejected,productionPtExecuted=0,coverage=None,qualityGatePass=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(rejected),productionPtExecuted=0,manifestSha256=review.host.sha(out/'manifest.json'))))

if __name__=='__main__':
    main()
