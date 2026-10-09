"""SS343 SSC233 genuine completed-ISSUED current binding, not the old INVALID case.
Generation only; no permit/Unit/DB/publication operation is issued here.
"""
import ast
from pathlib import Path
from pg864_completed_sources import java as old_java,java_test as old_test
from pg936_stage_candidate import source as stage_source
R=Path(__file__).resolve().parent
RUN='93cb976e-c36c-47a3-b9e2-0ad28d2996de'
ACT='0dfe0b7f-0e36-4b81-9086-500d896d1187'
EPOCH='22ba4479-64b2-4a3c-b2f9-ba720045e821'
PERMIT='09c13154c30c568c19323eef91bf1a8a2037236abaabbf9ce5b39888c966cfc7'
def bind(raw):
    raw=raw.replace('PG864','PG942').replace('Pg864','Pg942').replace('pg864','pg942')
    raw=raw.replace('PG862','NEXT_PG932').replace('pg862','NEXT_pg932').replace('PG832','PG862').replace('pg832','pg862').replace('NEXT_PG932','PG932').replace('NEXT_pg932','pg932')
    changes=(('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),('9de2d03c-28c7-4647-97d9-c66ace06048c',RUN),('021111b4-6de5-4733-917d-5ac176240ffc',ACT),('8b153538-1523-4987-a456-6cbea0d345ee',EPOCH),('2026-10-09T05:42:22.532331Z','2026-10-09T19:07:23.894279Z'),('2026-10-09T15:32:16.513983Z','2026-10-09T19:31:23.759513Z'),('2026-10-09T15:32:16.513984Z','2026-10-09T19:31:23.759514Z'),('37356ff23d0393924c22079bd4c87fce7c3070155d84704fb1cb143e7b1c60a5','2913a5e9001f1e16431499005a37dfec3ce5476a21e907ef3dfd95793fe638fd'))
    for a,b in changes:raw=raw.replace(a,b)
    return raw
EPOCH_METHOD='''
  static boolean epoch(StartupPermitRecords.Epoch value,UUID expected){
    if(value==null||expected==null)return false;
    boolean initial=expected.equals(OLD_EPOCH);
    return value.state()==(initial?StartupPermitRecords.State.ISSUED:StartupPermitRecords.State.INVALID)
      &&value.boot().equals(BOOT)&&value.epoch().equals(expected)&&value.activation().equals(ACTIVATION)
      &&(initial?value.permitDigest().equals(Optional.of("09c13154c30c568c19323eef91bf1a8a2037236abaabbf9ce5b39888c966cfc7")):value.permitDigest().isEmpty());
  }
'''
def java():
    raw=bind(old_java())
    marker='    require(epoch.state()==StartupPermitRecords.State.INVALID&&epoch.boot().equals(BOOT)&&epoch.epoch().equals(expectedEpoch)&&epoch.activation().equals(ACTIVATION)&&epoch.permitDigest().isEmpty());'
    assert raw.count(marker)==1;raw=raw.replace(marker,'    require(epoch(epoch,expectedEpoch));')
    marker='  static void original(MaintenanceRunFiles.Session session)throws Exception{';assert raw.count(marker)==1
    raw=raw.replace(marker,EPOCH_METHOD+marker).replace('Fixed completed data, not a successful-parent receipt.','Fixed genuine completed-ISSUED data; new candidate parent/native acceptance remains separate.')
    raw=raw.replace('fresh.version()==4&&fresh.variant()==2&&!fresh.equals(OLD_EPOCH)','fresh.version()==4&&fresh.variant()==2&&!fresh.equals(OLD_EPOCH)&&!fresh.equals(BOOT)&&!fresh.equals(ACTIVATION.id())&&!fresh.equals(ACTIVATION.run().id())')
    return raw
EPOCH_ORACLE='''
    var boot=UUID.fromString("cc9ed874-7f4f-450e-a188-8de1e42c8441");
    var epoch=UUID.fromString("22ba4479-64b2-4a3c-b2f9-ba720045e821");
    var fresh=UUID.fromString("11111111-2222-4333-8444-555555555555");
    var issued=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.ISSUED,boot,epoch,activation,Optional.of("09c13154c30c568c19323eef91bf1a8a2037236abaabbf9ce5b39888c966cfc7"));
    require(Pg942CompletedDeployment.epoch(issued,epoch));
    require(!Pg942CompletedDeployment.epoch(null,epoch));require(!Pg942CompletedDeployment.epoch(issued,null));
    require(!Pg942CompletedDeployment.epoch(issued,fresh));
    var wrongDigest=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.ISSUED,boot,epoch,activation,Optional.of("0".repeat(64)));
    require(!Pg942CompletedDeployment.epoch(wrongDigest,epoch));
    var wrongBoot=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.ISSUED,fresh,epoch,activation,issued.permitDigest());
    require(!Pg942CompletedDeployment.epoch(wrongBoot,epoch));
    var wrongActivation=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.ISSUED,boot,epoch,foreign,issued.permitDigest());
    require(!Pg942CompletedDeployment.epoch(wrongActivation,epoch));
    var invalidBefore=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.INVALID,boot,epoch,activation,Optional.empty());
    require(!Pg942CompletedDeployment.epoch(invalidBefore,epoch));
    var invalidAfter=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.INVALID,boot,fresh,activation,Optional.empty());
    require(Pg942CompletedDeployment.epoch(invalidAfter,fresh));
    require(!Pg942CompletedDeployment.epoch(invalidAfter,epoch));
    var issuedAfter=new dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch(dev.codex.schubert.nk.batch.file.StartupPermitRecords.State.ISSUED,boot,fresh,activation,issued.permitDigest());
    require(!Pg942CompletedDeployment.epoch(issuedAfter,fresh));
'''
def java_test():
    raw=bind(old_test());marker='    var events=new ArrayList<String>();';assert raw.count(marker)==1
    return raw.replace(marker,EPOCH_ORACLE+marker)
def refs():
    tree=ast.parse(stage_source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
    p=ast.parse(payload);outer=next(n for n in p.body if isinstance(n,ast.With));stop=next(i for i,n in enumerate(outer.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='before'for t in n.targets))
    defs=p.body[:p.body.index(outer)]+outer.body[:stop];raw=ast.unparse(ast.Module(body=defs,type_ignores=[]))+'\n'
    raw=raw.replace('validate_baseline(comparable, baseline, list(pathlib.Path(\'/run/systemd/system/schubert-nk-morning-controller.service.d\').iterdir()))','validate_current(comparable, baseline, list(pathlib.Path(\'/run/systemd/system/schubert-nk-morning-controller.service.d\').iterdir()))');assert 'validate_current(comparable'in raw
    # Explicit independent original approval; never derive expected from the new candidate.
    raw+='''
approval_root=pathlib.Path('/etc/schubert-nk/release-approval');approval=approval_root/'current'
expected_old_approval=b'NKRELEASEAPPROVAL1\\nversion=0.1.0-PG862\\nmanifest_sha256=20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe\\n'
assert approval.read_bytes()==expected_old_approval
a=approval.lstat();d=approval_root.lstat()
assert stat.S_ISREG(a.st_mode)and(a.st_uid,a.st_gid,stat.S_IMODE(a.st_mode),a.st_nlink)==(0,0,0o400,1)and not os.listxattr(approval)
assert stat.S_ISDIR(d.st_mode)and d.st_uid==d.st_gid==0 and not os.listxattr(approval_root)
assert sorted(q.name for q in approval_root.iterdir())==['current']
baseline['trees'][str(approval_root)]={str(approval_root):{'metadata':metadata(d),'sha256':None},str(approval):{'metadata':metadata(a),'sha256':hashlib.sha256(expected_old_approval).hexdigest()}}
'''
    finite=bind((R/'pg864_finite_delta.py').read_text());body=bind((R/'pg864_completed_refs_body.py').read_text()).replace('==564','==584')
    raw+='''
from pg944_parent_receipt import completed
def genuine_parent():
 data=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/0dfe0b7f-0e36-4b81-9086-500d896d1187.done').read_bytes()
 assert hashlib.sha256(data).hexdigest()=='2913a5e9001f1e16431499005a37dfec3ce5476a21e907ef3dfd95793fe638fd'
 journal=subprocess.check_output(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=75f48ce36cd740e98a801eede7fdbb7f','-o','json','--no-pager'],timeout=10)
 result=completed([json.loads(l)for l in journal.splitlines()],data)
 assert result['genuinePid1StartDone']and result['genuineRootDone']and result['elapsedSeconds']<1800
'''
    marker='    assert runtime==[]';assert body.count(marker)==1;body=body.replace(marker,'    genuine_parent()\n'+marker)
    raw+=finite+'\n'+body;ast.parse(raw);return raw
def sources():
    result={'Pg942CompletedDeployment.java':java(),'Pg942CompletedDeploymentTest.java':java_test(),'pg942_completed_refs.py':refs()}
    for n in ('Pg797OwnedDatabase.java','Pg797OwnedDatabaseTest.java','Pg798DatabaseScope.java','Pg798DatabaseScopeTest.java'):result[n]=(R/n).read_text()
    result['pg944_parent_receipt.py']=(R/'pg944_parent_receipt.py').read_text()
    return result
