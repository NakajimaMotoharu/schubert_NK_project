"""Eleven local independent String constants and one SDK-fixture field rename, Main unchanged."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11860-web-exporter-fixture-plan-v1'
FILES=[f'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/Web{kind}MetricExporterTest.java' for kind in ('Duration','Counter','Gauge')]
NAMES={'"route"':'ROUTE_LABEL','"service"':'SERVICE_LABEL','"/login"':'LOGIN_ROUTE','"WEB"':'WEB_SERVICE','"state"':'STATE_LABEL','"active"':'ACTIVE_STATE','"le=\\\"+Inf\\\"} 2\\n"':'INFINITE_BUCKET_TWO'}

def inputs():
    normal=data.read_checked(data.BASE/'PG11834-mq-media-collector-value-six-compile-v1/manifest.json','878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b');assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));rows=[]
        for row in root:
            if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;m=next(m for m in ts if m.start()==point);literal=m.group();count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count
            rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
        assert len(rows)==(5 if 'Duration' in path else 3);assert not any(m.group() in {r['name'] for r in rows}|{'suppliedReading'} for m in ts);table[path]=rows
    assert sum(map(len,table.values()))==11
    return normal,snapshot,table

def transformed(text,stem,rows):
    if 'Gauge' in stem:
        for old,new in [('final double value;','final double suppliedReading;'),('this.value = value;','this.suppliedReading = value;'),('return value;','return suppliedReading;')]:
            assert text.count(old)==1;text=text.replace(old,new,1)
    return strings(text,stem,rows)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,fieldBindingTokensRenamed=3 if 'Gauge' in path else 0))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=11,stringReferences=sum(r['references'] for rows in table.values() for r in rows),fieldRenameDiagnostics=1,fieldBindingTokensRenamed=3,originalMethods=48,rawDiagnosticCorrectionsExpected=12,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
