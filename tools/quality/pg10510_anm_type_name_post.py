"""Identifier-only source and exact single UTF8 entry binary proof, no Controller execution."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10504_anm_type_name_plan import TARGET, OLD, NEW, check
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '6612747b7a5492e5c49647d85cfc2dcbe6d75c9f'
OUT = data.BASE/'PG10510-anm-type-name-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10504-anm-type-name-plan-v1/manifest.json',
        '0d0d2f6fa38aaa86eb738162718ccd717179271ca3cfd1825589f5b4cb1443f1')
    old = data.read_checked(data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json',
        '11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179')
    normal_path = data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    static = data.read_checked(data.BASE/'PG10507-anm-type-name-static-v2-v1/manifest.json',
        'd3c018b12b4e6cc22099e6859386a6c5c54a53f587434317c185935b4bd60ba2')
    assert normal['source'] == SOURCE and old['source'] == plan['baseSource'] == static['baseSource']
    assert normal['actualExit'] == normal['terminal']['actualExit'] == normal['testsExecuted'] == 0
    hashes,previous_hashes = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(previous_hashes)
    assert {p for p,h in hashes.items() if previous_hashes[p] != h} == {TARGET}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    previous = subprocess.check_output(['git','show',plan['baseSource']+':'+TARGET],cwd=data.ROOT).decode()
    current = (data.ROOT/TARGET).read_text()
    check(current,previous)
    assert data.sha(previous.encode()) == plan['beforeSha256']
    assert data.sha(current.encode()) == plan['plannedSha256'] == static['sourceHashes'][TARGET] == hashes[TARGET]
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    binary = ('web','dev/codex/schubert/nk/web/session/AnimationControllerTest.class')
    assert set(before) == set(after) and len(after) == 1962
    assert {k for k,h in after.items() if before[k] != h} == {binary}
    relative = binary[1]
    before_path = Path(old['jars']['web']['path']).parent/'test-classes'/relative
    after_path = Path(normal['jars']['web']['path']).parent/'test-classes'/relative
    raw_before,raw_after = before_path.read_bytes(),after_path.read_bytes()
    needle = b'\x01'+len(OLD).to_bytes(2,'big')+OLD.encode()
    replacement = b'\x01'+len(NEW).to_bytes(2,'big')+NEW.encode()
    assert len(needle) == len(replacement) and raw_before.count(needle) == raw_after.count(replacement) == 1
    assert raw_after == raw_before.replace(needle,replacement,1)
    old_static = data.read_checked(data.BASE/'PG10478-disjoint-six-literal-static-v1/manifest.json',
        '1cae3c256e3442adace66f78b521f981b119754d1edfeaef03ac0c2a4f73e4bc')
    old_rows = [r for r in old_static['reports']['pmd']['details'] if r['class'].split('.')[0] == 'AnimationControllerTest']
    assert static['reports']['pmd']['details'] == old_rows and len(old_rows) == 5
    assert static['actualExit'] == 1 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    context = data.read_checked(data.BASE/'PG10500-fixture-volatile-context-post-v1/manifest.json',
        'e17e849f071a01e8c7b6e2dc24a09d210ae821b0d31226c5fdc0964000f90aa8')
    assert context['source'] == plan['baseSource'] and context['actualExit'] == 0
    review = data.read_checked(data.BASE/'PG10504-anm-type-name-plan-v1/meaning-review.json',plan['meaningReviewSha256'])
    assert len(review) == 54 and sum(r['renamed'] for r in review) == 1
    approved = subprocess.check_output(['git','show','origin/main:'+plan['approvedSs']],cwd=data.ROOT)
    assert data.sha(approved) == plan['approvedSsSha256']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={TARGET:hashes[TARGET]},oldName=OLD,newName=NEW,
        identifierReferencesChanged=6,allOtherTokensAndLiteralValuesUnchanged=True,
        samePhysicalMainClasses=1843,otherTestClassesUnchanged=1961,testClasses=1962,
        beforeTestClassSha256=data.sha(raw_before),testClassSha256=data.sha(raw_after),
        binaryDifference='EXACTLY_ONE_EQUAL_LENGTH_UTF8_CONSTANT_FIELD_IDENTIFIER_ENTRY',
        everyOtherClassByteIncludingAllMethodCodeAndDebugIdentical=True,
        normalManifestSha256=data.sha(normal_path.read_bytes()),staticManifestSha256='d3c018b12b4e6cc22099e6859386a6c5c54a53f587434317c185935b4bd60ba2',
        reviewedConstants=54,otherConstantMeaningsConfirmed=53,rawPmdFindings=5,checkstyleFindings=0,
        oldRawFindingRowsAndControlContextsUnchangedAfterIdentifierNormalization=True,
        narrowStaticContextApplicableFindings=0,suppressionsAdded=False,
        oldContextSource=context['source'],oldRuntimeSuccessReassigned=False,
        productTestsExecuted=0,originalControllerPtStatus='NOT_EXECUTED_HOLD',
        externalActions=0,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
