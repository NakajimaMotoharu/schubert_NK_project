# 朝batch・backup・削除・再実行設計

## 1. 目的・追跡

毎日05:00 JSTの計画停止、package update、OS reboot、DB/config backup、条件付き業務data削除、
transfer/Expiry清掃、依存順起動、失敗時の継続/打切り、二重起動防止と再実行を定める。

- 上位設計: [251_朝バッチ・バックアップ・起動停止設計](../../200_UI/250_運用・非機能/251_朝バッチ・バックアップ・起動停止設計.md)
- 関連RD: AVL-001～AVL-010、OPS-001～OPS-017、BAK-001～BAK-008、BKO-001～BKO-008
- 関連SS: [332_SQL・transaction・lock・削除設計](../330_データ・ファイル/332_SQL・transaction・lock・削除設計.md)、
  [333_大容量結果file・media・Range配信設計](../330_データ・ファイル/333_大容量結果file・media・Range配信設計.md)
- 関連QA/RDF/UIC: QA-013、QA-014、QA-024、QA-029、QA-033、QA-038～QA-040、QA-043、RDFなし、UIC-003

## 2. Unit・step構成

| フェーズ | Unit/step ID | Timeout | 成功・失敗の後続 |
|---|---|---:|---|
| 05:00開始 | `schubert-nk-maintenance.timer` | - | `maintenance.service`を1回起動 |
| 停止/update | `schubert-nk-maintenance.service` | 60min | 更新警告はreboot継続、安全性判定失敗はreboot/公開停止 |
| Reboot後束ね | `schubert-nk-morning.target` | - | 下記unitを順序起動 |
| DB | distribution PostgreSQL unit | 120s | 失敗は後続全停止 |
| Backup | `schubert-nk-backup.service` / `BACKUP_DB`,`BACKUP_CONFIG` | 30min | 失敗は業務data削除だけskip、起動続行 |
| Cleanup | `schubert-nk-cleanup.service` / `CLEAN_*` | 30min | 個別warningは継続、root/DB safety異常は後続停止 |
| Broker | `artemis.service` | 120s | 失敗はAPI以降停止 |
| Expiry | `schubert-nk-expiry-cleanup.service` | 10min | critical/health異常はAPI以降停止 |
| API | `schubert-nk-api.service` | 120s | 失敗はWeb/Caddy停止 |
| Web | `schubert-nk-web.service` | 120s | 失敗はCaddy停止 |
| 公開 | `caddy.service`＋smoke | 30s | 失敗は公開停止、運用介入 |

## 3. Run identity・排他

SSC-049/PG-D-147: root controllerのfile adapterは実効UID0、/runと/run/schubert-nkのroot:root0755・ACLなし・RW tmpfs、maintenance.lockのroot:root0600・通常file・nlink1・size0・同deviceを検証する。NOFOLLOWで各directoryとentryを保持してからflockを取得し、獲得直後/処理後に固定pathを再openして同dev/ino・権限・ACLを確認する。元の保持能力は全保守callback終了まで存続し、entry/root close失敗で成功にしない。競合はcallback0回でDUPLICATE、admission/IOは固定診断で失敗。root以外の親、ACL追加、別FS、symlink/hardlink、未知属性、inode交換を受理せず、adapter自身が作成/chmod/unlinkして修復しない。特権rootによる保守中の置換は運用禁止であり検証だけで敵対rootを封じ込めたとはしない。

- Maintenance全体の`run_id`はUUID、`business_date`は開始時点のJST日付、`run_started_at`はUTC `Instant`で固定。
- OS排他は`/run/schubert-nk/maintenance.lock`を`flock(LOCK_EX|LOCK_NB)`。DB接続後は固定
  `pg_try_advisory_lock(71419602)`も取得。両方を持つprocessだけcleanup/morningを実行。
- Lock取得失敗は何も停止/削除せずexit 20、SYSTEM/BATCH alert。Lock file本体を手動削除して解除しない。
- 各stepは`batch_runs`へRUNNINGをINSERTし、成功/WARNING/FAILED/SKIPPEDで完了。Process異常のRUNNING残留は
  次回起動時にABANDONED相当のFAILEDとし、同じrun IDの新attemptで再開。

