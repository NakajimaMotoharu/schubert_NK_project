"""One necessary coherent3955 same-source host campaign after rollback PG; no guest actions."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5780_jms_primary_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='9b80cc9540ff9b23ce45ee0c6893141db407be18'
LABEL='PG5808';SLOT='pg5808-rollback-six-v1'
PROOFS={
 'PG5802-rollback54-v1/manifest.json':'PENDING_ACTUAL_RESULT',
 'PG5804-rollback-static-v1/manifest.json':'PENDING_ACTUAL_RESULT'}
CHANGED_TESTS={
 'api/messaging/inbound/InboundTransactionsPrimaryContractTest',
 'api/messaging/inbound/SyncRequestListenerTest',
 'api/messaging/inbound/ApiConsumerTerminalRemainderTest',
 'web/messaging/ArtemisReplyConsumerTest'}
NEW_TESTS={
 'api/messaging/inbound/ConsumerRollbackUnconfirmedContractTest',
 'protocol/transport/UnconfirmedJmsRollbackExceptionTest',
 'web/messaging/ReplyRollbackUnconfirmedContractTest',
 'web/messaging/ReplyRollbackSignalContractTest'}


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5780',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3939,583,1664):return ast.copy_location(ast.Constant({3939:3955,583:587,1664:1665}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<coherent3955 original host runner>'):raise ValueError('all generated namespace static0 first')
    if any(s in raw for s in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):raise ValueError('only unchanged host fixture profile; held operations prohibited')
    compile(raw,'<one necessary3955>','exec');return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('PG5780',LABEL).replace('pg5780','pg5808').replace('jms-primary','rollback')
    old="'tests': 3939, 'suites': 583, 'mainClasses': 1664"
    if raw.count(old)!=1:raise ValueError('one complete planned physical inventory')
    raw=raw.replace(old,"'tests': 3955, 'suites': 587, 'mainClasses': 1665",1)
    trigger='BUG1485 three same-identity exception guards in two Main classes. Seven new finite proxy cases/two suites, all original3932 cases/resources/POM unchanged. Separate API/Web purposeful reds retained; selected14/static/current-byte proof complete. Guest/failed cohort held; no old PT/native success imported.'
    replacement='BUG1489 typed unconfirmed rollback stops four receiver groups; Web outer fatal signal connected. New16 independent finite cases/four suites, four original Test files explicitly corrected for cause retention and externally unconfirmed rollback; all original3939 identities retained. Selected54 and independent850/1665/eight-modified-one-added proof first. No old PT/native import or held guest/failed-cohort operation.'
    if raw.count(trigger)!=1:raise ValueError('one declared coherent rollback regression trigger')
    raw=raw.replace(trigger,replacement,1);compile(raw,'<new-only3955 driver>','exec');return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical Main/Test/config')
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    for rel,digest in PROOFS.items():
        raw=(base/rel).read_bytes();v=json.loads(raw)
        if hashlib.sha256(raw).hexdigest()!=digest or v['source']!=SOURCE or v['actualExit']!=0:raise ValueError('actual current54 and full source/static proof first, never a planned success')
    rows=subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines();changes={};added={}
    for row in rows:
        action,path=row.split('\t')
        if '/src/test/'not in path:continue
        if not path.endswith('Test.java')or'/src/test/java/dev/codex/schubert/nk/'not in path:raise ValueError('no test resources or oracle fixtures silently changed')
        key=path.split('/src/test/java/dev/codex/schubert/nk/')[1][:-5]
        (changes if action=='M'else added if action=='A'else {}).update({key:path})
        if action not in('M','A'):raise ValueError('no removed or aliased Test identities')
    if set(changes)!=CHANGED_TESTS or set(added)!=NEW_TESTS:raise ValueError('exact four added and four explicitly reviewed existing Test files')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('original harness, characterization and build gates unchanged')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.RUNTIME.preflight()
    os.umask(0o077)
    with(W/'pg5808-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.RUNTIME.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one coherent rollback3955>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
