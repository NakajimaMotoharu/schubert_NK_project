"""Necessary coherent3967 once after SS322 isolation PG; ordinary host fixtures only."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5808_rollback_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='6b5cea563b6f68b0b604afc06490063793e49662'
LABEL='PG5832';SLOT='pg5832-isolation-six-v1'
NEW_TESTS={
 'protocol/transport/FailedJmsIsolationExceptionTest',
 'api/messaging/inbound/FatalIsolationConsumersContractTest',
 'web/messaging/ReplyFatalIsolationContractTest'}
HELPER='api/messaging/inbound/FatalIsolationFixture'
CHANGED_TESTS={
 'api/messaging/inbound/InboundTransactionsPrimaryContractTest',
 'api/messaging/inbound/SyncRequestListenerTest',
 'web/messaging/ReplyIsolationPrimaryContractTest',
 'web/messaging/ArtemisReplyConsumerTest'}


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5808',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3955,587,1665):return ast.copy_location(ast.Constant({3955:3967,587:590,1665:1666}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<coherent3967 original runner>'):raise ValueError('full emitted namespace static0')
    if any(s in raw for s in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):raise ValueError('held operations prohibited; normal host fixture profile only')
    compile(raw,'<one necessary3967>','exec');return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('PG5808',LABEL).replace('pg5808','pg5832').replace('rollback-six','isolation-six')
    old="'tests': 3955, 'suites': 587, 'mainClasses': 1665"
    if raw.count(old)!=1:raise ValueError('one planned physical inventory')
    raw=raw.replace(old,"'tests': 3967, 'suites': 590, 'mainClasses': 1666",1)
    a=raw.index("'trigger': ");b=raw.index('}, sort_keys=True)',a)
    trigger='BUG1494/SS322 permanent isolation failure: four groups stop without ACK despite confirmed rollback; retain protocol/isolation/unknown rollback. Selected66 and all851/1666 static/ABI delta proof first. Exact12 new cases/three suites, one test-only fixture, four old identity-preserving cause oracle supplements. All original3955 case identities retained; no old PT/native or held operation import.'
    raw=raw[:a]+"'trigger': "+repr(trigger)+raw[b:]
    compile(raw,'<new-only3967 driver>','exec');return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical Main/Test/config')
    selected=W/'pg5828-isolation-selected66-v1/manifest.safe.json';v=json.loads(selected.read_bytes())
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';p=base/'PG5830-isolation-static-v1/manifest.json';s=json.loads(p.read_bytes());private=W/'pg5830-isolation-static-v1/manifest.safe.json'
    if not(v['source']==s['source']==SOURCE and v['actualExit']==s['actualExit']==0 and v['selectedQualified']and(v['tests'],v['suites'])==(66,18)and not v['failedOrSkipped']and s['selectedManifestSha256']==hashlib.sha256(selected.read_bytes()).hexdigest()and s['privateManifestSha256']==hashlib.sha256(private.read_bytes()).hexdigest()and s['physicalMain']==1666 and s['inputSourceFiles']==851 and s['unchangedPhysicalClasses']==1659):raise ValueError('actual same-source66 and independent source/class/ABI/static proof first')
    rows=subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();changed=set();added=set()
    for row in rows:
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('original test resources unchanged')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5]
        if action not in('M','A'):raise ValueError('no removed Test identity')
        (changed if action=='M'else added).add(key)
    if changed!=CHANGED_TESTS or added!=NEW_TESTS|{HELPER}:raise ValueError('exact four oracle supplements and three suites/one finite helper')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('build/characterization gates unchanged')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.previous.RUNTIME.preflight();os.umask(0o077)
    with(W/'pg5832-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.previous.RUNTIME.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one coherent isolation3967>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
