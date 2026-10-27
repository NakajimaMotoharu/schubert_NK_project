"""Six same-value public template names plus one field rename; four complete original Tests."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed

OUT = data.BASE/'PG12446-config-template-plan-v1'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java'
NAMES = {'"common.yml.template"':'COMMON_TEMPLATE','"api.yml.template"':'API_TEMPLATE','"web.yml.template"':'WEB_TEMPLATE','"batch.yml.template"':'BATCH_TEMPLATE','"api.env.template"':'API_ENV_TEMPLATE','"inbox-inspector.env.template"':'INSPECTOR_ENV_TEMPLATE'}
IDS = {'PMD-05240','PMD-05241','PMD-05242','PMD-05243','PMD-05244','PMD-05245'}

def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inputs():
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    before = (snapshot/TEST).read_text();assert data.sha(before.encode()) == normal['begin']['inputHashes'][TEST]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows = []
    for r in original:
        if r['id'] not in IDS:
            continue
        assert r['path'] == TEST and r['inputSha256'] == normal['begin']['inputHashes'][TEST] and r['rule'] == 'AvoidDuplicateLiterals'
        a = r['attributes'];start = sum(map(len,before.splitlines(keepends=True)[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        literal = next(m.group() for m in LEX.finditer(before) if m.start() == start)
        references = int(re.search(r' appears ([0-9]+) times',r['message'])[1])
        assert literal in NAMES and raw(before).count(literal) == references and NAMES[literal] not in raw(before)
        rows.append(dict(id=r['id'],name=NAMES[literal],literal=literal,references=references))
    assert len(rows) == 6 and sum(r['references'] for r in rows) == 30 and raw(before).count('BATCH') == 2 and 'BATCH_DEFAULTS' not in raw(before)
    field = next(r for r in original if r['id'] == 'PMD-05246')
    assert field['path'] == TEST and field['rule'] == 'AvoidFieldNameMatchingMethodName' and field['inputSha256'] == normal['begin']['inputHashes'][TEST]
    assert len(re.findall(r'@Test\s+void ',before)) == 4
    return normal,before,rows

def changed(before,rows):
    text = transformed(before,'ConfigurationTemplateContractTest',rows)
    for m in reversed(list(LEX.finditer(text))):
        if m.group() == 'BATCH':
            text = text[:m.start()]+'BATCH_DEFAULTS'+text[m.end():]
    return text

def emit():
    _,before,rows = inputs();assert (data.ROOT/TEST).read_text() == before
    after = changed(before,rows)
    return '*** Begin Patch\n*** Update File: '+str(data.ROOT/TEST)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n*** End Patch\n'

def main():
    invocation = capture(__file__);assert not OUT.exists();normal,before,rows = inputs();after = (data.ROOT/TEST).read_text()
    assert raw(after) == raw(changed(before,rows)) and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,fieldRename=dict(id='PMD-05246',before='BATCH',after='BATCH_DEFAULTS',references=2))],originalMethods=4,stringConstants=6,stringReferences=30,fieldRenames=1,rawDiagnosticsCorrected=7,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
