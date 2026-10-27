"""Independent strict raw token inverse for six constant values and one two-reference field rename."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG12448-config-template-source-post-v1'
PLAN = '3ccd10cea379621ccbe31b03ea8faa0aed9844013b648ac199447d41ca446d95'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java'
NAMES = {'COMMON_TEMPLATE':('"common.yml.template"',4),'API_TEMPLATE':('"api.yml.template"',4),'WEB_TEMPLATE':('"web.yml.template"',4),'BATCH_TEMPLATE':('"batch.yml.template"',10),'API_ENV_TEMPLATE':('"api.env.template"',4),'INSPECTOR_ENV_TEMPLATE':('"inbox-inspector.env.template"',4)}

def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(before,after):
    tokens = raw(after)
    for name,(literal,count) in NAMES.items():
        decl = raw('private static final String '+name+' = '+literal+';')
        found = [i for i in range(len(tokens)-len(decl)+1) if tokens[i:i+len(decl)] == decl]
        if len(found) != 1:
            raise ValueError('one exact same-value String declaration required')
        i = found[0];del tokens[i:i+len(decl)]
        if tokens.count(name) != count or raw(before).count(literal) != count:
            raise ValueError('all original exact references required')
        tokens = [literal if token == name else token for token in tokens]
    if tokens.count('BATCH_DEFAULTS') != 2 or tokens.count('BATCH') != 0:
        raise ValueError('one field declaration and one usage renamed, no method rename')
    tokens = ['BATCH' if token == 'BATCH_DEFAULTS' else token for token in tokens]
    if tokens != raw(before):
        raise ValueError('all original method/helper/control/fixture/oracle tokens must remain')

def main():
    invocation = capture(__file__);assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG12446-config-template-plan-v1/manifest.json',PLAN)
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    snapshot = Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    before,after = (snapshot/TEST).read_text(),(data.ROOT/TEST).read_text()
    assert len(plan['sourceChanges']) == 1 and plan['sourceChanges'][0]['path'] == TEST and plan['stringConstants'] == 6 and plan['stringReferences'] == 30 and plan['fieldRenames'] == 1
    assert data.sha(before.encode()) == plan['sourceChanges'][0]['beforeSha256'] and data.sha(after.encode()) == plan['sourceChanges'][0]['sha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    inverse(before,after)
    methods = re.findall(r'@Test\s+void (\w+)\(',before);assert len(methods) == 4 and methods == re.findall(r'@Test\s+void (\w+)\(',after)
    bads = []
    for name,(literal,_) in NAMES.items():
        decl = 'private static final String '+name+' = '+literal+';'
        for wrong in ('',decl.replace(literal,'"foreign.template"'),decl.replace('String','Object')):
            bads.append(after.replace(decl,wrong,1))
    bads.extend([after.replace('BATCH_DEFAULTS','WRONG_FIELD',1),after.replace('BATCH_DEFAULTS','BATCH',1),after.replace('@Test','@Disabled',1),after.replace('assertEquals(','assertNotEquals(',1)])
    negatives = 0
    for bad in bads:
        assert bad != after
        try:
            inverse(before,bad)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('changed original independent oracle accepted')
    assert negatives == len(bads) == 22
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PLAN,sourceChanges=plan['sourceChanges'],originalMethods=4,originalCatalog=[dict(path=TEST,method=m) for m in methods],metadataNegativeVectors=negatives,allOriginalRawTokensRestored=True,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
