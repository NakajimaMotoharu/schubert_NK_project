"""Five same-value fixture constants after independently checked SDK-oracle fix; no replay."""
import subprocess
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG12405-batch-runtime-literal-source-post-v1'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/bootstrap/BatchRuntimeDependencyTest.java'
CONSTANTS = [('PMD-03435','RUNTIME_SCOPE_ELEMENT','"<scope>runtime</scope>"',8),('PMD-03436','PROJECT_GROUP','"dev.codex.schubert"',7),('PMD-03437','BOOTSTRAP_ARTIFACT','"schubert-nk-bootstrap"',7),('PMD-03438','FLYWAY_GROUP','"org.flywaydb"',4),('PMD-03439','TEST_SCOPE_ELEMENT','"<scope>test</scope>"',7)]

def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(before,after):
    tokens = raw(after)
    for _,name,literal,count in CONSTANTS:
        declaration = raw('private static final String '+name+' = '+literal+';')
        positions = [i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)] == declaration]
        if len(positions) != 1:
            raise ValueError('one unchanged String declaration required')
        a = positions[0];del tokens[a:a+len(declaration)]
        if tokens.count(name) != count or raw(before).count(literal) != count:
            raise ValueError('all fixed original references required')
        tokens = [literal if token == name else token for token in tokens]
    if tokens != raw(before):
        raise ValueError('all independently reviewed SDK oracle tokens must be retained')

def main():
    invocation = capture(__file__);assert not OUT.exists()
    oracle = data.read_checked(data.BASE/'PG12404-batch-runtime-oracle-source-post-v1/manifest.json','252f1348b9bfc70035cfb52c0c4fb464383e81e07a9c1de9bfdff64e3849f905')
    normal = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    before = subprocess.check_output(['git','show','92941a174c9dc82289addcc20ef6d95f5f53314e:'+TEST],cwd=data.ROOT).decode()
    after = (data.ROOT/TEST).read_text()
    assert data.sha(before.encode()) == oracle['sourceChanges'][0]['sha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    inverse(before,after);negatives = 0
    for _,name,literal,_ in CONSTANTS:
        declaration = 'private static final String '+name+' = '+literal+';'
        for wrong in ['',declaration.replace(literal,'"changed"'),declaration.replace('String','Object')]:
            bad = after.replace(declaration,wrong,1);assert bad != after
            try:
                inverse(before,bad)
            except ValueError:
                negatives += 1
            else:
                raise AssertionError('changed fixture accepted')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],oracleIntermediateSource='92941a174c9dc82289addcc20ef6d95f5f53314e',invocation=invocation,oracleSourcePostSha256='252f1348b9bfc70035cfb52c0c4fb464383e81e07a9c1de9bfdff64e3849f905',sourceChanges=[dict(path=TEST,beforeSha256=normal['begin']['inputHashes'][TEST],oracleIntermediateSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))],sameValueConstantIds=[r[0] for r in CONSTANTS],stringConstants=5,stringReferences=33,metadataNegativeVectors=negatives,allOracleIntermediateTokensRestored=True,allMainAndOtherInputsPreserved=True,originalMethods=2,newMethods=1,expectedMethods=oracle['expectedMethods'],newTestIds=['PT-BAT-283C'],productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
