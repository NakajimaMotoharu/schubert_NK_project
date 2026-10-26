"""Read constructor symbols in exact normal class bytes; no target class loading or PT."""
from collections import Counter
from pathlib import Path
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument

SOURCE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10558-trace-context-final-compile-v1/snapshot'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10580-remaining-constructor-bindings-v1'
OUT = data.BASE/'PG10580-remaining-constructor-bindings-v1'


def key(row):
    return tuple(row[k] for k in ('path','method','line','expectedExpressionSha256'))


def owner_matches(owner,syntax):
    actual = owner.replace('/','.').replace('$','.')
    return actual == syntax or actual.endswith('.'+syntax)


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    origin = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    all_rows = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',origin['sitesJsonSha256'])
    done = set()
    pins = {
        'PG10520-constructor-carrier-review-v3':('de115abc7337ea95939b3fc80360882f250b5d3b977596b179c815a6590afa23','sites.json','sitesSha256'),
        'PG10574-jdk-expected-contexts-v1':('e6444600194163bafccbd61dbb6c77f0cd1122ab12bd627cfaa01b9128a5a819','reviewed-sites.json','reviewedSitesSha256'),
        'PG10330-wire-helper-context-v1':('3adecef2effbdf4d4940ff60e130491f08de3db773f677ec0d1acf0bdd46021d','reviewed-sites.json','reviewedSitesSha256'),
        'PG10362-golden-helper-context-v1':('5082a9445528742cda2184924d73aae9cab2dbc7475fd73a1a314fc62362c6c6','reviewed-sites.json','reviewedSitesSha256'),
        'PG10364-byte-response-helper-context-v1':('76b4e4560b6070bb477b04dbf48d603781ef9c2dc6a4ea9acf7c1204f43dcfa2','reviewed-sites.json','reviewedSitesSha256')}
    for name,(pin,file,field) in pins.items():
        manifest = data.read_checked(data.BASE/name/'manifest.json',pin)
        done.update(key(r) for r in data.read_checked(data.BASE/name/file,manifest[field]))
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    selected = [r for r in all_rows if r['expectedConstructorTypes'] and key(r) not in done
        and data.sha((data.ROOT/r['path']).read_bytes()) == r['sourceSha256']]
    sources = {r['path']:r['sourceSha256'] for r in selected}
    assert len(selected) == 168 and len(sources) == 65
    physical = {}
    source_classes = {}
    for path,digest in sources.items():
        assert normal['begin']['inputHashes'][path] == data.sha((NORMAL/path).read_bytes()) == digest
        prefix,suffix = path.split('/src/test/java/')
        directory = NORMAL/prefix/'target/test-classes'/Path(suffix).parent
        outer = directory/(Path(path).stem+'.class')
        files = [outer,*sorted(directory.glob(Path(path).stem+'$*.class'))]
        source_classes[path] = []
        for file in files:
            assert file.is_file() and not file.is_symlink()
            relative = str(file.relative_to(NORMAL))
            model = decode(file.read_bytes(),str(file.relative_to(NORMAL/prefix/'target/test-classes')))
            assert model['sourceFile'] == Path(path).name
            physical[relative] = dict(sha256=data.sha(file.read_bytes()),sourceFile=Path(path).name)
            source_classes[path].append(relative)
    helper = data.ROOT/'tools/quality/architecture/ExpectedConstructorBindings.java'
    helper_text = helper.read_text()
    assert all(marker not in helper_text for marker in ('Class.forName','getDeclared','MethodHandle','ClassLoader','newInstance','invokeExact'))
    helper_sha = data.sha(helper.read_bytes())
    SLOT.mkdir(mode=0o700)
    reader = SLOT/'reader'
    reader.mkdir()
    listing = SLOT/'fixed-class-files.tsv'
    with listing.open('x') as stream:
        stream.write(''.join(path+'\t'+row['sourceFile']+'\n' for path,row in sorted(physical.items())))
    listing_sha = data.sha(listing.read_bytes())
    steps.SLOT = SLOT
    tc = data.ROOT.parent/'toolchain/jdk-25.0.4/bin'
    stages = [steps.step('compile-reader',[str(tc/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(reader),str(helper)])]
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    stages.append(steps.step('parse-normal-class-bytes',[str(tc/'java'),'-cp',str(reader),helper.stem,str(NORMAL),str(listing)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    declarations,constructors = {},[]
    lines = (SLOT/'parse-normal-class-bytes.stdout').read_text().splitlines()
    for line in lines[:-1]:
        fields = line.split('\t')
        if fields[0] == 'CLASS':
            _,path,name,source,digest = fields
            assert path in physical and digest == physical[path]['sha256'] and source == physical[path]['sourceFile']
            assert path not in declarations
            declarations[path] = name
        else:
            kind,path,method,number,owner,descriptor = fields
            assert kind == 'CTOR' and path in physical
            constructors.append(dict(path=path,method=method,line=int(number),owner=owner,descriptor=descriptor))
    assert lines[-1] == 'SUMMARY\t'+str(len(physical))+'\t'+str(len(constructors))
    assert set(declarations) == set(physical)
    results = []
    for row in selected:
        text = (data.ROOT/row['path']).read_text()
        expression = first_argument(text,row)
        final_line = text.count('\n',0,expression[-1][2])+1
        bindings = {}
        for syntax in row['expectedConstructorTypes']:
            calls = [call for call in constructors if call['path'] in source_classes[row['path']]
                and (call['method'] == row['method'] or call['method'].startswith('lambda$'+row['method']+'$'))
                and row['line'] <= call['line'] <= final_line and owner_matches(call['owner'],syntax)]
            owners = sorted({call['owner'] for call in calls})
            bindings[syntax] = dict(owners=owners,status='EXACT_METHOD_EXPECTED_SPAN_UNIQUE_OWNER' if len(owners)==1 else 'UNRESOLVED_TYPE_BINDING_KEEP_PENDING')
        results.append(dict(row,expectedFinalLine=final_line,constructorBindings=bindings,
            constructorSemanticsReviewed=False,argumentOriginsReviewed=False))
    assert all(data.sha((NORMAL/path).read_bytes()) == row['sha256'] for path,row in physical.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in sources.items())
    assert data.sha(helper.read_bytes()) == helper_sha and data.sha(listing.read_bytes()) == listing_sha
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'constructor-bindings.json',results)
    counts = Counter(binding['status'] for row in results for binding in row['constructorBindings'].values())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        syntaxSites=168,consumerSources=65,normalPhysicalTestClasses=len(physical),
        parsedConstructorInvocations=len(constructors),typeBindingCounts=dict(counts),
        rowsSha256=data.sha((OUT/'constructor-bindings.json').read_bytes()),sourceHashes=sources,
        normalPhysicalTestClassesHashes=physical,readerHelperSha256=helper_sha,inputListSha256=listing_sha,
        readerRuntimeClasspathOnly=str(reader),normalTargetsOnRuntimeClasspath=False,
        targetClassLoading=0,targetCompilation=0,productTestsExecuted=0,externalActions=0,
        symbolBindingsAreNotConstructorOrOracleQualification=True,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(dict(actualExit=0,sites=168,sources=65,typeBindings=dict(counts),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()
