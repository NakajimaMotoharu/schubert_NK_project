"""Reconcile the four-module class graph by the exact CleanupRepository physical delta."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import runpy
import subprocess

HERE = Path(__file__)
G = runpy.run_path(str(HERE.with_name('5189_wbs66_four_module_delta_handoff.py')))
OPS, E, H = G['E'].parent, G['E'], G['D']
P = 'dev.codex.schubert.nk.batch.repository.CleanupRepository'
FILES = {name: name.replace('.', '/') + '.class' for name in (P, P+'$1', P+'$StatementFactory')}
read, write, ref = G['load'], G['write'], G['ref']
sha, analyze, edges = G['sha'], G['analyze'], G['edges']
verified = G['revalidate_reference']


def combined_original(graph, scope):
    old = verified(graph['historicalBaseline'])
    full = Path(graph['historicalBaseline']['path']).with_name('jdeps.stdout.gz')
    assert ref(full)['sha256'] == old['evidence'][full.name]
    delta = Path(graph['rawAnalysis']['path'])
    assert ref(delta) == graph['rawAnalysis']
    removed = set(graph['changedAndNewPhysical']) | set(graph['removed'])
    scope_path = Path(scope['deltaAfter']['stdout']['path'])
    assert ref(scope_path) == scope['deltaAfter']['stdout']
    scope_rows = edges(scope_path.read_text())
    scope_names = {line[0] for line in scope_rows}
    assert scope_names == {'dev.codex.schubert.nk.batch.platform.ProcessResourceScope'}
    original = edges(gzip.decompress(full.read_bytes()).decode())
    until_last = [(a,b,c) for a,b,c in original if a not in removed] + edges(gzip.decompress(delta.read_bytes()).decode())
    return [(a,b,c) for a,b,c in until_last if a not in scope_names] + scope_rows


def invoke(build, names, out):
    workspace = Path(build['cwd'])
    assert workspace.parent == Path('../pgpt-runs/PG379').resolve()
    launcher = Path('../toolchain/jdk-25.0.4/bin/jdeps').resolve()
    assert ref(launcher.with_name('java'))['sha256'] == build['tools']['javaSha256']
    paths = [workspace/'src/schubert-nk-batch/target/classes'/FILES[name] for name in names]
    physical = [ref(p) for p in paths]
    assert all(not p.is_symlink() and pin['sha256']==build['physicalClassHashes']['batch'][FILES[name]]
               for p,pin,name in zip(paths,physical,names,strict=True))
    command = [str(launcher),'-verbose:class','-filter:none','--ignore-missing-deps',*map(str,paths)]
    start = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command,capture_output=True,timeout=30)
    end = datetime.now(timezone.utc).isoformat()
    with (out/'jdeps.stdout.gz').open('xb') as f:
        f.write(gzip.compress(result.stdout,mtime=0))
    receipt = dict(command=command,startedAtUTC=start,terminalAtUTC=end,actualExit=result.returncode,
                   jdeps=ref(launcher),actualPhysical=physical,stdout=ref(out/'jdeps.stdout.gz'),
                   originalStdoutSha256=sha(result.stdout),stderrSha256=sha(result.stderr))
    write(out/'jdeps-command.json',receipt)
    assert result.returncode==0 and not result.stderr
    rows=edges(result.stdout.decode())
    assert {origin for origin,_,_ in rows} == set(names)
    return rows,ref(out/'jdeps-command.json')


def external(rows):
    return {(a,b) for a,b,c in rows if c=='not found' and not b.startswith(G['SOURCE_ROOT'])}


def main():
    start=read(next(H.glob('502_*')))
    v=start['values']
    assert G['git']('rev-parse','HEAD').decode().strip()==v['source']
    out=E/v['run']
    build,prod,scope,graph_proof,third=map(verified,v['oracleReferences'])
    assert prod['productionCoreMain']==build['sourceCore']==v['productionCoreMain']
    assert scope['source']==build['baselineSource'] and build['actualExit']==build['productTestsExecuted']==0
    assert prod['build']==v['oracleReferences'][0] and build['inputHashesReverified']
    old=verified(scope['normalCurrentFourModuleCompile'])
    be,ae=[G['class_owners'](x['physicalClassHashes']) for x in (old,build)]
    assert len(be)==len(ae)==1101
    assert set(be)-set(ae)=={P+'$1'} and set(ae)-set(be)=={P+'$StatementFactory'}
    assert {f for m in old['physicalClassHashes'] for f,k in old['physicalClassHashes'][m].items()
            if k!=build['physicalClassHashes'][m].get(f)}=={FILES[P],FILES[P+'$1']}
    graph=graph_proof['f02PhysicalEdges']
    original=combined_original(graph,scope)
    before=analyze(original,be)
    assert dict(before,externalUnresolved=0)==scope['currentTypedEdgeSummary']
    assert len(external(original))==third['currentReferencePairs']==385
    assert not third['unconfirmedNameReferences'] and not third['ambiguousOrigins']
    assert len(set(original))==len(original)
    assert not [l for l in original if l[1]==P+'$1' and l[0] not in (P,P+'$1')]
    removed=[l for l in original if l[0] in (P,P+'$1')]
    assert {row[0] for row in removed}=={P,P+'$1'}
    new_rows,cmd=invoke(build,(P,P+'$StatementFactory'),out)
    current=[l for l in original if l[0] not in (P,P+'$1')] + new_rows
    after=analyze(current,ae)
    assert len(set(current))==len(current)
    assert len(current)==len(original)-len(removed)+len(new_rows)
    assert before['edges']==after['edges'] and not after['internalUnresolved']
    assert external(original)==external(current)
    assert any(a.endswith('.StorageIoException') and b=='java.sql.SQLException' for a,b,_ in current)
    delta_in=sorted(set(new_rows)-set(removed))
    delta_out=sorted(set(removed)-set(new_rows))
    m=dict(actualExit=0,groupStart=start['eventId'],source=build['sourceCore'],
           priorProofs=v['oracleReferences'],command=cmd,unchangedPhysical=1099,removedPhysical=P+'$1',
           changedPhysical=P,addedPhysical=P+'$StatementFactory',
           before=before,after=after,removedEdges=delta_out,addedEdges=delta_in,
           externalExactPairs=385,externalUnresolvedAfterPriorQualification=0,
           externalThirdPartySetEqual=True,crossModuleSetEqual=True,storageSqlStillOpen=True,
           noProtectedClassReads=True,actualRuntimeActions=0,productTests=0,newBuilds=0,
           wholeF02Accepted=False,whole451Accepted=False,newAcceptance=0,verifier=ref(HERE),
           terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(out/'manifest.json',m)
    print(ref(out/'manifest.json'),before,after)


if __name__=='__main__':
    main()
