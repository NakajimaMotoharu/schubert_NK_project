"""Complete physical/source/ABI proof for two Test-local oracle helpers, never target execution."""
import copy
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13324_state_oracle_config as cfg
import f03_state_oracle_sources as source
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from classfile_code_metadata import decode
from pg13139_private_constant_metadata import remove_constant
import pg9666_pagination_static as runner

SOURCE = '703876e73d6ec1bd06229a8b9a119e66d8d99a30'
NORMAL = '1d4bc617cab74a361cb8222a563e8080cc67857546d71525a49d224cb7b6ddb2'
STATIC = '685652b4fc50b1070032b0d6241ba1afdf0e678e106117f83d3f301009116f1e'
OUT = data.BASE/'PG13334-state-oracle-source-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13334-state-oracle-source-post-v1'

def methods(model):
    result = copy.deepcopy(model['methods'])
    for m in result:m.pop('codeLength')
    return sorted(result,key=lambda m:(m['name'],m['descriptor']))

def nonempty(text):return [line for line in text.splitlines() if line.strip()]

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    old = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1])
    n = data.read_checked(data.BASE/'PG13330-state-oracle-v1/manifest.json',NORMAL)
    s = data.read_checked(data.BASE/'PG13332-state-oracle-v1/manifest.json',STATIC)
    p = data.read_checked(data.BASE/'PG13328-state-oracle-preflight-v1/manifest.json','629aeda4f686b04577d45843f7db1c3723c24907b9ff85f605dd7e9c3b0caf45')
    assert n['source'] == s['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == s['actualExit'] == p['actualExit'] == 0
    assert s['spotbugsSixExit'] == 0 and p['diagnosticMultisetUnchanged'] and len(n['jars']) == 6
    hashes = n['begin']['inputHashes'];assert set(hashes) == set(old['begin']['inputHashes'])
    assert {path for path,sha in hashes.items() if old['begin']['inputHashes'][path] != sha} == set(cfg.SPECS)
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    before_main,after_main = jar_classes(old),jar_classes(n);assert before_main == after_main and len(after_main) == 1843
    a,b = test_classes(old),test_classes(n);assert set(a) == set(b) and len(a) == len(b) == 1974
    roots = {path.split('/src/test/java/')[1][:-5]:(path,spec) for path,spec in cfg.SPECS.items()}
    closure = {k for k in b if k[0] == 'web' and any(k[1] == root+'.class' or k[1].startswith(root+'$') for root in roots)}
    changed = {k for k in a if a[k] != b[k]};assert changed and changed <= closure
    models = {};rows = [];source_projections = {};labels = {}
    for path,spec in cfg.SPECS.items():
        text = (data.ROOT/path).read_text();source_projections[path] = source.project(source.tokens(text),spec,source.before(path));labels[path] = source.negatives(text,spec,source.before(path))
    helper_count = switch_count = 0
    for role,entry in sorted(closure):
        x,y = [decode((Path(v['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry) for v in [old,n]]
        assert x['sourceFile'] == y['sourceFile'] and x['flags'] == y['flags'];xm,ym = methods(x),methods(y);kind = 'ORIGINAL_MEMBERS_UNCHANGED'
        root = entry[:-6]
        if root in roots:
            path,spec = roots[root];desc = '(Ldev/codex/schubert/nk/protocol/layout/semantic/'+spec['enum']+';)Ljava/lang/String;'
            added = dict(name=spec['helper'],descriptor=desc,flags=10,hasCode=True)
            assert ym.count(added) == 1 and added not in xm;ym.remove(added)
            assert ym == xm and y['fields'] == x['fields'];kind = 'ONE_PRIVATE_STATIC_ORACLE_HELPER';helper_count += 1
        elif y['fields'] != x['fields']:
            assert x['flags'] & 0x1000 and y['fields'] == x['fields']+1 and ym == xm
            assert [m['name'] for m in ym] == ['<clinit>'];kind = 'JAVAC_SYNTHETIC_ENUM_SWITCH_FIELD';switch_count += 1
        else:assert ym == xm
        models[(role,entry)] = (x,y,kind)
        rows.append(dict(module=role,entry=entry,oldSha256=a[(role,entry)],newSha256=b[(role,entry)],byteChanged=(role,entry) in changed,oldFields=x['fields'],newFields=y['fields'],kind=kind))
    assert helper_count == switch_count == 2
    SLOT.mkdir();runner.SLOT = SLOT;javap = runner.TC/'jdk-25.0.4/bin/javap';javap_sha = data.sha(javap.read_bytes());stages = [];abi = []
    for i,((role,entry),(x,y,kind)) in enumerate(models.items()):
        if kind == 'ORIGINAL_MEMBERS_UNCHANGED':continue
        outputs = []
        for label,value in [('old',old),('new',n)]:
            cp = str(Path(value['jars'][role]['path']).parent/'test-classes');name = str(i)+'-'+label
            stage = runner.step(name,[str(javap),'-p','-constants','-s','-classpath',cp,entry[:-6].replace('/','.')],SLOT,timeout=120)
            assert stage['actualExit'] == 0 and not stage['timedOut'];stages.append(stage);outputs.append((SLOT/(name+'.stdout')).read_text())
        spec = next(v for path,v in cfg.SPECS.items() if Path(path).name == y['sourceFile'])
        enum = 'dev.codex.schubert.nk.protocol.layout.semantic.'+spec['enum']
        if kind == 'ONE_PRIVATE_STATIC_ORACLE_HELPER':
            declaration = 'private static java.lang.String '+spec['helper']+'('+enum+');';descriptor = '(L'+enum.replace('.','/')+';)Ljava/lang/String;'
        else:declaration = 'static final int[] $SwitchMap$'+enum.replace('.','$')+';';descriptor = '[I'
        restored = remove_constant(outputs[1],declaration,descriptor)
        assert nonempty(restored) == nonempty(outputs[0])
        abi.append(dict(entry=entry,removedOnlyAddedMember=declaration,descriptor=descriptor,allOtherPrivatePublicDeclarationsIdentical=True,oldSha256=data.sha(outputs[0].encode()),newSha256=data.sha(outputs[1].encode())))
    assert data.sha(javap.read_bytes()) == javap_sha and jar_classes(n) == after_main and test_classes(n) == b
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL,staticManifestSha256=STATIC,
        preflightManifestSha256='629aeda4f686b04577d45843f7db1c3723c24907b9ff85f605dd7e9c3b0caf45',allMainPhysicalUnchanged=1843,previousTestPhysical=len(a),currentTestPhysical=len(b),changedTestPhysical=len(changed),
        oldTestPhysicalUnchanged=len(a)-len(changed),newTestPhysical=0,sourceFileClosureClasses=len(closure),classMetadata=rows,newPrivateHelperMethods=helper_count,newPrivateFields=0,compilerSwitchFieldsAdded=switch_count,
        privateMetadata=abi,javapSha256=javap_sha,stages=stages,sourceProjections=source_projections,negativeLabels=labels,staticMetadataNegativeVectors=sum(len(v) for v in labels.values()),
        independentUiDomainCases=source.ui_domain(),oracleCallsCorrected=8,rawStatic=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],diagnosticMultisetUnchanged=True,
        productTestsExecuted=0,newTestIds=0,newAccepted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',oldPtQualificationTransferred=False,rawCodeHashIsNotSemanticProof=True,
        wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
