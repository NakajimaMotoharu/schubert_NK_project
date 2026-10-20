"""One necessary coherent3973 after serialized PG and two legal Sync in-flight contracts."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5860_terminal_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='79098cfa553d38cb6032c28d8722394e59c39966';LABEL='PG5886';SLOT='pg5886-terminal-serial-six-v1'
CHANGED_TESTS={'api/messaging/inbound/FatalIsolationFixture','api/messaging/inbound/CommittedTerminalAdmissionContractTest'}
NEW_METHODS={'term005SyncTwoInFlightCommittedCallbacksSignalOnce','term006SyncTwoInFlightIsolationFailuresSignalOnce'}


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5860',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3971:return ast.copy_location(ast.Constant(3973),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<coherent3973 original runner>'):raise ValueError('complete generated namespace')
    if any(s in raw for s in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):raise ValueError('only approved isolated host fixtures')
    compile(raw,'<necessary3973>','exec');return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('PG5860',LABEL).replace('pg5860','pg5886').replace('terminal-six','terminal-serial-six')
    old="'tests': 3971, 'suites': 592, 'mainClasses': 1666"
    if raw.count(old)!=1:raise ValueError('one exact3973 inventory')
    raw=raw.replace(old,"'tests': 3973, 'suites': 592, 'mainClasses': 1666",1)
    a=raw.index("'trigger': ");b=raw.index('}, sort_keys=True)',a)
    trigger='PG-D445/BUG1501: three dedicated single-session terminal decisions simplified under SS321/JMS serialized listener contract; Sync Main unchanged with two new legal independent-context in-flight tests. Prior3971 identities retained plus exact2 cases/no new suite; one test-only fixture supplement, no oracle changes. Selected83 and all851/1666/three physical differences/publicABI/static first. No old PT/native import or held operations.'
    raw=raw[:a]+"'trigger': "+repr(trigger)+raw[b:]
    compile(raw,'<new-only3973 driver>','exec');return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed Main/Test/config')
    p=W/'pg5880-terminal-serial83-v1/manifest.safe.json';v=json.loads(p.read_bytes());base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5882-terminal-serial-static-v1/manifest.json';s=json.loads(sp.read_bytes());private=W/'pg5882-terminal-serial-static-v1/manifest.safe.json'
    if not(v['source']==s['source']==SOURCE and v['actualExit']==s['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(83,22)and not v['failedOrSkipped']and s['selectedManifestSha256']==hashlib.sha256(p.read_bytes()).hexdigest()and s['privateManifestSha256']==hashlib.sha256(private.read_bytes()).hexdigest()and s['physicalMain']==1666 and s['inputSourceFiles']==851 and s['unchangedPhysicalClasses']==1663):raise ValueError('actual same-source83 and independent all-source/three-class/publicABI/static proof')
    changed=set()
    for row in subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines():
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if action!='M'or not path.endswith('.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('no new/removed suite or changed resource')
        changed.add(path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5])
    if changed!=CHANGED_TESTS:raise ValueError('one existing test class/two new cases and finite helper only')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('unchanged build and characterization gate')


def main():
    prerequisites();server_source(SOURCE,'0'*64);runtime=previous.previous.previous.previous.RUNTIME;fresh=runtime.preflight();os.umask(0o077)
    with(W/'pg5886-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(runtime.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<coherent3973>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
