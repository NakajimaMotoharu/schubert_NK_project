"""Independent add-only source and complete physical byte scope; no Product invocation."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import out, prior_normal, original_value
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
import f03_lgs_boundary_vectors_v3 as vectors
import pg13571_lgs_boundary_config_v5 as cfg

SOURCE = 'e8e06bedba3311c8335dbb5ba9c4fdffafd86acf'

def main():
    invocation = capture(__file__)
    target = out(cfg, cfg.POST_NUMBER)
    assert not target.exists()
    normal_path = out(cfg, cfg.NORMAL_NUMBER) / 'manifest.json'
    normal_pin = data.sha(normal_path.read_bytes())
    normal = data.read_checked(normal_path, normal_pin)
    preflight_pin = '3107b605c91cdf57d2317fb12254925b9ca9da11c26d225c2365c82c39cb2281'
    preflight = data.read_checked(out(cfg, cfg.PREFLIGHT_NUMBER) / 'manifest.json', preflight_pin)
    static_path = out(cfg, cfg.STATIC_NUMBER) / 'manifest.json'
    static_pin = data.sha(static_path.read_bytes())
    static = data.read_checked(static_path, static_pin)
    assert normal['source'] == static['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == static['actualExit'] == static['spotbugsSixExit'] == 0
    assert static['normalManifestSha256'] == normal_pin and static['preflightManifestSha256'] == preflight_pin
    assert static['rawStatic'] == preflight['rawStatic'] == 2 and preflight['removedFindingIds'] == []
    old = prior_normal(cfg)
    hashes = normal['begin']['inputHashes']
    assert hashes.keys() == old['begin']['inputHashes'].keys()
    assert {p for p in hashes if hashes[p] != old['begin']['inputHashes'][p]} == {cfg.PATH}
    assert all(data.sha((data.ROOT/p).read_bytes()) == pin for p, pin in hashes.items())
    row, = original_value(cfg)['sources']
    text = (data.ROOT/cfg.PATH).read_text()
    assert vectors.inverse(row['text'], text, []) == preflight['originalTokenInverses'][cfg.PATH]
    assert vectors.negative(row['text'], text, []) == preflight['negativeVectors'][cfg.PATH] == 10
    before, after = jar_classes(old), jar_classes(normal)
    assert before == after and len(after) == 1843
    a, b = test_classes(old), test_classes(normal)
    assert a.keys() == b.keys() and len(b) == 1978
    entry = cfg.PATH.split('/src/test/java/')[1][:-5]
    closure = {k for k in b if k[0] == 'web' and (k[1] == entry+'.class' or k[1].startswith(entry+'$'))}
    changed = {k for k in b if a[k] != b[k]}
    assert closure and changed and changed <= closure
    assert all(data.sha(Path(item['path']).read_bytes()) == item['sha256'] for item in normal['jars'].values())
    verify(invocation)
    target.mkdir()
    data.write(target/'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation,
        normalManifestSha256=normal_pin, staticManifestSha256=static_pin, preflightManifestSha256=preflight_pin,
        mainPhysical=1843, allMainBytesUnchanged=True, oldTestPhysical=1978, testPhysical=1978,
        changedTestPhysical=sorted(changed), sourceFileClosure=sorted(closure), otherTestBytesUnchanged=1978-len(changed),
        originalJUnitMethodsPreserved=8, addedJUnitMethods=0, addedSubvectorIds=cfg.VECTOR_IDS,
        originalTokenInverse=preflight['originalTokenInverses'][cfg.PATH], negativeVectors=10,
        rawStatic=2, removedDiagnosticCount=0, productTestsExecuted=0, oldProductResultTransferred=False,
        newAccepted=0, whole451Accepted=False, formalUpdated=False, externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
