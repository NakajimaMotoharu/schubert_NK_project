"""Existing runtime841 retirement only after independently attested completed-failed recovery.
Compile/stage/retire each new-only; no start, stop, DB update or original mutation.
"""
import ast,json,sys
from pathlib import Path
import pg815_retirement_sources as old
import pg815_retirement_compile as compiler
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
DIGEST='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'
def before():
    r=json.loads((W/'pg859-completed-failed-post-v1.safe.json').read_text())
    assert r['actualExit']==0 and r['all24Preserved'] and r['M_A0'] and r['databaseClient0'] and r['sameEpochInvalid']
    assert r['source']==SOURCE and r['batchRows']==564 and r['startupEntries']==47
    return r['snapshotSha256']
def bind(raw):
    from pg856_sources import bind as cohort
    raw=cohort(raw)
    for a,b in [('Pg815','Pg860'),('PG815','PG860'),('pg815','pg860'),('pg805-once-resume.conf','pg841-once-resume.conf'),('pg814-recovered949-post-v1','pg859-completed-failed-post-v1'),(old.SNAPSHOT,before()),('pg856-failed-done-tools-v1','pg856-failed-done-tools-v2'),('pg856-failed-done-recovery-v1','pg856-failed-done-recovery-v2')]:raw=raw.replace(a,b)
    raw=raw.replace('==554','==564').replace('== 554','== 564').replace('originalPendingUnchanged','originalCompletedUnchanged')
    fields='Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL,TimeoutStartUSec,TimeoutStopUSec,ExecStart,ExecStop,User,Group,SupplementaryGroups,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictAddressFamilies,ReadWritePaths,ReadOnlyPaths,Requires,After,FragmentPath,DropInPaths'
    return raw.replace(fields,fields+',RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')
def java():return bind(old.java())
def java_test():return bind(old.java_test())
def snapshot_library():return bind(old.snapshot_library())
def helper():return bind(old.helper())
def sources():
    result={'Pg860RuntimeRetirement.java':java(),'Pg860RuntimeRetirementTest.java':java_test(),'pg860_runtime_retirement_refs.py':helper(),'pg860_snapshot.py':snapshot_library()}
    for name in ('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):result[name]=(R/name).read_text()
    result['pg777_reference_capability.py']=(W/'pg856-failed-done-tools-v2/pg777_reference_capability.py').read_text()
    return result
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1]in ('compile','stage','retire')
    SNAPSHOT=before()
    if sys.argv[1]=='compile':
        raw=bind(compiler.source()).replace('import pg860_retirement_sources as p','import pg860_retirement as p').replace('pg860_retirement_test.py','pg860_retirement_test.py')
    else:raw=bind((R/'pg815_retirement_native.py').read_text())
    ast.parse(raw)
    exec(compile(raw,'<860 normal existing841 retirement dispatch>', 'exec'),{'__file__':str(R/'pg860_retirement.py'),'__name__':'__main__','sources':sources})
