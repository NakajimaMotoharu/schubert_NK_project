"""Read-only runtime PT-design mapping, existing whole-PG review reuse; never execute database paths."""
import copy
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json'
NORMAL_PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
OUT=data.BASE/'PG17246-morning-db-runtime-static-pt-design-v1'
DOC='documents/400_PGPT/450_品質/3361_MorningDBSession実行部_静的PT設計対応.md'
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java'
REFERENCES=[
 ('PG11580-batch-session-source-review-v1','198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc'),
 ('PG11582-batch-session-source-review-post-v1','7f2130d91fa6fe4e4b1b3846455218702099d19effb32b6e6d361219300c57a3'),
 ('PG16112-batch-session-saved44-reference-v1','0425538b6334d0ae7be11ef628a76bbfaf4efcfe182c5a5536d56b0810114966'),
 ('PG16114-batch-session-reference-post-v1','8b334d8ea9700d5e2e1972c1db8ed15e04212a1d7508b535d97d8dae3fa22168')]
ROWS=[["D-MDB-001","execute / Session.guard","341 SSC104;332 SSC063","callback終了でactive=false、同thread・非handoff・非interrupt限定。Connection/owned credentialの責務、SQL/IO既知固定と未知identity・close順位を区別。別thread/再入/終了後/取得前失敗/close同時失敗は非成功。","public <T> T execute(","session.active = false;","thread != Thread.currentThread().threadId()"],["D-MDB-002","inspectPermitDatabase","341 SSC104/200","cleanupVerifiedかつexpiryHandoffStarted後だけ、同Connectionのrole/schema/advisoryを前後照合。null・role変化・lock消失・owner期限・schema unknownを拒否しpermitを生成しない。","public DatabaseObservation inspectPermitDatabase(","if (!cleanupVerified || !expiryHandoffStarted)"],["D-MDB-003","requireUnused / requireConsistent","341 SSC094;332 §8.3","新runは参照0、resumeはidentityConsistent。backupCommitted前限定、同run/cutoffの前後guard。存在・不整合を成功補完せずSQL等の実後条件は未実測。","public void requireUnused(","public void requireConsistent("],["D-MDB-004","beginBackup","341 SSC104","schema確認→同TX二step begin→commit確定→autoCommit=true→backupCommitted。途中失敗では手修復/再発行しない。commit送達unknown後に権限や成功を付与しない。","public BackupBegins beginBackup(","backupCommitted = true;"],["D-MDB-005","successfulBackup / successfulHandle","341 SSC200;331 §8.3","最新二SUCCESSが同run/date/attempt/start/endの一束で、別step、µs、終了≦now、固定target/success1又は2/failure0/byte>0/error null。欠落/3行/未来/日違い/driver未知を拒否。SQL literalと独立14列値を将来oracleにする。","public Optional<BackupBegins> successfulBackup(","private BatchStepAttempt successfulHandle("],["D-MDB-006","beginResumeBackup / completeReusedBackup","341 SSC200","同manifest再読と同handleの既SUCCESS確認、二SKIP確認後のみcommit。再用完了はreadback/rollback後backupFinished。元SUCCESSを今回新Backup成功へ数えず、manifest交換/null/不一致拒否。","public BackupBegins beginResumeBackup(","public void completeReusedBackup("],["D-MDB-007","completionGuard / completeBackup","341 SSC104/134","同begin、未finished/未handoff、autoCommit/RW/READ_COMMITTED/HELD。独立bundle完成callback前後に再確認し、返却時刻だけでDB/原本/Unit成功を認定しない。","private void completionGuard(","public Instant completeBackup("],["D-MDB-008","failBackup / failedBackupSnapshot / failedObservationGuard","341 SSC134;332 SSC063","二FAILEDだけ同TX確定→独立二行再読→rollback後finished。正確なCOMMAND_FAILURE(1,0,1,0)二値だけended保持。snapshotは同begin/end/ownerの再読で、異なるfailed理由から代替権限を作らない。","public void failBackup(","public BackupFailureSnapshot failedBackupSnapshot(","private void failedObservationGuard("],["D-MDB-009","observeBackup / observeBackupPair","341 SSC134/200","current二rowをid昇順lockしsemantic DB/config順へ戻す。再用では元manifest+prior二SUCCESS、通常ではexpected handle、未manifestでは正確なfailed/end一致。余行/NULL/不同値/owner故障は非成功。","public BackupObservation observeBackup(","private List<BackupStepRepository.Terminal> observeBackupPair("],["D-MDB-010","handoffCleanup","341 SSC104","backupFinished後一回、開始前autoCommit=true、inHandoff中Session再入不可。子callback後にlock回収とguardを満たして返す。callback/再取得失敗でも開始済み印を戻して再発行しない。","public <T> T handoffCleanup(","handoffStarted = true;"],["D-MDB-011","requireAbandonedRequest","341 SSC104;332 §8.3","同run、元startがcutoff以後/今回start未満、二step元FAILED/ABANDONEDでattempt小・日付/終了窓一致。RO TX二row/余行拒否、rollback/状態復帰/consistent再読。既requestを書換えず別runを救済しない。","public void requireAbandonedRequest(","connection.setReadOnly(true);"],["D-MDB-012","recheckConsistent","332 SSC063","JDBC RW設定のままserver SET TRANSACTION READ ONLY。Statement取得直後primary記録/direct close、SQL-only固定変換・未知identity維持。Connection借用とclose所有を分け、失敗時に値を返さない。","public void recheckConsistent(","SET TRANSACTION READ ONLY","JdbcResourceFailures.replace(failure, secondary)"],["D-MDB-013","beginExpiry overloads","341 SSC200","cleanupVerified、expiry未handoff/未begin、同Backup run必須。prior auditとcurrent.SKIP整合、commit後に元SUCCESS又は正確RUNNING初期監査を独立再読、rollback/owner再確認後だけbeginsを保持。元audit更新や再purgeを許可しない。","public ExpiryBegins beginExpiry(","if (current.skipped() != prior.isPresent())"],["D-MDB-014","handoffExpiry","341 SSC200/104","cleanupVerified＋expiryBegins後一回だけhandoff。開始済みを保持し、finally inHandoff解除は再実行許可ではない。別thread・重複・autoCommit false・子/再取得unknownを非成功。","public <T> T handoffExpiry(","expiryHandoffStarted = true;"],["D-MDB-015","observeExpiry","341 SSC200;331 expiry監査","同begins/EXPIRY receipt。SKIPはexit0＋元audit一致、通常SUCCESS0/WARNING10/FAILED30を厳密照合しended非null、許可error NONE/COMMAND_FAILURE/SAFETY_FAILUREだけ。rollback後owner再確認、未知status/終了/不一致を0補完しない。","public ExpiryObservation observeExpiry(","? 10","? 30 : -1;"],["D-MDB-016","observeCleanup variants","341 SSC199/200","Backupfinished＋handoff、receipt0/10のみ、failedBackupと保持failureEnded整合。七terminalを現在DBから読み各SKIP/backupUnavailable/finishedを再検査、receipt一致・rollback・owner再確認後だけcleanupVerified。拒否30とは分ける。","private CleanupTerminalRepository.Snapshot observeCleanup(","cleanupVerified = true;"],["D-MDB-017","observeCleanupRejected / cleanupReferences overloads","341 SSC199/200/201","拒否はCLEANUP exit30・同ownerのreadRejected二回一致だけで完了/新attemptでない。元参照はexpected全row再読後だけ取得、元成功seals/進捗はRepository側別契約。NULL/交換/unknownを成功値で埋めない。","public CleanupTerminalRepository.RejectedSnapshot observeCleanupRejected(","public java.util.List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences("],["D-MDB-018","currentRunReference","341 SSC200","data-only same-run lookupでforeign UUID拒否。現在runを返すだけで原本session能力や管理検索・同日別run成功の認定を作らない。originals注入経路と区別。","static SuccessRunLookup currentRunReference(","if (!id.equals(run.id())) throw unavailable();"]]

