"""Necessary coherent3971 after SS322 committed-terminal PG; approved isolated host fixtures."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5832_isolation_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='a46c781e9ec0260f0297fd6a8c4de39c73e9257c'
LABEL='PG5860';SLOT='pg5860-terminal-six-v1'
NEW_TESTS={'api/messaging/inbound/CommittedTerminalAdmissionContractTest','web/messaging/ReplyCommittedTerminalAdmissionContractTest'}
CHANGED_TESTS={'api/messaging/inbound/FatalIsolationFixture','api/messaging/inbound/ApiConsumerTerminalRemainderTest','api/messaging/inbound/SyncRequestConsumersTest','api/messaging/inbound/WebLogConsumersTest','web/messaging/ReplyRollbackSignalContractTest','web/messaging/ArtemisReplyConsumersTest'}


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5832',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3967,590):return ast.copy_location(ast.Constant({3967:3971,590:592}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<coherent3971 original runner>'):raise ValueError('complete generated namespace')
    if any(s in raw for s in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):raise ValueError('held operations prohibited')
    compile(raw,'<necessary3971>','exec');return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('PG5832',LABEL).replace('pg5832','pg5860').replace('isolation-six','terminal-six')
    old="'tests': 3967, 'suites': 590, 'mainClasses': 1666"
    if raw.count(old)!=1:raise ValueError('one declared inventory')
    raw=raw.replace(old,"'tests': 3971, 'suites': 592, 'mainClasses': 1666",1)
    a=raw.index("'trigger': ");b=raw.index('}, sort_keys=True)',a)
    trigger='BUG1501/SS322 committed isolation must halt four receiver groups; selected81 and independent all851/1666 static/ABI proof first. Four new independent terminal-admission cases, one fixture supplement and five SS-derived old terminal oracle corrections (BUG1503). Eight prior protocol-expression physical differences are also included in this source. Retain all original3967 identities; no old PT/native import and no held runtime operations.'
    raw=raw[:a]+"'trigger': "+repr(trigger)+raw[b:]
    compile(raw,'<new-only3971 driver>','exec');return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical Main/Test/config')
    selected=W/'pg5856-terminal-selected81-v3/manifest.safe.json';v=json.loads(selected.read_bytes())
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5858-terminal-static-v1/manifest.json';s=json.loads(sp.read_bytes());private=W/'pg5858-terminal-static-v1/manifest.safe.json'
    if not(v['source']==s['source']==SOURCE and v['actualExit']==s['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(81,22)and not v['failedOrSkipped']and s['selectedManifestSha256']==hashlib.sha256(selected.read_bytes()).hexdigest()and s['privateManifestSha256']==hashlib.sha256(private.read_bytes()).hexdigest()and s['physicalMain']==1666 and s['inputSourceFiles']==851):raise ValueError('actual same-source81/source/class/ABI/static proof first')
    changed=set();added=set()
    for row in subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines():
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('.java')or'/src/test/java/dev/codex/schubert/nk/'not in path or action not in('M','A'):raise ValueError('no removed test or changed resource')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5]
        (changed if action=='M'else added).add(key)
    if changed!=CHANGED_TESTS or added!=NEW_TESTS:raise ValueError('exact four new cases and six declared Test/fixture supplements')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('build/characterization gates unchanged')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.previous.previous.RUNTIME.preflight();os.umask(0o077)
    with(W/'pg5860-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.previous.previous.RUNTIME.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<coherent terminal3971>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
