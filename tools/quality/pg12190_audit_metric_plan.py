"""Five same-value Strings, three field identifiers and one if-index in independent Test oracles."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
from pg10840_web_view_duplicate_plan import transformed

OUT=data.BASE/'PG12190-audit-metric-plan-v1'
NORMAL='462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048'
AUDIT='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebSecurityAuditTest.java'
RECORDER='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricRecorderTest.java'
CONTRACT='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricContractTest.java'
FILES=[AUDIT,RECORDER,CONTRACT]
NAMES={'"step"':'STEP_LABEL','"DEBUG"':'DEBUG_MODE','"SUCCESS"':'SUCCESS_STATUS','"BACKUP_DB"':'BACKUP_DB_STEP','"CONFIG_INVALID"':'INVALID_CONFIG_CODE'}
RENAMES={AUDIT:{'ACTOR':'AUDIT_PRINCIPAL'},RECORDER:{'RUNS':'RUNS_METRIC_NAME','LAST':'LAST_METRIC_NAME'},CONTRACT:{}}
METHODS={AUDIT:6,RECORDER:8,CONTRACT:5}

def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inputs():
    normal=data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json',NORMAL)
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];rows=[]
        if path!=AUDIT:
            ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True)
            for row in original:
                if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
                assert row['inputSha256']==normal['begin']['inputHashes'][path]
                a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
                literal=next(m.group() for m in ts if m.start()==point);count=int(re.search(r' appears ([0-9]+) times',row['message'])[1])
                assert literal in NAMES and sum(m.group()==literal for m in ts)==count
                rows.append(dict(id=row['id'],literal=literal,name=NAMES[literal],references=count))
        assert len(rows)=={AUDIT:0,RECORDER:4,CONTRACT:1}[path]
        assert len(re.findall(r'@Test\s+void ',text))==METHODS[path]
        assert not set(raw(text))&({v for v in RENAMES[path].values()}|{r['name'] for r in rows}|{'LOCKED_EVENT_INDEX'})
        table[path]=rows
    assert sum(row['references'] for rows in table.values() for row in rows)==40
    return normal,snapshot,table

def change(before,path,rows):
    after=transformed(before,Path(path).stem,rows) if rows else before
    mapping=RENAMES[path]
    for m in reversed(list(LEX.finditer(after))):
        if m.group() in mapping:after=after[:m.start()]+mapping[m.group()]+after[m.end():]
    if path==AUDIT:
        assert after.count('if (i == 2)')==1
        after=after.replace('if (i == 2)','if (i == LOCKED_EVENT_INDEX)',1).replace('class WebSecurityAuditTest {','class WebSecurityAuditTest {\n  private static final int LOCKED_EVENT_INDEX = 2;',1)
    return after

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before
        after=change(before,path,rows)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert raw(after)==raw(change(before,path,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,identifierRenames=RENAMES[path],integerIndexConstant=path==AUDIT,originalMethods=METHODS[path]))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=5,stringReferences=40,fieldRenames=3,ifIndexConstants=1,rawDiagnosticsCorrected=9,originalMethods=19,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