## 4. 05:00計画停止・update・reboot

SSC-049/PG-D-146のOS排他部品: LinuxFileLockは親が既に型/所有/ACL/namespaceを検証して保持したlock inodeだけを独立O_RDONLY|O_CLOEXECでopenし、flock(LOCK_EX|LOCK_NB)成功後だけcallbackを呼ぶ。EWOULDBLOCKはcallback0回の競合結果、他errno/open/close失敗は非成功。callback終了・例外時も全FDを閉じ、close完了前に成功結果を返さない。FDは複製/公開せずcloseでlockを解除、既存lockfileの削除/作成/内容変更をしない。対象はlocal /runのOS lockでありNFS/SMBの異なる意味へ拡張しない。実util-linux flockと相互排他をPTで検証するが、root配布/親inactive/実backup/DB lock引渡しを本部品だけで実装済みとしない。

### 4.1 実行順

1. OS lock取得、run ID生成、host/app/schema/version、disk、Queue/DLQ、未処理job、active session件数を記録。
2. Caddyをmaintenance responseへ切替えるか停止し、public 55160の新規業務requestを遮断。
3. WebへSIGTERM。HTTP新要求を止め、MQ待機を最大30秒で完了/エラー化。
4. APIへSIGTERM。Consumer receive停止、処理中DB/JMS transactionを最大60秒でcommitまたはrollback/requeue。
5. Artemis停止、journal flushとclean stopをunit resultで確認。
6. PostgreSQL fast shutdown、`pg_isready`不応答とunit inactiveを確認。
7. Package metadata更新→noninteractive upgrade、実行前後のpackage list/kernel/reboot-requiredを記録。
8. Package manager lock、dpkg未完了、filesystem、boot partition、kernel/initramfsの安全性を検査。
9. Reboot安全なら`systemctl reboot`。安全でなければpublicを開けずexit 30で運用待ち。

Update command自体の非0はWARNINGとし、dpkg状態とboot可否が正常ならreboot/復旧を続行する。
自動`kill -9`を使わず、stop timeoutはunit FAILED・証跡保存・public停止とし、強制終了は353の運用判定に委ねる。

### 4.2 Reboot不成立のwatch

Maintenance開始から60分でreboot完了markerが更新されない場合、外部監視はcriticalとする。
同一server内監視だけでreboot hangを検出できると仮定しない。

## 5. Reboot後の起動順・gate

```text
PostgreSQL readiness
 -> BACKUP_DB + BACKUP_CONFIG
 -> CLEAN_BUSINESS   (backup successのみ、failureはSKIPPED)
 -> CLEAN_TECHNICAL  (backup successのみ)
 -> CLEAN_TRANSFER   (backup成否にかかわらず、root safety必須)
 -> Artemis readiness
 -> CLEAN_EXPIRY
 -> API readiness
 -> Web readiness
 -> Caddy validate/start
 -> loopback/public smoke
```

Backup serviceがFAILEDでもmorning target自体はcleanupへ進み、cleanupがDBの当日成功rowを見て
BUSINESS/TECHNICALをSKIPPEDにする。Transferは独立実行。Transfer rootの実体/権限/重複異常だけは
Artemis以降を開始しない。

## 6. DB backup

### 6.1 作成

1. Backup rootをabsolute・real pathで検証し、`/`、home、asset/transfer/log/Artemis root自体または配下を拒否。
2. `yyyyMMdd-HHmmss-<runId>.part`をmode 0700でCREATE_NEW。同一mountの確定先とする。
3. Systemd credentialで渡された`.pgpass`を`PGPASSFILE`へ指定し、passwordをcommand line/environment実値へ出さない。
4. QA-043/UIC-003承認済みの`schubert-backup` OS user固定unitから、`schubert_backup`専用credentialで
   `pg_dump --format=custom --no-owner --no-privileges --schema=schubert --schema=schubert_web_session --schema=schubert_meta --file=<part>/schubert_nk.dump schubert_nk`
   を実行する。`schubert_batch` credentialでdumpしない。
