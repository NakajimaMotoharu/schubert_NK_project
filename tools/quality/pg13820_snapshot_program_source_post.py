"""Original assertions preserved; complete Main/Test physical byte difference post."""
import json
import subprocess
from pathlib import Path
import snapshot_program_qualification as cfg
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

data = cfg.data
OUT = data.BASE/'PG13820-snapshot-program-source-post-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    n,pin = cfg.normal()
    prior = data.read_checked(data.BASE/'PG13596-lgs-remaining-two-branches-v1/manifest.json','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
    p = cfg.TEST_ROOT+'InspectorUnitSnapshotTest.java'
    old = subprocess.check_output(['git','show','17ab52b253282ce45016f0586c0167a22029fd8c:'+p],cwd=data.ROOT,text=True)
    new = (data.ROOT/p).read_text()
    start = new.index('  @Test\n  void normalExitCodeIsLiteralOnlyAfterNormalMainCode() {')
    end = new.index('  @Test\n  void immutabilityAndNull()',start)
    assert new[:start]+new[end:] == old
    assert old.count('@Test') == 9 and new.count('@Test') == 10
    block = new[start:end]
    for term in ['{0, 1, 10, 30, 70, 143, 255}','{0, 2, 3, 4, 5, 6}','assertEquals(status, state.normalExitCode());','malformed(state::normalExitCode);']:
        assert term in block
    assert set(prior['begin']['inputHashes']) == set(n['begin']['inputHashes'])
    assert {path for path,sha in n['begin']['inputHashes'].items() if prior['begin']['inputHashes'][path] != sha} == {p}
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    before,after = jar_classes(prior),jar_classes(n)
    assert before == after and len(after) == 1843
    a,b = test_classes(prior),test_classes(n)
    assert a.keys() == b.keys() and len(b) == 1978
    prefix = p.split('/src/test/java/')[1][:-5]
    closure = {k for k in b if k[0] == 'batch' and (k[1] == prefix+'.class' or k[1].startswith(prefix+'$'))}
    changed = {k for k in b if a[k] != b[k]}
    assert changed and changed <= closure
    for path,sha in cfg.PINS.items():
        assert n['begin']['inputHashes'][cfg.TEST_ROOT+path+'.java'] == sha
    assert data.sha((cfg.NORMAL_SLOT/'snapshot'/cfg.CONFIG).read_bytes()) == cfg.CONFIG_SHA
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=cfg.SOURCE,invocation=invocation,normalManifestSha256=pin,
        previousNormalManifestSha256='1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12',changedInputPaths=[p],
        originalMethodsPreserved=9,addedMethods=1,newTestIds=['PT-SNAPSHOT-NORMAL-EXIT-001'],originalAssertionsUnchanged=True,
        mainPhysical=1843,allMainBytesUnchanged=True,testPhysical=1978,changedTestPhysical=sorted(changed),sourceFileClosure=sorted(closure),
        otherTestBytesUnchanged=1978-len(changed),fixtureConfigSha256=cfg.CONFIG_SHA,productTestsExecuted=0,oldProductResultTransferred=False,
        whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),changedTestPhysical=sorted(changed),unchangedMainPhysical=len(after))))

if __name__ == '__main__':main()
