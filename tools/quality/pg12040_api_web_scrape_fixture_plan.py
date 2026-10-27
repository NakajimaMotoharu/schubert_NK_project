"""21 independent scrape fixture Strings plus two same-value counter-kind comparisons."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed as strings
OUT=data.BASE/'PG12040-api-web-scrape-fixture-plan-v1'
FILES=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricScrapeTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricScrapeTest.java']
NAMES={'"DEBUG"':'DEBUG_MODE','"STANDARD"':'STANDARD_MODE','"LGNREQ01"':'LOGIN_LAYOUT','"# TYPE "':'TYPE_LINE_PREFIX','"service"':'SERVICE_LABEL','"API"':'API_SERVICE','"WEB"':'WEB_SERVICE','"state"':'STATE_LABEL','"active"':'ACTIVE_POOL_STATE','"layout"':'LAYOUT_LABEL','"result"':'RESULT_LABEL','"0000"':'SUCCESS_RESULT','"query_id"':'QUERY_ID_LABEL','"outcome"':'OUTCOME_LABEL','"SUCCESS"':'SUCCESS_OUTCOME','"gauge"':'GAUGE_TYPE'}
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inputs():
    normal=data.read_checked(data.BASE/'PG12016-web-business-record-six-compile-v1/manifest.json','214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a');assert normal['actualExit']==normal['testsExecuted']==0;snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True);rows=[]
        for row in root:
            if row['path']!=path or row['rule'] not in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition'):continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;literal=next(m.group() for m in ts if m.start()==point)
            if row['rule']=='AvoidDuplicateLiterals':
                count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count;rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
            else:
                assert literal=='1' and text[:point].endswith('kind == ');rows.append(dict(id=row['id'],kind='ORDER_INT',literal='1',name='COUNTER_PROVIDER_KIND',point=point,references=1))
        assert sum(r['kind']=='STRING' for r in rows)==(14 if 'ApiMetric' in path else 7) and sum(r['kind']=='ORDER_INT' for r in rows)==(2 if 'ApiMetric' in path else 0);assert not set(raw(text))&{r['name'] for r in rows};assert len(re.findall(r'@Test\s+void ',text))==14;table[path]=rows
    return normal,snapshot,table

def transformed(text,stem,rows):
    for row in sorted((r for r in rows if r['kind']=='ORDER_INT'),key=lambda r:r['point'],reverse=True):
        p=row['point'];assert text[p:p+1]=='1';text=text[:p]+row['name']+text[p+1:]
    text=strings(text,stem,[r for r in rows if r['kind']=='STRING'])
    if any(r['kind']=='ORDER_INT' for r in rows):
        header='class '+stem+' {\n';assert text.count(header)==1;text=text.replace(header,header+'  private static final int COUNTER_PROVIDER_KIND = 1;\n',1)
    return text

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'
def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert raw(after)==raw(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=21,stringReferences=sum(r['references'] for rows in table.values() for r in rows if r['kind']=='STRING'),orderConstants=1,comparisonReferences=2,originalMethods=28,rawDiagnosticCorrectionsExpected=23,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