5. Exit 0、file >0 byte、`pg_restore --list`成功、dump SHA-256を検証。
6. DB/app/schema/OS/JDK/PG/Artemis version、開始/終了、file size/hashを`MANIFEST.json`へ記録。Secretなし。

### 6.2 Config・credential backup

- `/etc/schubert-nk`の非秘密configはroot所有のtar、path traversal/symlinkを入れず`config.tar`へ固定。
- Credential directoryはrootが専用allowlistだけ読み、recovery用公開keyのみをhostに置き、
  `age` recipient暗号化の`credentials.tar.age`へする。復号private keyは当該server/backupに置かない。
- Archive中のfilename/permission一覧は機密扱いとし、暗号文本だけのhash/sizeをmanifestへ出す。

`age`の導入versionとrecipient fingerprintはrelease/config manifestへ記録する。別暗号工具への交換は
backup/restore手順の変更・rehearsalなしに行わない。

### 6.3 確定・7世代

1. 全fileのfsync、directory fsync後、`.part`をsuffixなし確定directoryへatomic rename。
2. 確定後にSHA-256を再照合し、`batch_runs`のDB/config両stepをSUCCESS。一方失敗は当日backup不成立。
3. 新規backup成功後だけ、正規名・通常directoryの成功backupを古い順に並べ、8世代目以降を削除。
4. Unknown name、symlink、manifest不整合、`.part`は自動世代削除せずwarning。既存7世代をbackup失敗時に削除しない。

## 7. Business/technical cleanup

### 7.1 必須gate

SSC-049/PG-D-148: 親OS lock保持下で、削除開始前にAPI/Web各unitのId/LoadState/ActiveState/SubState/Job/MainPID/ControlPIDを固定systemctl showで読み、対象Id一致・loaded/inactive/dead・Job空・PID各0を全件確認する。not-found/masked/failed/active/遷移中/残job・PIDは通さない。7fieldは各1回、ASCIIのみ・末尾LF1つ・1～1024byte、未知/重複/欠落/CR/NULは失敗。unitごと5秒、非zero/IO/close/timeout/interruptは無条件に後続不可、割込flagを保持する。前後の割込確認と再実行時のfresh観測を必須とし、古い結果をcacheしない。これは停止実行やcgroup全検査ではない。親は保守中の再起動を禁止し、通常stop timeout/TERM/復旧の既存設計を維持する。

- 同じ`business_date`のBACKUP_DBとBACKUP_CONFIGがSUCCESS。Dump/manifest directoryが現存しhash再照合済み。
- `run_started_at`を全DELETEのcursor/cutoffに使い、実行中の現在時刻で対象を広げない。
- API/Webはinactive、DB batch advisory lock取得済み。未満足は削除0件でSKIPPED/FAILEDを記録。

### 7.2 Step順

| Step | 対象 | Chunk | 失敗時 |
|---|---|---:|---|
| `CLEAN_NOTIFICATION` | COMPLETED/ERROR 24h超、CANCELLEDの前日まで | 1,000 | Chunk rollback、FAILED、question削除へ進まない |
| `CLEAN_QUESTION` | 論理削除済み＋notification不存在 | 1,000 | FK競合はskip/warning、他DB異常はFAILED |
| `CLEAN_SESSION` | UI 251の失効/期限条件 | 1,000 | Failed tableを記録しtechnical後続は独立 |
| `CLEAN_INBOX_OUTBOX` | expires/SENT+7日、PROCESSING/PENDING/ERROR除外 | 1,000 | 異常rowを削除せずalert |
| `CLEAN_LOG` | 90日超。`security_hold_until > log cutoff`は除外、NULL/期限到達は削除 | 10,000 | Chunk単位再開、hold件数をskipped記録 |
| `CLEAN_BATCH_RUN` | 400日超、RUNNING/FAILED調査中除外 | 1,000 | 証跡保護を優先しskip |

SQL、lock、delete順は332 §11を正とする。Batch roleは基底tableを直接DELETEせず、331 §3.3のallowlist済み
maintenance functionを呼び出す。各chunk commit後にcountを更新する。
Process kill後は未削除rowだけ残り、同cutoff再実行で0件/残件を冪等処理する。