def require(ok,why):
    if not ok:raise ValueError(why)
def contract(v):
    require(v['source']==SOURCE and type(v['productTestsExecuted']) is int and v['productTestsExecuted']==0,'no dynamic qualification')
    require(v['status']=='STATIC_PT_DESIGN_MAPPING_RECORDED' and v['dynamicStatus']=='NOT_EXECUTED_HOLD','static is not PT pass/exempt')
    require(v['coverage'] is None and v['newAccepted']==0 and v['formalUpdated'] is False and v['effortPercent'] is None,'no coverage/phase fabrication')
    require(v['wholeCurrentTestSemanticReviewComplete'] is False and v['oldRuntimeTransferred'] is False,'no unseen Test or old execution')
    require(v['newFullPgReviewCredit']==0 and v['priorWholePgReviewReused'] is True and v['designRows']==ROWS,'no duplicate prior PG credit')
    require(all(v[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualNetworkActions','actualServiceActions']),'no external action')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only static record')
    normal=data.read_checked(NORMAL,NORMAL_PIN);require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'same normal source only')
    refs=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in REFERENCES]
    old,post,current,current_post=refs
    require(old['source']==post['source']=='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b' and current['source']==current_post['source']==SOURCE and all(v['actualExit']==0 for v in refs),'keep historical and current static domains')
    require(current['oldReviewManifestSha256']==REFERENCES[0][1] and current['oldPostManifestSha256']==REFERENCES[1][1] and current['priorFullSourceReviewReused'] is True and current['newManualReviews']==0,'existing PG reuse not new review')
    require(len(current['sourceHashes'])==5 and MAIN in current['sourceHashes'],'curated five source paths')
    require(all(data.sha((data.ROOT/p).read_bytes())==normal['begin']['inputHashes'][p]==h for p,h in current['sourceHashes'].items()),'full same reviewed source bytes')
    text=(data.ROOT/MAIN).read_text();require(len(text.splitlines())==1645 and data.sha(text.encode())==current['sourceHashes'][MAIN]=='27bda4446e8b0a112963704b95d530af2357d254f3f6bced1ce04284fb5e88e2','bounded actual Main text')
    body=(data.ROOT/DOC).read_text();require(len(ROWS)==18 and len({r[0] for r in ROWS})==18,'eighteen design rows not tests')
    anchors={}
    for row in ROWS:
        require(all(cell in body for cell in row[:4]),'actual manual design row')
        anchors[row[0]]=[]
        for anchor in row[4:]:
            require(anchor in text,'reviewed textual anchor, not semantic runtime proof')
            anchors[row[0]].append(dict(text=anchor,firstLine=text[:text.index(anchor)].count('\n')+1))
    approved={}
    for number in ['331','332','341','343']:
        paths=list((data.ROOT/'documents/300_SS').glob('**/'+number+'_*.md'));require(len(paths)==1,'unique approved design')
        p=paths[0];relative=str(p.relative_to(data.ROOT));blob=p.read_bytes()
        require(blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'same approved design')
        approved[relative]=data.sha(blob)
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,status='STATIC_PT_DESIGN_MAPPING_RECORDED',dynamicStatus='NOT_EXECUTED_HOLD',designRows=ROWS,anchors=anchors,sourceHashes=current['sourceHashes'],manualRuntimeReadRanges=[[661,1645],[478,547]],priorWholePgReviewReused=True,newFullPgReviewCredit=0,priorStaticReviewSource=old['source'],priorReferences=[list(p) for p in REFERENCES],approvedDesignHashes=approved,documentPath=DOC,documentSha256=data.sha(body.encode()),wholeCurrentTestSemanticReviewComplete=False,productTestsExecuted=0,coverage=None,oldRuntimeTransferred=False,newAccepted=0,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,whole451Accepted=False)
    contract(value);labels=[]
    vectors=[('source','OLD'),('productTestsExecuted',18),('status','PASS'),('dynamicStatus','PASS'),('coverage',100),('newAccepted',1),('formalUpdated',True),('effortPercent',100),('wholeCurrentTestSemanticReviewComplete',True),('oldRuntimeTransferred',True),('newFullPgReviewCredit',1),('priorWholePgReviewReused',False),('designRows',[]),('actualVmActions',1),('actualDatabaseActions',1),('actualNetworkActions',1),('actualServiceActions',1)]
    for key,item in vectors:
        bad=copy.deepcopy(value);bad[key]=item;require(bad!=value,'nondegenerate vector')
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('static record false credit '+key)
    for ref in refs:verify(ref['invocation'])
    verify(invocation);value.update(metadataNegativeVectors=len(labels),negativeLabels=labels);OUT.mkdir();data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
