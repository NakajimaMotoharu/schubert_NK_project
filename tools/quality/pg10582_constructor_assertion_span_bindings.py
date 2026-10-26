"""Refine read-only type metadata using original assertion start, never rerun the reader."""
from collections import Counter
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument, lex
from pg10580_remaining_constructor_bindings import owner_matches

OUT = data.BASE/'PG10582-constructor-assertion-span-bindings-v1'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10558-trace-context-final-compile-v1/snapshot'
RAW = data.ROOT.parent/'pgpt-runs/PG379/pg10580-remaining-constructor-bindings-v1/parse-normal-class-bytes.stdout'


def assertion_line(text,row):
    expression = first_argument(text,row)
    values = lex(text)
    candidates = [start for i,(value,start,_) in enumerate(values[:-2])
        if value == row['assertion'] and values[i+1][0] == '(' and values[i+2][1] == expression[0][1]]
    if len(candidates) != 1:
        raise ValueError('one original assertion enclosing first expected argument required')
    return text.count('\n',0,candidates[0])+1


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10580-remaining-constructor-bindings-v1/manifest.json',
        'a9e61e1889b9f51469f28112da46f5df80e47769a679b723f6739896c2bafc8c')
    rows = data.read_checked(data.BASE/'PG10580-remaining-constructor-bindings-v1/constructor-bindings.json',primary['rowsSha256'])
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    assert data.sha(RAW.read_bytes()) == primary['stages'][-1]['stdoutSha256']
    calls = []
    for line in RAW.read_text().splitlines():
        fields = line.split('\t')
        if fields[0] != 'CTOR':
            continue
        _,path,method,number,owner,descriptor = fields
        calls.append(dict(path=path,method=method,line=int(number),owner=owner,descriptor=descriptor))
    mains = {}
    for module,item in normal['jars'].items():
        path = Path(item['path'])
        assert data.sha(path.read_bytes()) == item['sha256']
        with zipfile.ZipFile(path) as jar:
            for entry in jar.namelist():
                if not entry.endswith('.class'):
                    continue
                owner = entry.removesuffix('.class')
                assert owner not in mains
                source = 'src/schubert-nk-'+module+'/src/main/java/'+owner.split('$')[0]+'.java'
                mains[owner] = dict(module=module,physicalClassSha256=data.sha(jar.read(entry)),
                    source=source,sourceSha256=normal['begin']['inputHashes'].get(source))
    selected = []
    for row in rows:
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][row['path']]
        begin = assertion_line(text,row)
        prefix,suffix = row['path'].split('/src/test/java/')
        binary_prefix = prefix+'/target/test-classes/'+suffix.removesuffix('.java')
        files = {p for p in primary['normalPhysicalTestClassesHashes']
            if p == binary_prefix+'.class' or p.startswith(binary_prefix+'$')}
        assert files
        bindings = {}
        for syntax in row['expectedConstructorTypes']:
            matches = [call for call in calls if call['path'] in files
                and (call['method'] == row['method'] or call['method'].startswith('lambda$'+row['method']+'$'))
                and begin <= call['line'] <= row['expectedFinalLine'] and owner_matches(call['owner'],syntax)]
            owners = sorted({call['owner'] for call in matches})
            bindings[syntax] = dict(owners=owners,
                status='EXACT_ASSERTION_TO_EXPECTED_END_UNIQUE_OWNER' if len(owners)==1 else 'UNRESOLVED_TYPE_BINDING_KEEP_PENDING',
                supportingInvocationMetadata=matches,
                mainSourceBinding=mains.get(owners[0]) if len(owners)==1 else None)
        selected.append(dict(row,assertionStartLine=begin,assertionSpanConstructorBindings=bindings))
    assert len(selected) == 168
    counts = Counter(binding['status'] for row in selected for binding in row['assertionSpanConstructorBindings'].values())
    assert sum(counts.values()) == 180
    sample = 'assertEquals(\n new Thing(1), value);'
    row = dict(assertion='assertEquals',line=2,expectedExpressionSha256=data.sha(b'new Thing(1)'))
    assert assertion_line(sample,row) == 1
    rejected = 0
    for damaged in (dict(row,line=1),dict(row,expectedExpressionSha256='0'*64)):
        try:
            assertion_line(sample,damaged)
        except ValueError:
            rejected += 1
    assert rejected == 2
    assert all(data.sha((NORMAL/path).read_bytes()) == value['sha256'] for path,value in primary['normalPhysicalTestClassesHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'constructor-bindings.json',selected)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        priorStrictExpectedSpanManifestSha256='a9e61e1889b9f51469f28112da46f5df80e47769a679b723f6739896c2bafc8c',
        oldStrictBindingCounts=primary['typeBindingCounts'],assertionSpanBindingCounts=dict(counts),
        syntaxSites=168,consumerSources=65,constructorTypeOccurrences=180,metadataNegativeVectors=2,
        rowsSha256=data.sha((OUT/'constructor-bindings.json').read_bytes()),
        reusedOriginalReaderStdoutSha256=data.sha(RAW.read_bytes()),readerReexecuted=False,
        constructorSemanticsOrArgumentProvenanceQualified=False,
        normalPhysicalMainClasses=len(mains),targetCompilation=0,targetClassLoading=0,
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(dict(actualExit=0,counts=dict(counts),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()
