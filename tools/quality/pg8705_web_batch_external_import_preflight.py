"""Exact role boundary/foreign SDK-JUnit import guard before fresh normal compilation."""
import copy
import datetime
import json
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SOURCE='4c97764a913a09fd39d9881eb6e112e66c1547e3'

def external(body):
    values=re.findall(r'^import (?:static )?([^;]+);$',body,re.M)
    assert len(values)==len(set(values))
    return set(value for value in values if not value.startswith('dev.codex.schubert.nk.'))

def assess(actual,expected):
    assert actual==expected

if __name__=='__main__':
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8705-web-batch-external-import-preflight-v1'
    assert not out.exists()
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    rows=[]
    negatives=[]
    for scope,suffix in (('main',''),('test','Test')):
        base=f'src/schubert-nk-api/src/{scope}/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource{suffix}.java'
        expected=external((host.ROOT/base).read_text())
        for role,title in (('web','Web'),('batch','Batch')):
            path=f'src/schubert-nk-{role}/src/{scope}/java/dev/codex/schubert/nk/{role}/monitoring/{title}StandardMetricSource{suffix}.java'
            body=(host.ROOT/path).read_text()
            assert body.startswith('package dev.codex.schubert.nk.'+role+'.monitoring;') and title+'StandardMetricSource'+suffix in body
            actual=external(body)
            assess(actual,expected)
            if scope=='test':
                assert body.count('@Test')==16 and len(re.findall(r'void '+role+r'host\d{3}',body))==16
                assert 'org.junit.jupiter.api.Test' in actual
            for name in ('foreign-import','missing-import','extra-import'):
                changed=copy.copy(actual)
                if name=='foreign-import':changed.remove(sorted(changed)[0]);changed.add('org.junit.jupiter.'+role+'.Test')
                elif name=='missing-import':changed.remove(sorted(changed)[0])
                else:changed.add('java.net.ServerSocket')
                try:assess(changed,expected)
                except AssertionError:negatives.append(path+':'+name)
                else:raise AssertionError('every import mutation must reject')
            rows.append(dict(path=path,sha256=host.sha(host.ROOT/path),externalImports=sorted(actual),baselinePath=base,baselineSha256=host.sha(host.ROOT/base)))
    helper=host.ROOT/'tools/quality/architecture/WebBatchStandardMetricSourceJunitLauncher.java'
    selected=re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);',helper.read_text(),re.S)
    assert len(selected)==1
    selected=re.findall(r'"([a-zA-Z0-9_.]+)"',selected[0])
    expected={f'dev.codex.schubert.nk.{role}.monitoring.{title}StandardMetricSourceTest' for role,title in (('web','Web'),('batch','Batch'))}
    assert len(selected)==2 and set(selected)==expected
    assert external(helper.read_text()) and all(not name.startswith(('org.junit.jupiter.web.','org.junit.jupiter.batch.')) for name in external(helper.read_text()))
    verify(invocation)
    out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,sourceRows=rows,helperSha256=host.sha(helper),selected=selected,negativeGuards=negatives,productTestsExecuted=0,mainChanged=False,formalUpdated=False,newAccepted=0,actualVmActions=0,actualNetworkActions=0))
    print(json.dumps(dict(actualExit=0,files=4,negativeGuards=len(negatives),manifestSha256=host.sha(out/'manifest.json'))))