SSC-051/PG-D-136のCLEAN_LOG再開: 331 §3.9の永続cursor/累積を使い、同run/cutoffで全holdを含む各chunkを一度だけ数える。target0のENDをDBへ記録するまで完了としない。親のattempt件数は開始時と終了時のmaintenance_read_log_cleanup_progress累積差分、run累積は別記録。row lock競合/SQL異常/commit不明は未完了、再開時はDB状態を読取り直す。CLEAN_BATCH_RUNでlog progressの完了400日・調査保護も別chunkで清掃する。持続cursorのない旧関数を親側の無限retryで補わない。親process実装/OS gateは引き続き必須。

### 7.3 非公開Inbox検査process（SSC-049/QA-046）

UIC-006の検査をbackup成功後のcleanup内部で実施する。通常API/Web inactive条件、固定run/cutoff、backup gateを維持する。検査中はHTTP/JMS Consumerを生成せず、DB snapshot/参照の検査だけを行う。batchのadvisory lockを別connectionから二重取得して自己deadlockさせないよう、検証・削除chunkのconnection/lock所有者を実装前に明示する。検査前後のlock断絶や他runの結果流用を許可しない。異常行は削除せず固定理由・件数だけを返し、暗号文・平文・鍵をbatchへ渡さない。SQL/権限/oneshot wiringのPT完了まで本stepを完了扱いしない。

SSC-049/PG-D-122のlock所有: 親batchはOS flockを保守全体で保持する。検査を開始する前に前段transactionを完了しDB session advisory lockを解放し、専用processが自身のDB transactionで71419602を取得してから候補を検査する。検査・DELETE・commitの間にlockを渡さない。親はprocess終了後にDB advisoryを再取得して後続へ進む。引渡し区間に別DB主体がlockを取得した場合、検査側/親の再取得失敗は失敗として停止し、検査未実施を成功にしない。OS lockを放す実装や、検証済結果を別transactionへ渡す実装は不可。実oneshot/異常終了の試験は後続gateとし、SQL単体PTで実運用結線完了とはしない。

SSC-049/PG-D-127再開状態: 専用processは331 §3.8の永続progressを同run/cutoffでlockして読み、候補処理とcursor/件数を同transactionで確定する。各row transactionを1件chunkとして使うため1,000上限を超えず、processは最大1,000回ずつのbounded呼出しを繰り返し30分のunit制限内でENDまで進む。途中中断は未完了、最終ENDでのみ検査stepをSUCCESS（保護0）またはWARNING（保護あり）へ集約する。未対応/不正rowもcursorを進めて保護件数へ加算し、先頭同一rowの無限再走をしない。commit不明時は同runでDB状態を再読取りし、削除済み行の件数を失わない。親attempt件数はそのattempt開始時/終了時の累積差分、run累積は別項目とする。既完了runは保存状態を返すだけ、鍵/参照修復後の再検査は新しい保守runで行う。CLEAN_BATCH_RUNでは完了progressの400日保持とRUNNING/FAILED調査保護を確認し、331の専用清掃関数で削除する。SQL/Javaだけでは専用unit/親のOS lock引継ぎ・backup実体gateは未完了。

SSC-050/PG-D-129: 全maintenance_cleanupの第2引数は固定run_started_atとし、log90日・batch履歴400日の保持閾値をcaller側で二重に差し引かない。SQL側でも当日backupの状態・終了・同runをrow lockの単一snapshotで再検証する。Batch履歴は完了ended_at基準、現在runと同run内のRUNNING/FAILED調査中を保持する。親processの実backup照合とOS lockは別途必須であり、このSQL補正で省略しない。

SSC-049/PG-D-130: run executorは324 §12.7の単調時計30分とinterruptを各最大1,000呼出しchunk前後で確認する。END/保護0だけSUCCESS、END/保護ありWARNING、途中停止/DB障害はFAILED相当50。最後の確認済み累積値を「最新総数」と誤記せず、次attemptは同runで永続状態を再読する。30分はprocess unit上限でも維持し、Java協調停止だけで長時間SQLの強制停止を保証したとしない。親の実backup/key/OS lock/終了後close検証は別gate。

## 8. Transfer cleanup

