"""Bounded same-source class metadata graph; unique responsibility candidates only, not PT."""
from collections import Counter,defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import class_reference_metadata as parser
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9386-composite-reference-graph-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PREFIX='dev/codex/schubert/nk/'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def tree(directory):
    return {str(path.relative_to(directory)):sha(path.read_bytes()) for path in sorted(directory.rglob('*')) if path.is_file()}
def tree_digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__));assert not OUT.exists();vector_count=parser.vectors()
    inputs={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'prior':('PG9374-inherited-companion-join-v1/manifest.json','0f2cfc89eb1750dd6a6ba220a721554ee6388c5441aec6775e40028b5dd0d0aa'),
      'fixtures':('PG9358-static-companion-compile55-v1/manifest.json','1e6283063e08ae26c4abe5b9cd2d4eb4fce69a45365c4aae14b996641f61d751'),
      'physical':('PG9252-web-life-lock-trace-v1/manifest.json','70f008f4256751e5bf4ecc0baa9e398dc715643cbbff8eb1380927fbfb7d49b6')}
    proofs={}
    for key,(path,digest) in inputs.items():
        raw=(BASE/path).read_bytes();assert sha(raw)==digest;proofs[key]=json.loads(raw)
        assert proofs[key]['source']==SOURCE and proofs[key]['actualExit']==0
    normal=proofs['normal'];prior=proofs['prior'];hashes=normal['begin']['inputHashes']
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};known={row['path']:row for row in prior['sourceRows']}
    source_paths={path for path in hashes if path.startswith('src/schubert-nk-') and path.endswith('.java') and '/src/' in path and '/java/' in path}
    assert len(source_paths)==1789
    test_paths={path for path in source_paths if '/src/test/java/' in path};main_paths=source_paths-test_paths
    unknown=sorted(test_paths-set(logical)-set(known));assert len(unknown)==338 and len(test_paths)==824
    for path in source_paths:
        assert sha((ROOT/path).read_bytes())==hashes[path]
        saved=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'/path
        assert saved.is_file() and sha(saved.read_bytes())==hashes[path]
    main_classes={};test_classes={};by_test_class=defaultdict(set);by_source=defaultdict(list)
    for module,jar in sorted(normal['jars'].items()):
        jar_path=Path(jar['path']);assert sha(jar_path.read_bytes())==jar['sha256']
        with zipfile.ZipFile(jar_path) as archive:
            for entry in archive.namelist():
                if not entry.endswith('.class'):continue
                raw=archive.read(entry);assert sha(raw)==proofs['physical']['physicalClasses'][module+':'+entry]
                parsed=parser.read(raw);class_name=parsed['className']
                assert class_name+'.class'==entry and class_name not in main_classes
                package=class_name.rpartition('/')[0]
                path='src/schubert-nk-'+module+'/src/main/java/'+package+'/'+parsed['sourceFile']
                assert path in main_paths
                row=logical.get(path);expected=(row['owner'],row['costOwner']) if row else (known[path]['canonicalOwner'],known[path]['canonicalCostOwner'])
                assert expected[0] and expected[0]==expected[1]
                main_classes[class_name]=dict(module=module,path=path,owner=expected[0],sha256=sha(raw))
    assert len(main_classes)==1843
    trees={}
    for directory,pin in sorted(proofs['fixtures']['begin']['borrowedFixtureClassDirectories'].items()):
        root=Path(directory);module=root.parent.parent.name.removeprefix('schubert-nk-');files=tree(root)
        assert len(files)==pin['fileCount'] and tree_digest(files)==pin['treeSha256'];trees[directory]=pin
        for entry,digest in files.items():
            if not entry.endswith('.class'):continue
            parsed=parser.read((root/entry).read_bytes());class_name=parsed['className'];assert class_name+'.class'==entry
            path='src/schubert-nk-'+module+'/src/test/java/'+class_name.rpartition('/')[0]+'/'+parsed['sourceFile']
            assert path in test_paths
            key=module+':'+class_name;assert key not in test_classes
            row=dict(key=key,module=module,entry=entry,className=class_name,sourceFile=parsed['sourceFile'],path=path,sha256=digest,
              references=parsed['references'],reflectiveOrDynamicLookup=parsed['reflectiveOrDynamicLookup'])
            test_classes[key]=row;by_test_class[class_name].add(path);by_source[path].append(row)
    assert set(by_source)==test_paths
    direct={path:set() for path in test_paths};edges={path:set() for path in test_paths};held={path:set() for path in test_paths}
    for key,row in test_classes.items():
        path=row['path']
        if row['reflectiveOrDynamicLookup']:held[path].add('REFLECTION_OR_DYNAMIC_CLASS_RESOLUTION')
        for name in row['references']:
            if not name.startswith(PREFIX):continue
            if name in main_classes:
                direct[path].add(main_classes[name]['owner']);continue
            own=test_classes.get(row['module']+':'+name)
            matches={own['path']} if own else by_test_class.get(name,set())
            if len(matches)!=1:held[path].add('UNRESOLVED_OR_DUPLICATE_PROJECT_REFERENCE:'+name)
            elif path not in matches:edges[path].update(matches)
    owner_sets,hold_sets=parser.source_closure(direct,edges,held)
    candidates=[];unresolved=[]
    for path in unknown:
        owners=sorted(owner_sets[path]);reasons=sorted(hold_sets[path])
        row=dict(path=path,sha256=hashes[path],mainOwners=owners,unresolvedReasons=reasons,directMainOwners=sorted(direct[path]),
          helperSourceDependencies=sorted(edges[path]),witnessClasses=sorted(item['key'] for item in by_source[path]))
        if len(owners)==1 and not reasons:
            row.update(owner=owners[0],costOwner=owners[0],status='STRUCTURAL_SINGLE_PRIMARY_CANDIDATE_REVIEW_REQUIRED_NOT_ACCEPTED')
            candidates.append(row)
        else:row['status']='KEEP_UNREGISTERED';unresolved.append(row)
    for directory,pin in trees.items():assert tree_digest(tree(Path(directory)))==pin['treeSha256']
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    write(OUT/'main-class-sources.json',main_classes);write(OUT/'test-class-metadata.json',list(test_classes.values()))
    write(OUT/'candidates.json',candidates);write(OUT/'unresolved.json',unresolved)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,inputs=inputs,
      classReaderAndGraphVectors=vector_count,originalUnknownSources=338,mainClasses=1843,testClasses=len(test_classes),testSources=824,
      proposedCandidates=len(candidates),unresolved=len(unresolved),candidateOwners=dict(Counter(row['owner'] for row in candidates)),
      treePins=trees,mainMapSha256=sha((OUT/'main-class-sources.json').read_bytes()),testMetadataSha256=sha((OUT/'test-class-metadata.json').read_bytes()),
      candidatesSha256=sha((OUT/'candidates.json').read_bytes()),unresolvedSha256=sha((OUT/'unresolved.json').read_bytes()),
      productTestsExecuted=0,targetCompile=0,targetRuntimeClassLoading=0,newTestIds=0,newMain=0,newAccepted=0,coverage=None,
      actualRegistered=0,formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,candidates=len(candidates),unresolved=len(unresolved),owners=value['candidateOwners'],manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
