"""Pre-register the static defect, then preserve and replace only four ordinary private monitors."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=b/'evidence/PG37206-f03-sync39-source-review-v1/site-decisions.json';rows=[x for x in ld(review) if x['disposition']=='APPLICABLE_ORDINARY_LOCK_CHANGE_PLANNED'];assert len(rows)==4
paths=sorted({x['raw']['path'] for x in rows});assert len(paths)==3
ledger=r/'documents/900_OTHER/910_台帳';bug=ledger/'915_障害表.md';horizontal=ledger/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'\bBUG-?(\d{3,4})(?!\d)',bug.read_text())))==3160
assert max(map(int,re.findall(r'\bYKT-?(\d{3,4})(?!\d)',horizontal.read_text())))==2629
out=b/'evidence/PG37210-monitor-lock4-source-v1';assert not out.exists();out.mkdir();before={}
for name in paths:
 p=r/name;assert all(sha(p)==x['sourceSha256'] for x in rows if x['raw']['path']==name);before[name]=p.read_bytes();(out/(p.name+'.before')).write_bytes(before[name])
testdir=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
testpins={str(p.relative_to(r)):sha(p) for p in testdir.glob('*.java')}
with bug.open('a') as f:f.write('\n\n## BUG3161 PG 2026-11-17 通常監視4siteの同期規則適用\n\n対象BatchMetricRecorder.record、MonitoringObservationClock.context、MonitoringPoller.observe/observeNow。重要度低/優先中、発見工程PG、独立sourceレビューPG37206。期待private final所有・全compound処理の排他を維持し、PMD7.28 AvoidSynchronizedStatementの適用4siteを解消。実際はprovider/registry/actionをintrinsic monitor内で実行。機能障害や実virtual-thread pinningの再現は未実施であり断定しない。原因=コーディング規約のprivate lockをintrinsic monitorだけで実装し、native/callback pinningの注意を四通常境界へ適用していなかった。修正前起票。private final ReentrantLock/lock-try-finallyへ限定変更し、原whole通常PTと例外同一性/別thread再入/有限並行/再入可能性を確認。RD171/UI252/SS351/411§9/451/PG-D364/YKT2630。Root/file/capture35及び回復10のHOLDは解除しない。修正commit/再試験未確定、状態OPEN。\n')
with horizontal.open('a') as f:f.write('\n\n## YKT2630 BUG3161 private monitorのcallback境界\n\n検索条件=原F03同期54siteの全bodyとprivate monitor生成元、PG37206現39のsource hash一致。通常監視3class/4siteを是正対象とする。既pure-memory15はPG37076個別非該当を参照し新規再資格0。残native/file/client/capture35は非該当とせず未解決HOLDで、同原因の全域完了を宣言しない。通常4の変更後は全対応whole Test/例外後異thread再入/finite worker終了、Main compile/null/static/public ABI/無filter countersを保存する。対象外の承認や実native成功を推定しない。個別4の限定結果と全35未完を区別。修正commit/再試験未確定、状態OPEN。\n')
changed=[]
for name,raw in before.items():
 text=raw.decode();candidate=text.replace('import java.util.Objects;','import java.util.Objects;\nimport java.util.concurrent.locks.ReentrantLock;',1).replace('private final Object lock = new Object();','private final ReentrantLock lock = new ReentrantLock();',1)
 pairs=[]
 for row in [x for x in rows if x['raw']['path']==name]:
  old='synchronized (lock) '+row['fullBody'];assert candidate.count(old)==1
  new='lock.lock();\n    try '+row['fullBody']+' finally {\n      lock.unlock();\n    }';candidate=candidate.replace(old,new,1);pairs.append((old,new))
 restored=candidate
 for old,new in reversed(pairs):restored=restored.replace(new,old,1)
 restored=restored.replace('private final ReentrantLock lock = new ReentrantLock();','private final Object lock = new Object();',1).replace('import java.util.Objects;\nimport java.util.concurrent.locks.ReentrantLock;','import java.util.Objects;',1)
 assert restored.encode()==raw
 (r/name).write_text(candidate);changed.append(dict(path=name,beforeSha256=hashlib.sha256(raw).hexdigest(),afterSha256=sha(r/name),sites=len(pairs),inverseBeforeFormatWholeByteExact=True))
assert all(sha(r/p)==h for p,h in testpins.items())
with (r/'documents/400_PGPT/440_判断/441_実装判断記録.md').open('a') as f:f.write('\n\n### PG-D364 通常監視4siteの明示private lock（2026-11-17）\n\nBUG3161/YKT2630/F03原2-2。既private final所有・compound順序・同thread再入・uninterruptible取得・解放後可視性を維持し、三classの四synchronized blockだけをprivate final ReentrantLock/lock()/try/finally unlock()へ変更する。default non-fairで新しい公平性保証は追加しない。callback/clock/registryをlock外へ移動しない。外側public ABI/ログ/metric/時間/所有の契約は不変。411§9より詳細な内部実装でRD/UI/SS変更不要。PMD raw規則を抑制せず、元通常Test期待と新異thread/例外解放を独立検証。native/file/capture35の代替受入やRoot/QA056解除へ転用しない。\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceBefore=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),mainChanges=changed,originalTestSourceHashes=testpins,mainClasses=3,sites=4,originalTestSourcesUnchanged=True,productTestsExecuted=0,actualNativeRootDbVmOperations=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedMain=3,sites=4,testChanges=0,bug='BUG3161')))
