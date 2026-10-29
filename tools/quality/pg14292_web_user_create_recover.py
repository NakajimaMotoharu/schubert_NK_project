"""Recover original completed owned compile/JVM receipts without replay; preserve wrapper failure."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14282_current_pt_environment_post import headers
import scoped_prometheus_post as check
import scoped_prometheus_host as common
import pg14288_web_user_create_whole_eight_pt as original

RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14288-web-user-create-whole-eight-pt-v1'
OUT=data.BASE/'PG14292-web-user-create-recovered-terminal-v1'
PINS={'begin.safe.json':'98887d0555ef3dec57720ea3f2746b535475756e44da8b7cff2c24bcb488f3e7','fresh-test-compile-exit.safe.json':'1fd9ef4deca0f2355fcb8f72e1a9b2bb445029dfd56f8c711a4768f216603e7d','selected-junit-exit.safe.json':'7b6db345937a7292c911cd71b5e8f9956401242afa375d29b1f53c134d9cb139'}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    inputs={n:data.read_checked(RUN/n,h) for n,h in PINS.items()}
    begin=inputs['begin.safe.json'];stages=[inputs[n] for n in ['fresh-test-compile-exit.safe.json','selected-junit-exit.safe.json']]
    assert begin['source']==original.SOURCE and begin['selectedSuites']==original.COUNTS and begin['expectedTests']==8
    assert all(s['actualExit']==0 and not s['timedOut'] for s in stages)
    assert data.sha((data.ROOT/'tools/quality/pg14288_web_user_create_whole_eight_pt.py').read_bytes())=='f4785dc50b59797eb5c748c7c1e94449bd469e197b7c9253de4641abf3f98554'
    verify(begin['invocation'])
    snapshot=original.COMPILE/'snapshot'
    for p,h in begin['sourceHashes'].items():assert data.sha((snapshot/p).read_bytes())==data.sha((data.ROOT/p).read_bytes())==h
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        assert all(data.sha(Path(p).read_bytes())==h for p,h in begin[key].items())
    for label,stage in zip(['fresh-test-compile','selected-junit'],stages):
        assert data.sha((RUN/(label+'.log')).read_bytes())==stage['logSha256']
        first=json.loads((RUN/(label+'-begin.safe.json')).read_bytes())
        assert first['command']==stage['command'] and first['startUTC']==stage['startUTC']
    lines=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            lines.append(line)
    assert sum(len(x.encode()) for x in lines)<=4096
    stages[1]=dict(stages[1],reportedEnvironment=headers(lines),environmentBasis='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION')
    suites={};cases=[];xml={}
    for path in sorted((RUN/'xml').glob('TEST-*.xml')):
        doc=ET.parse(path).getroot();name=doc.get('name')
        assert name=='dev.codex.schubert.nk.web.form.UserCreateFormTest' and name not in suites
        suites[name]={k:int(doc.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        xml[path.name]=data.sha(path.read_bytes())
        for case in doc.findall('testcase'):
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),result='PASS' if not list(case) else 'NOT_PASS',nonPass=[c.tag for c in case]))
    raw=dict(source=original.SOURCE,actualExit=0,begin=begin,stages=stages,suites=suites,cases=cases,xmlHashes=xml,execSha256=data.sha((RUN/'jacoco.exec').read_bytes()),qualification='RECOVERED_ORIGINAL_JVM_TERMINAL_POST_PENDING',whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,recoveryInvocation=invocation,originalWrapperExit=1,originalWrapperFailure='BUG2098_NEWLINE_AFTER_JVM_TERMINAL',recoveryOriginalReceiptHashes=PINS,productTestsReexecuted=0,actualExternalOperations=0)
    common.SOURCE=original.SOURCE;check.COUNTS=original.COUNTS;check.EXPECTED_FIXTURE_HASHES={};check.assess(raw)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',raw)
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