333 §12のsecure directory walkを使い、backup失敗時も実行する。Root正常で個別file削除失敗はWARNINGとし
後続起動。Root不正/重複/mount read-only/permission不正は対象0件でFAILEDとし、Artemis/API/Web/Caddyを開始しない。

| 拡張子 | 処理 | 理由 |
|---|---|---|
| `.part` | cutoff前なら削除 | 中間file |
| `.ready` | cutoff前なら削除 | 取得成否にかかわらず次回朝削除 |
| 不明file/symlink/device/socket | 削除せずWARNING | 誤削除/攻撃防止 |
| root/日付directory | rootは不変、空の正規日付dirだけ削除 | 広範囲削除防止 |

## 9. Artemis Expiry cleanup

1. Broker readinessと`nk.expiry.q` healthを確認。`nk_mq_maintenance`のLoadCredentialで管理APIへloopback接続。
2. Brokerが保持するexpiry timestampが`run_started_at - 7 days`より前のmessageをselectorでcount/byte見積り。
3. Count/byte/cutoffを記録した後、同selectorをArtemis management operationでpurge。Queue/journal fileをOSから削除しない。
4. 実行後countで削除差分を照合。DLQは対象にしない。
5. Purge失敗でもExpiryがwarning未満・broker health正常ならWARNING exitでAPI起動。Critical以上またはhealth不正はFAILEDで停止。

## 10. Readiness・smoke

| Component | Probe | 成功条件 |
|---|---|---|
| PostgreSQL | `pg_isready`＋readonly/read-write probe | 想定DB/schema version、role/grant、WAL/disk正常 |
| Artemis | CLI/management/readiness | acceptor loopback、journal、全Address/Queue、disk/duplicate cache |
| API | loopback management `/actuator/health/readiness` | DB/MQ/asset/codec/Consumer全UP |
| Web | loopback management readiness＋`/login` | MQ reply Consumer、technical DB、descriptor verifier全UP |
| Caddy | `caddy validate`→service active→HTTPS | Loopback `/login` 200、global IPは利用可能な監視地点から確認 |

Readinessは認証情報・Queue内容・DBデータをbodyへ返さない。Caddy公開後のsmoke失敗はCaddyを再停止し、
部分的に利用可能な状態を継続しない。

## 11. 再実行仕様

| Command | 前提 | 再実行動作 |
|---|---|---|
| `morning-run --resume <runId>` | Public/app停止、lock取得 | SUCCESS stepはSKIPPED、FAILED/ABANDONEDの次attemptを同cutoffで実行 |
| `backup` | PostgreSQL UP、root安全 | 毎回新directory、最新成功を当日成功に使用 |
| `cleanup --run-id` | 同runのbackup gate | 条件付DELETE、既削除は0件SUCCESS |
| `transfer-cleanup --run-id` | App停止、root safety | 既削除fileは0件、unknownは繰返しwarning |
| `expiry-cleanup --run-id` | Artemis UP、API停止 | 同cutoff selectorの残件だけpurge |

新しい日時でresume対象を再計算しない。別日へ進む場合は新run ID/business dateを作る。
SSC-054/BUG-138: 手動backup再実行は通常成功stepのskip例外。331 §8.2のbackup2stepだけ同日複数SUCCESSを保持し、新attempt失敗で既存成功を消去・状態変更しない。最新成功の実artifactを検証し、通常step成功一意性・固定run/cutoffと全backup gateは維持する。DB制約修正を実backup生成/検証完了と混同しない。
Manual commandもsystemd transient scopeまたは対応oneshot unitを通し、root shellでJava/SQL/scriptを直接実行しない。

## 12. Exit code・終了判定

| Code | 分類 | Systemd/operation |
|---:|---|---|
| 0 | SUCCESS | 後続へ進む |
| 10 | WARNING | Unitは設計済みwrapperでsuccess扱いに変換しalert。後続継続 |
| 20 | DUPLICATE/LOCKED | 二重実行なし、alert、自動再試行なし |
| 30 | SAFETY_GATE_FAILED | 削除/公開/後続停止、運用介入 |
| 40 | BACKUP_FAILED | Business cleanup skip、transfer/app起動は続行 |
| 50 | COMPONENT_FAILED | 依存後続を開始せず運用介入 |
| 70 | CONFIG/USAGE | 無操作で終了、修正後再実行 |

