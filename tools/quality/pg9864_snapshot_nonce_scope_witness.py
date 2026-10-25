"""Old fixed source witness with nonsecret test buffers; exit1 is defect evidence, not a PASS."""
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SLOT = ROOT.parent/'pgpt-runs/PG379/pg9864-snapshot-nonce-scope-witness-v1'
OUT = BASE/'PG9864-snapshot-nonce-scope-witness-v1'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_sha = 'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95'
    normal = data.read_checked(BASE/'PG9812-cleanup-values-six-compile-v1/manifest.json',normal_sha)
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE
    helper = ROOT/'tools/quality/architecture/SnapshotNonceScopeWitness.java'
    helper_sha = data.sha(helper.read_bytes())
    jars = normal['jars']
    assert all(data.sha(Path(j['path']).read_bytes()) == j['sha256'] for j in jars.values())
    jspecify = ROOT.parent/'toolchain/m2/repository/org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar'
    assert jspecify.is_file() and jspecify.resolve() == jspecify
    annotation_sha = data.sha(jspecify.read_bytes())
    main_path = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
    assert data.sha((ROOT/main_path).read_bytes()) == normal['begin']['inputHashes'][main_path]
    name = 'dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'
    with zipfile.ZipFile(jars['api']['path']) as jar:
        original_class_sha = data.sha(jar.read(name))
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'witness'
    classes.mkdir()
    tc = ROOT.parent/'toolchain/jdk-25.0.4/bin'
    cp = ':'.join([jars['api']['path'],str(jspecify)])
    steps.SLOT = SLOT
    stages = [steps.step('compile-witness',[str(tc/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(classes),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('old-source-two-failures',[str(tc/'java'),'-cp',str(classes)+':'+cp,
        'dev.codex.schubert.nk.api.idempotency.SnapshotNonceScopeWitness']))
    code = stages[-1]['actualExit']
    output = (SLOT/'old-source-two-failures.stdout').read_text()
    expected = ['CASE\t'+kind+'\tPRIMARY=true\tINITIALIZED=true\tNONCE_CLEAR=false\tCALLER=true' for kind in ('RUNTIME','ERROR')]
    reproduced = code == 1 and output.splitlines() == expected and not stages[-1]['timedOut']
    assert reproduced
    assert data.sha(helper.read_bytes()) == helper_sha and data.sha(jspecify.read_bytes()) == annotation_sha
    assert all(data.sha(Path(j['path']).read_bytes()) == j['sha256'] for j in jars.values())
    verify(invocation)
    OUT.mkdir()
    (OUT/'witness-result.txt').write_text(output)
    manifest = dict(actualExit=code,source=SOURCE,normalManifestSha256=normal_sha,invocation=invocation,
        helperSha256=helper_sha,annotationLibrarySha256=annotation_sha,stages=stages,
        originalCodecClassSha256=original_class_sha,originalMainSourceSha256=normal['begin']['inputHashes'][main_path],
        defectReproduced=reproduced,failureCases=2,exceptionIdentityPreserved=True,callerArraysUnchanged=True,
        ownedNonceCleared=False,productPassCredit=0,actualCredentialsUsed=False,privateReflection=False,
        actualExternalOperations=0,graph9Operations=0,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',manifest)
    print(json.dumps(dict(actualExit=code,defectReproduced=reproduced,failureCases=2,notPassCredit=True,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
