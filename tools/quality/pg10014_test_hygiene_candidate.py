"""Host compiler-only Test hygiene candidate; never run Tests or mutate the worktree."""
from collections import Counter
import difflib
import json
import os
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_import_expansion_test import parse, replace_imports
import pg9346_direct_companion_jdk_post as steps
from pg10012_test_hygiene_checkstyle_baseline import HELD

ROOT = data.ROOT
SOURCE = 'bba24d15923831a17e5464328b70fdb950fb2fcf'
SLOT = ROOT.parent/'pgpt-runs/PG379/pg10014-test-hygiene-candidate-v1'
OUT = data.BASE/'PG10014-test-hygiene-candidate-v1'
TC = ROOT.parent/'toolchain'
NORMAL = ROOT.parent/'pgpt-runs/PG379/pg9992-query-pair-six-compile-v1/snapshot'


def path_hash(path):
    if path.is_dir():
        rows = {p.relative_to(path).as_posix():data.sha(p.read_bytes()) for p in sorted(path.rglob('*.class'))}
        return data.sha(json.dumps(rows,sort_keys=True).encode())
    return data.sha(path.read_bytes())


def step(label, command):
    value = steps.step(label,command)
    if value['actualExit'] != 0 or value['timedOut']:
        raise ValueError('finite compiler/format step failed: '+label)
    return value


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    baseline = data.read_checked(data.BASE/'PG10012-test-hygiene-checkstyle-baseline-v1/manifest.json',
        '2ca11b812be3c4feda2b9236eaf6956f38f8e521a5ba2b137865b12c3f7679f2')
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    selected = baseline['selectedSourceHashes']
    assert baseline['actualExit'] == normal['actualExit'] == 0 and baseline['source'] == normal['source'] == SOURCE
    assert len(selected) == 832 and not HELD & set(selected)
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    tools = [ROOT/'tools/quality'/n for n in ('SourceImportExpansion.java','SourceDeclarationExpansion.java','IsolatedSourceOutput.java')]
    formatter = TC/'google-java-format-1.36.1-all-deps.jar'
    checkstyle = TC/'static-gates-20261015/checkstyle-14.3.0-all.jar'
    rule = ROOT/'tools/quality/static/checkstyle.xml'
    tool_hashes = {str(p):data.sha(p.read_bytes()) for p in [*tools,formatter,checkstyle,rule]}
    os.umask(0o077)
    SLOT.mkdir()
    for label in ('original','imported','tool-classes'):
        (SLOT/label).mkdir()
    steps.SLOT = SLOT
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,selected=832,
        heldSourceHashes=baseline['heldSourceHashes'],toolAndRuleHashes=tool_hashes,
        actualProductTests=0,actualExternalActions=0,worktreeModified=False))
    for name,digest in selected.items():
        source = ROOT/name
        assert source.is_file() and not source.is_symlink() and data.sha(source.read_bytes()) == digest
        target = SLOT/'original'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    stages = [step('compile-tools',[str(TC/'jdk-25.0.4/bin/javac'),'-proc:none','-Xlint:all','-Werror',
        '-d',str(SLOT/'tool-classes'),*map(str,tools)])]
    modules = {}
    dependencies = {}
    by_artifact = {Path(v['path']).name:Path(v['path']) for v in normal['jars'].values()}
    for item in normal['jars'].values():
        jar = Path(item['path'])
        assert data.sha(jar.read_bytes()) == item['sha256']
        dependencies[str(jar)] = item['sha256']
        tests_jar = jar.with_name(jar.stem+'-tests.jar')
        if tests_jar.is_file():
            by_artifact[tests_jar.name] = tests_jar
    java = str(TC/'jdk-25.0.4/bin/java')
    imports = 0
    for module,item in normal['jars'].items():
        prefix = f'src/schubert-nk-{module}/src/test/java'
        source_root = SLOT/'original'/prefix
        current_test = NORMAL/f'src/schubert-nk-{module}/target/test-classes'
        assert current_test.is_dir() and source_root.is_dir()
        cpfile = NORMAL/f'src/schubert-nk-{module}/target/pgpt-test-classpath.txt'
        cp = [current_test,Path(item['path'])]
        for value in cpfile.read_text().strip().split(os.pathsep):
            path = Path(value)
            if '/dev/codex/schubert/' in value:
                assert path.name in by_artifact
                path = by_artifact[path.name]
            assert path.is_absolute() and path.exists() and (path.is_relative_to(TC/'m2/repository') or path.is_relative_to(NORMAL))
            cp.append(path)
        cp = list(dict.fromkeys(cp))
        bindings = {str(p):path_hash(p) for p in cp}
        dependencies.update(bindings)
        command = [java,'-Xmx1536m','-cp',str(SLOT/'tool-classes'),'SourceImportExpansion',str(source_root),os.pathsep.join(map(str,cp))]
        stages.append(step(module+'-before-bindings',command))
        before = parse((SLOT/(module+'-before-bindings.stdout')).read_text())
        expected_paths = {p.removeprefix(prefix+'/') for p in selected if p.startswith(prefix+'/')}
        assert set(before) == expected_paths
        for relative,row in before.items():
            raw = (source_root/relative).read_text()
            candidate = replace_imports(raw,row['imports'])
            target = SLOT/'imported'/prefix/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x') as stream:
                stream.write(candidate)
            imports += len(row['imports'])
        modules[module] = dict(prefix=prefix,classpath=cp,classpathHashes=bindings,before=before)
        data.write(SLOT/'progress.safe.json',dict(phase='BEFORE_BINDINGS',completed=list(modules),productTestsExecuted=0))
    stages.append(step('declaration-candidates',[java,'-Xmx1536m','-cp',str(SLOT/'tool-classes'),
        'SourceDeclarationExpansion',str(SLOT/'imported'),str(SLOT/'candidate')]))
    counts = Counter()
    for line in (SLOT/'declaration-candidates.stdout').read_text().splitlines():
        parts = line.split('\t')
        assert len(parts) == 6 and parts[0] == 'CANDIDATE' and parts[1] in selected
        counts.update(dict(zip(('groups','variables','literalTabs','heldGroups'),map(int,parts[2:]))))
    paths = [SLOT/'candidate'/p for p in sorted(selected)]
    stages.append(step('format-candidates',[java,'-Xmx1536m','-jar',str(formatter),'--skip-reflowing-long-strings',
        '--replace',*map(str,paths)]))
    proofs = {}
    for module,item in modules.items():
        stages.append(step(module+'-after-bindings',[java,'-Xmx1536m','-cp',str(SLOT/'tool-classes'),
            'SourceImportExpansion',str(SLOT/'candidate'/item['prefix']),os.pathsep.join(map(str,item['classpath']))]))
        actual = parse((SLOT/(module+'-after-bindings.stdout')).read_text())
        assert set(actual) == set(item['before'])
        for name,row in actual.items():
            assert row['binding'] == item['before'][name]['binding'] and row['declarations'] == item['before'][name]['declarations']
            assert not row['imports']
        assert all(path_hash(Path(p)) == h for p,h in item['classpathHashes'].items())
        proofs[module] = dict(sourceFiles=len(actual),allBindingsAndDeclarationsIdentical=True,
            beforeTsvSha256=data.sha((SLOT/(module+'-before-bindings.stdout')).read_bytes()),
            afterTsvSha256=data.sha((SLOT/(module+'-after-bindings.stdout')).read_bytes()))
        data.write(SLOT/'progress.safe.json',dict(phase='AFTER_BINDINGS',completed=list(proofs),productTestsExecuted=0))
    listing = SLOT/'candidate-sources.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(p)+'\n' for p in paths))
    cs = steps.step('candidate-checkstyle',[java,'-jar',str(checkstyle),'-c',str(rule),'-f','xml',
        '-o',str(SLOT/'candidate-checkstyle.xml'),'@'+str(listing)])
    errors = [n.attrib for n in ET.parse(SLOT/'candidate-checkstyle.xml').getroot().findall('.//error')]
    changed = []
    for name,digest in selected.items():
        path = SLOT/'candidate'/name
        assert path.is_file() and not path.is_symlink()
        original = (ROOT/name).read_text()
        candidate = path.read_text()
        assert original.count('@SuppressWarnings') == candidate.count('@SuppressWarnings')
        assert original.count('NOPMD') == candidate.count('NOPMD')
        current = data.sha(path.read_bytes())
        if current != digest:
            changed.append(dict(path=name,beforeSha256=digest,candidateSha256=current))
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in tool_hashes.items())
    verify(invocation)
    OUT.mkdir()
    (OUT/'candidate-checkstyle.xml').write_bytes((SLOT/'candidate-checkstyle.xml').read_bytes())
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,selectedSourceHashes=selected,
        heldSourceHashes=baseline['heldSourceHashes'],changed=changed,modules=proofs,
        wildcardImportsExpanded=imports,declarationCounts=dict(counts),dependencyHashes=dependencies,
        toolAndRuleHashes=tool_hashes,stages=stages,candidateCheckstyle=cs,candidateCheckstyleFindings=len(errors),
        remainingRuleCounts=dict(Counter(r['source'] for r in errors)),candidateOnly=True,
        mainModified=False,worktreeModified=False,productTestsExecuted=0,externalActions=0,
        newAccepted=0,wholeF03Accepted=False,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,selected=832,changed=len(changed),imports=imports,declarations=dict(counts),
        candidateCheckstyleFindings=len(errors),rawCheckstyleExit=cs['actualExit'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


def emit(batch):
    manifest = json.loads((OUT/'manifest.json').read_bytes())
    assert manifest['actualExit'] == 0 and manifest['candidateOnly'] and 0 <= batch < (len(manifest['changed'])+39)//40
    patch = '*** Begin Patch\n'
    for row in manifest['changed'][batch*40:(batch+1)*40]:
        name = row['path']
        assert '/src/test/java/' in name and name.endswith('.java') and name not in HELD
        current, proposed = ROOT/name,SLOT/'candidate'/name
        assert not current.is_symlink() and not proposed.is_symlink()
        assert data.sha(current.read_bytes()) == row['beforeSha256'] and data.sha(proposed.read_bytes()) == row['candidateSha256']
        delta = list(difflib.unified_diff(current.read_text().splitlines(keepends=True),proposed.read_text().splitlines(keepends=True)))
        assert delta and all(line.endswith('\n') for line in delta)
        patch += '*** Update File: '+str(current)+'\n'
        for line in delta[2:]:
            patch += '@@\n' if line.startswith('@@') else line
    print(patch+'*** End Patch\n',end='')


if __name__ == '__main__':
    if not sys.argv[1:]:
        main()
    elif len(sys.argv) == 3 and sys.argv[1] == '--emit-batch' and sys.argv[2].isdigit():
        emit(int(sys.argv[2]))
    else:
        raise ValueError('no-argument isolated candidate or explicit known patch batch only')
