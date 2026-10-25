"""Review-frozen source primary/related labels with immutable class metadata; never run targets."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg9360_static_companion_javap_metadata as jdk
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TC=ROOT.parent/'toolchain'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PREFIX='dev/codex/schubert/nk/'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')

def run(library,out,slot,primary_table,prior_name,prior_sha,unique_only):
    invocation=capture(library);assert not out.exists() and not slot.exists()
    graph_dir=BASE/'PG9386-composite-reference-graph-v3'
    graph_raw=(graph_dir/'manifest.json').read_bytes();assert sha(graph_raw)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw);assert graph['source']==SOURCE and graph['actualExit']==0
    for name,key in (('unresolved.json','unresolvedSha256'),('test-class-metadata.json','testMetadataSha256'),('main-class-sources.json','mainMapSha256')):
        assert sha((graph_dir/name).read_bytes())==graph[key]
    originals=json.loads((graph_dir/'unresolved.json').read_bytes());classes=json.loads((graph_dir/'test-class-metadata.json').read_bytes())
    mains=json.loads((graph_dir/'main-class-sources.json').read_bytes())
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json';assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    normal=json.loads(normal_path.read_bytes());hashes=normal['begin']['inputHashes']
    prior_raw=(BASE/prior_name).read_bytes();assert sha(prior_raw)==prior_sha
    prior=json.loads(prior_raw);assert prior['source']==SOURCE and prior['actualExit']==0
    known={row['path'] for row in prior['sourceRows']}
    selected=[row for row in originals if row['path'] not in known and Path(row['path']).stem in primary_table]
    assert len(selected)==len(primary_table) and {Path(row['path']).stem for row in selected}==set(primary_table)
    selected_by_path={row['path']:row for row in selected}
    for row in selected:
        owner=primary_table[Path(row['path']).stem]
        assert owner in row['mainOwners']
        if unique_only:assert row['mainOwners']==[owner] and row['unresolvedReasons']==['REFLECTION_OR_DYNAMIC_CLASS_RESOLUTION']
    by_source=defaultdict(list);by_class=defaultdict(set)
    for row in classes:by_source[row['path']].append(row);by_class[row['className']].add(row['path'])
    closure=set(selected_by_path);pending=list(closure)
    while pending:
        path=pending.pop()
        for row in by_source[path]:
            for name in row['references']:
                if not name.startswith(PREFIX) or name in mains:continue
                same={x['path'] for x in classes if x['module']==row['module'] and x['className']==name}
                dependency=same or by_class[name];assert len(dependency)==1
                dep=next(iter(dependency))
                if dep not in closure:closure.add(dep);pending.append(dep)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};extra={row['path']:row for row in prior['sourceRows']}
    os.umask(0o077);slot.mkdir();receipts=[];independent={};main_refs=set();by_module=defaultdict(list)
    for path in sorted(closure):
        assert hashes[path]==sha((ROOT/path).read_bytes())
        saved=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'/path
        assert sha(saved.read_bytes())==hashes[path]
        for row in by_source[path]:by_module[row['module']].append(row)
    for module,rows in sorted(by_module.items()):
        directory=next(Path(p) for p in graph['treePins'] if '/schubert-nk-'+module+'/' in p)
        for offset in range(0,len(rows),40):
            batch=rows[offset:offset+40]
            argv=[str(TC/'jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(directory)]+[row['className'].replace('/','.') for row in batch]
            start=dt.datetime.now(dt.timezone.utc).isoformat()
            process=subprocess.Popen(argv,cwd=slot,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
            write(slot/(module+'-'+str(offset)+'-process.safe.json'),dict(pid=process.pid,ownerPid=os.getpid(),command=argv,startUTC=start))
            timed_out=False
            try:stdout,stderr=process.communicate(timeout=120)
            except subprocess.TimeoutExpired:timed_out=True;process.kill();stdout,stderr=process.communicate(timeout=15)
            receipt=dict(command=argv,actualExit=process.returncode,timedOut=timed_out,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
              stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
            write(slot/(module+'-'+str(offset)+'-exit.safe.json'),receipt);receipts.append(receipt)
            assert process.returncode==0 and not timed_out and not stderr
            metadata={row['className']:row for row in jdk.parse_metadata(stdout.decode())}
            assert set(metadata)=={row['className'] for row in batch}
            for row in batch:
                item=metadata[row['className']];actual={name for name,_ in item['refs'] if name.startswith(PREFIX)}
                assert item['sourceFile']==row['sourceFile'] and actual=={name for name in row['references'] if name.startswith(PREFIX)}
                assert sha((directory/row['entry']).read_bytes())==row['sha256']
                independent[row['key']]=dict(path=row['path'],className=row['className'],sourceFile=row['sourceFile'],projectClassReferences=sorted(actual),
                  reflectionOrDynamicLookup=row['reflectiveOrDynamicLookup'],classSha256=row['sha256'])
                main_refs.update(actual & mains.keys())
    main_sources={}
    grouped=defaultdict(list)
    for name in sorted(main_refs):grouped[mains[name]['module']].append(name)
    for module,names in sorted(grouped.items()):
        jar=normal['jars'][module];assert sha(Path(jar['path']).read_bytes())==jar['sha256']
        argv=[str(TC/'jdk-25.0.4/bin/javap'),'-p','-classpath',jar['path']]+[name.replace('/','.') for name in names]
        result=subprocess.run(argv,cwd=slot,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=False)
        assert result.returncode==0 and not result.stderr
        sources=[line.removeprefix('Compiled from "').removesuffix('"') for line in result.stdout.decode().splitlines() if line.startswith('Compiled from "')]
        assert sources==[Path(mains[name]['path']).name for name in names]
        receipts.append(dict(command=argv,actualExit=0,stdoutSha256=sha(result.stdout),stderrSha256=sha(result.stderr),rawOutputPersisted=False))
        for name in names:
            path=mains[name]['path'];baseline=logical.get(path)
            expected=(baseline['owner'],baseline['costOwner']) if baseline else (extra[path]['canonicalOwner'],extra[path]['canonicalCostOwner'])
            assert expected==(mains[name]['owner'],mains[name]['owner']) and hashes[path]==sha((ROOT/path).read_bytes())
            main_sources[name]=dict(path=path,owner=mains[name]['owner'],sha256=hashes[path])
    catalog=[]
    for original in sorted(selected,key=lambda row:row['path']):
        path=original['path'];owner=primary_table[Path(path).stem]
        catalog.append(dict(path=path,sha256=hashes[path],owner=owner,costOwner=owner,relatedOwners=sorted(set(original['mainOwners'])-{owner}),
          originalReferenceOwners=original['mainOwners'],unresolvedRuntimeReasons=original['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='FROZEN_LITERAL_SOURCE_PRIMARY_AND_RELATED_SCOPES_RUNTIME_UNCERTAINTY_RETAINED_NOT_PT'))
    verify(invocation);out.mkdir();write(out/'candidates.json',catalog);write(out/'class-proofs.json',independent);write(out/'main-source-proofs.json',main_sources)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      graphManifestSha256=sha(graph_raw),normalManifestSha256=sha(normal_path.read_bytes()),priorManifestSha256=prior_sha,
      frozenPrimaryOwners=primary_table,candidates=len(catalog),verifiedClosureSources=len(closure),independentClassMetadata=len(independent),
      independentMainSourceFiles=len(main_sources),uniqueKnownMainResponsibilityOnly=unique_only,receipts=receipts,
      candidatesSha256=sha((out/'candidates.json').read_bytes()),classProofsSha256=sha((out/'class-proofs.json').read_bytes()),
      mainProofsSha256=sha((out/'main-source-proofs.json').read_bytes()),runtimeUncertaintyPreserved=True,
      targetCompile=0,targetRuntimeClassLoading=0,productTestsExecuted=0,newAccepted=0,newTestIds=0,newMain=0,coverage=None,formalUpdated=False,effortPercent=None)
    write(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,candidates=len(catalog),testClasses=len(independent),mainSourceClasses=len(main_sources),manifestSha256=sha((out/'manifest.json').read_bytes()))))