WARNINGをunit失敗としてdependencyを止めないよう、wrapperが`batch_runs`の状態を記録後に
systemd向け処理を明示する。予期外exception/signalは50扱い。

## 13. 証跡・機密除外

SSC-049/PG-D-144: private Inspector子unitだけは343 §6.8のreceipt wrapperを入口とする。JVM正常終了と検査成功を分離し、wrapperの0/10/50/70を親が同run/cutoffの永続progress・unit終了状態と照合する。子unitのSuccessExitStatus=10は「警告付きで子processが終了した」という扱いに限り、親CLEAN_INBOX stepを自動成功にしない。親だけがWARNING/件数/attemptをbatch_runsへ記録した後に後続へ進む。childの0だけで親OS lock/停止/backupを省略せず、古いunit結果/別run/不確定commitは成功へ補完しない。

Run ID、business date/cutoff、host、app/schema/config/package version、step/attempt、開始/終了、status、
target/success/failure/skipped count、byte数、duration、exit/error code、backup manifest hashをDBとstructured logへ記録する。

Command line全体、password、credential pathの内容、質問/回答本文、物理file path、backup暗号平文は記録しない。
Package名/versionと非秘密config hashは記録可。

## 14. PT・IT必須観点

- Timer、手動、二重起動、OS lock/DB lock、step中process kill、reboot不成立。
- Caddy/Web/API/Artemis/PostgreSQL各stop timeout、transaction rollback/requeue、自動SIGKILLなし。
- `pg_dump`非0、0 byte、list不正、hash不一致、config暗号失敗、rename失敗、容量不足。
- Backup専用role以外でのdump、dump roleのDML/SET ROLE/復号key取得、backup unit外からのcredential利用を負の試験にする。
- Backup成功/失敗分岐、7/8世代、既存世代保護、別test DBへのrestore。
- Notification全5state/cutoff境界、Question FK競合、chunk間kill/resume、保持対象外。
- Transfer root誤り、symlink/device/unknown file、個別失敗、root自体の保護。
- Expiry 7日境界、management権限拒否、warning/critical分岐、DLQ不変。
- 起動順全分岐、API/Web readiness内訳、Caddy公開前後smoke。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-033 | Morning排他をOS `flock`＋DB advisory lock `71419602`の二重にする | Reboot前後・手動/systemdの二重実行と、DB別host起動誤りを検出 | Unit/wrapper/PTにlock case |
| SS-D-034 | Credential backupをoffline private key式`age`で暗号化する | Server内backupと復号keyの同時漏えいを防ぐ。UI 251の暗号archiveを具体化 | Package/recipient fingerprint/recovery rehearsal |
| SS-D-035 | Cleanupはrun開始cutoff固定＋chunk commit＋同run resumeとする | 中断再開で対象範囲を広げず、大量DELETE lock/WALをbound | Batch repository、kill/resume IT |

## 16. 禁止事項

- Backup成功rowだけを信用し、dump/manifest/hash現存を確認せず業務dataを削除すること。
- 環境変数・glob・未検証のrootで再帰削除すること。Backup/transfer root自体を削除すること。
- Package update/backup失敗を無記録でsuccess化する、またはbackup失敗だけでapplicationを停止継続すること。
- Expiry/DLQ/journal fileをOSから直接削除、DLQを7日purge対象にすること。
- 再実行で新しいcutoffを使い、元run開始後のdataを追加削除すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 計画停止、backup、cleanup、Expiry、readiness、resume・exit codeを詳細化。 |
| 2026-08-31 | 横断監査でbatch cleanupを331のallowlist済みmaintenance function経由に固定し、文言誤りを修正。 |
| 2026-08-31 | `pg_dump`用SELECTとbatch保守権限を分離する`schubert_backup`案をQA-043/UIC-003として保留。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、専用backup OS/DB role・credential・固定dump commandを確定。 |
| 2026-09-03 | SSC-005を反映し、CLEAN_LOGのSecurity hold期限判定とskipped記録を確定。 |
