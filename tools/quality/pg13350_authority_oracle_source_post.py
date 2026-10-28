"""Independent source/physical/member binding for authority oracles, no target class initialization."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13340_authority_oracle_config as cfg
import f03_authority_oracle_sources_v2 as source
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg13334_state_oracle_source_post import methods,nonempty
from classfile_code_metadata import decode
from pg13139_private_constant_metadata import remove_constant
import pg9666_pagination_static as runner

SOURCE = 'b95a31982a8a6066a9608e56af5fd17d5665576e'
NORMAL = '310c52175ecb38fdab18ec14e791e0b240a38295e346322cfedad7b317d25de9'
OUT = data.BASE/'PG13350-authority-oracle-source-post-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13350-authority-oracle-source-post-v1'
ENUM = 'dev.codex.schubert.nk.protocol.layout.semantic.UserRole'
PRINCIPAL = 'dev.codex.schubert.nk.web.session.SessionPrincipal'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    old = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1])
    n = data.read_checked(data.BASE/'PG13346-authority-oracle-v1/manifest.json',NORMAL)
    plan = data.read_checked(data.BASE/'PG13343-authority-oracle-plan-v2/manifest.json','6c80c0be7cacc06a949e5fd6ddfe8e5afddd0c769f0bb61e5931d2f00059372d')
    p = data.read_checked(data.BASE/'PG13344-authority-oracle-preflight-v1/manifest.json','70b22623fd38efb3ed1185a3eb6e1bc3c30eb466e2dd476f7ed2465425929353')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0 and p['onlySpecifiedDuplicateLiteralRemoved']
    hashes = n['begin']['inputHashes'];assert set(hashes) == set(old['begin']['inputHashes'])
    assert {path for path,sha in hashes.items() if old['begin']['inputHashes'][path] != sha} == set(cfg.SPECS)
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(hashes[path] == sha for path,sha in plan['protectedSourceHashes'].items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    before_main,after_main = jar_classes(old),jar_classes(n);assert before_main == after_main and len(after_main) == 1843
    a,b = test_classes(old),test_classes(n);added = set(b)-set(a);assert not set(a)-set(b) and len(a) == 1974 and len(b) == 1978 and len(added) == 4
    roots = {path.split('/src/test/java/')[1][:-5]:path for path in cfg.SPECS}
    closure = {k for k in b if k[0] == 'web' and any(k[1] == root+'.class' or k[1].startswith(root+'$') for root in roots)}
    changed = {k for k in a if a[k] != b[k]};assert changed <= closure and added <= closure and len(closure) == 59
    source_projections = {};labels = {};models = {};rows = []
    for path,spec in cfg.SPECS.items():
        text = (data.ROOT/path).read_text();source_projections[path] = source.project(source.tokens(text),spec,source.before(path));labels[path] = source.negatives(text,spec,source.before(path))
    helpers = fields = 0
    for role,entry in sorted(closure):
        y = decode((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);ym = methods(y)
        assert y['sourceFile'] in {Path(path).name for path in cfg.SPECS}
        if (role,entry) in added:
            assert y['flags'] == 4128 and y['fields'] == 1 and ym == [dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True)]
            x = None;kind = 'NEW_JAVAC_SYNTHETIC_ROLE_SWITCH_CLASS'
        else:
            x = decode((Path(old['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
            assert x['sourceFile'] == y['sourceFile'] and x['flags'] == y['flags']
            if entry[:-6] in roots:
                helper = dict(name=cfg.HELPER,descriptor='(L'+PRINCIPAL.replace('.','/')+';)Ljava/lang/String;',flags=10,hasCode=True)
                assert ym.count(helper) == 1 and helper not in methods(x);ym.remove(helper)
                assert y['fields'] == x['fields']+2;helpers += 1;fields += 2;kind = 'TWO_PRIVATE_CONSTANTS_ONE_PRIVATE_HELPER'
            else:assert y['fields'] == x['fields'];kind = 'ORIGINAL_MEMBER_SHAPES_UNCHANGED'
            assert ym == methods(x)
        models[(role,entry)] = (x,y,kind)
        rows.append(dict(module=role,entry=entry,oldSha256=a.get((role,entry)),newSha256=b[(role,entry)],byteChanged=(role,entry) in changed or (role,entry) in added,oldFields=None if x is None else x['fields'],newFields=y['fields'],kind=kind))
    assert helpers == 6 and fields == 12 and len(changed) == 55
    SLOT.mkdir();runner.SLOT = SLOT;javap = runner.TC/'jdk-25.0.4/bin/javap';javap_sha = data.sha(javap.read_bytes());stages = [];abi = []
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL,sourceInputHashes=hashes,newTestPhysical=sorted(added),classMetadata=rows,javapSha256=javap_sha,productTestsExecuted=0))
    for i,((role,entry),(x,y,kind)) in enumerate(models.items()):
        if kind == 'ORIGINAL_MEMBER_SHAPES_UNCHANGED':continue
        outputs = {}
        for label,value in [('old',old),('new',n)]:
            if label == 'old' and x is None:continue
            cp = str(Path(value['jars'][role]['path']).parent/'test-classes');name = str(i)+'-'+label
            stage = runner.step(name,[str(javap),'-p','-constants','-s','-classpath',cp,entry[:-6].replace('/','.')],SLOT,timeout=120)
            assert stage['actualExit'] == 0 and not stage['timedOut'];stages.append(stage);outputs[label] = (SLOT/(name+'.stdout')).read_text()
        removed = []
        if x is None:
            expected = ['Compiled from '+json.dumps(y['sourceFile']),'class '+entry[:-6].replace('/','.')+' {','  static final int[] $SwitchMap$'+ENUM.replace('.','$')+';','    descriptor: [I','  static {};','    descriptor: ()V','}']
            assert nonempty(outputs['new']) == expected
        else:
            restored = outputs['new'];declarations = [('private static final java.lang.String '+name+' = '+json.dumps(value)+';','Ljava/lang/String;') for name,value in cfg.FIELDS.values()]
            declarations.append(('private static java.lang.String '+cfg.HELPER+'('+PRINCIPAL+');','(L'+PRINCIPAL.replace('.','/')+';)Ljava/lang/String;'))
            for declaration,descriptor in declarations:restored = remove_constant(restored,declaration,descriptor);removed.append(dict(declaration=declaration,descriptor=descriptor))
            assert nonempty(restored) == nonempty(outputs['old'])
        abi.append(dict(entry=entry,removedOnlyAddedMembers=removed,allOtherPrivatePublicDeclarationsIdentical=(x is not None),newSyntheticClassExactlyBound=(x is None),outputSha256={label:data.sha(text.encode()) for label,text in outputs.items()}))
    assert data.sha(javap.read_bytes()) == javap_sha and jar_classes(n) == after_main and test_classes(n) == b
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL,preflightManifestSha256='70b22623fd38efb3ed1185a3eb6e1bc3c30eb466e2dd476f7ed2465425929353',
        allMainPhysicalUnchanged=1843,previousTestPhysical=len(a),currentTestPhysical=len(b),changedTestPhysical=len(changed),oldTestPhysicalUnchanged=len(a)-len(changed),newTestPhysical=len(added),newTestClassEntries=sorted(added),sourceFileClosureClasses=len(closure),classMetadata=rows,
        newPrivateHelperMethods=helpers,newPrivateFields=fields,newCompilerSwitchClasses=4,existingCompilerSwitchClassesUnchangedFieldShape=2,privateMetadata=abi,javapSha256=javap_sha,stages=stages,sourceProjections=source_projections,negativeLabels=labels,
        staticMetadataNegativeVectors=sum(len(v) for v in labels.values()),independentSsDomainCases=source.ss_domain(),oracleCallsCorrected=7,rawStatic=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],onlySpecifiedDuplicateLiteralRemoved=True,removedFinding=cfg.REMOVED_FINDING,
        protectedSourceHashes=plan['protectedSourceHashes'],productTestsExecuted=0,newTestIds=0,newAccepted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',oldPtQualificationTransferred=False,rawCodeHashIsNotSemanticProof=True,unresolvedR09AcceptanceOwnership='UNKNOWN_UNCHANGED_NOT_SOURCE_OWNER_INFERRED',
        wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
