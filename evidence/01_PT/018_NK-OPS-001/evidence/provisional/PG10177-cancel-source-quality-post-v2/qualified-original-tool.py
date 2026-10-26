"""Preserve original compile failure and bind corrected static/oracle/source without replay."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg10170_cancel_wire_preflight import TEST, BINARY, SOURCE, restored_tokens, tokens
import pg9346_direct_companion_jdk_post as steps


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10177-cancel-source-quality-post-v2'
    slot = data.ROOT.parent/'pgpt-runs/PG379/pg10177-cancel-source-quality-post-v2'
    assert not out.exists() and not slot.exists()
    def read(name,digest):
        return data.read_checked(data.BASE/name/'manifest.json',digest)
    normal = read('PG10169-cancel-six-compile-v2','1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c')
    old = read('PG10154-credloc-six-compile-v1','683c715df260cde5a46f76888ad3e60159ddeae5e303e35992edc1edd9d0bf6e')
    static = read('PG10167-cancel-precommit-static-v2','1a1b0270608f2f142e6b5f21c76639351728b024e4c89cd91a529bb6f84bc80c')
    failed = read('PG10168-cancel-six-compile-v1','8c8f5924c9f9bfc88ae60ebfdd68fd53fe468909581cadaef677b64028d2382f')
    first_static = read('PG10166-cancel-precommit-static-v1','4d0d8310c5e389588bedb57cc8b84eddfb112842dca803dd02d72e25c675ccd4')
    pt = read('PG10174-cancel-wire-post-v1','f27db4ecb8fd113e713e5d28b37c849077b4256dee3ce2bdbdb99bee13766fbc')
    pre = read('PG10170-cancel-wire-preflight-v1','45588a838b3995a943abb415af60503f939c5f314318a949e2789be39f314659')
    assert normal['source'] == pt['source'] == pre['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == pt['actualExit'] == pre['actualExit'] == 0
    assert failed['actualExit'] == first_static['actualExit'] == 1 and failed['testsExecuted'] == 0 and not failed['jars']
    assert first_static['reports']['pmd']['findings'] == 7 and first_static['reports']['checkstyle']['findings'] == 0
    assert static['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    hashes = normal['begin']['inputHashes']
    assert static['sourceHashes'] == {TEST:hashes[TEST]} and static['baseSource'] == old['source']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    root = Path(old['jars']['protocol']['path']).parents[3]
    assert restored_tokens((data.ROOT/TEST).read_text()) == tokens((root/TEST).read_text())
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    selected = ('protocol',BINARY.replace('.','/')+'.class')
    generated = ('protocol',BINARY.replace('.','/')+'$1.class')
    assert set(before) == set(after) and len(after) == 1931
    assert {k for k in after if after[k] != before[k]} == {selected,generated}
    normal_root = Path(normal['jars']['protocol']['path']).parents[3]
    tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/CancelTestSyntheticDebugMeasure.java'
    asm = tc/'m2/repository/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar'
    metadata_hashes = {str(p):data.sha(p.read_bytes()) for p in (helper,asm)}
    slot.mkdir(mode=0o700)
    reader = slot/'reader'
    reader.mkdir()
    steps.SLOT = slot
    jdk = tc/'jdk-25.0.4/bin'
    stages = [steps.step('compile-metadata',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',str(asm),'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    relative = 'src/schubert-nk-protocol/target/test-classes/'+generated[1]
    stages.append(steps.step('strict-debug-only',[str(jdk/'java'),'-cp',str(reader)+os.pathsep+str(asm),
        helper.stem,str(root/relative),str(normal_root/relative)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    output = (slot/'strict-debug-only.stdout').read_text().splitlines()
    assert output[0] == 'METADATA_VECTORS\t5' and len(output) == 2
    label,normalized_sha = output[1].split('\t')
    assert label == 'DEBUG_ONLY' and len(normalized_sha) == 64
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in metadata_hashes.items())
    assert pt['tests'] == pt['suites'] == 1 and pt['newTestIds'] == 0 and not pt['coverageUnion']
    assert pt['forbiddenProductProbeHits'] == 0 and pt['onlyOneDeclaredTestMethodExecuted']
    receipt = data.ROOT.parent/'pgpt-runs/PG379/pg10168-cancel-six-compile-v1/exit.safe.json'
    value = json.loads(receipt.read_bytes())
    assert value == failed['terminal'] and value['actualExit'] == 1
    verify(invocation)
    out.mkdir()
    (out/'original-format-failure-exit.safe.json').write_bytes(receipt.read_bytes())
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        currentTestSourceSha256=hashes[TEST],mainClassesByteIdentical=1843,otherSourceTestClassesByteIdentical=1929,
        changedSourcePhysicalTestClasses=2,outerHasRequiredCodeChange=True,generatedClassDebugOnly=True,
        generatedClassBeforeSha256=before[generated],generatedClassAfterSha256=after[generated],
        generatedNormalizedSha256=normalized_sha,metadataVectors=5,metadataStages=stages,metadataToolHashes=metadata_hashes,
        originalGuardToolPreserved='tools/quality/pg10176_cancel_source_quality_post.py',
        originalGuardFailureObserved=True,originalShellExitIncludesSubsequentLinter=True,
        allOriginalSourceTokensPreserved=True,originalStaticFindings=7,originalStaticExit=1,
        originalCompileExit=1,originalCompileSource=failed['source'],originalCompileLogSha256=value['logSha256'],
        originalCompileReceiptSha256=data.sha(receipt.read_bytes()),sourceChangedBeforeFreshCompile=True,
        rawStaticExit=0,rawPmdFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        currentSourceTests=1,newTestIds=0,addedIndependentGoldenVectors=4,newGoldenVectorHashes=pre['newGoldenVectorHashes'],
        units=pt['units'],wholeSourceFour100=False,noCodeSwitchMapNotMeasuredPass=True,
        productTestsReexecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainUnchanged=1843,otherTestUnchanged=1930,
        originalCompileExit=1,currentStaticExit=0,manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
