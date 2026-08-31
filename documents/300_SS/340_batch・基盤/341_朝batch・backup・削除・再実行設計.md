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

- Maintenance全体の`run_id`はUUID、`business_date`は開始時点のJST日付、`run_started_at`はUTC `Instant`で固定。
- OS排他は`/run/schubert-nk/maintenance.lock`を`flock(LOCK_EX|LOCK_NB)`。DB接続後は固定
  `pg_try_advisory_lock(71419602)`も取得。両方を持つprocessだけcleanup/morningを実行。
- Lock取得失敗は何も停止/削除せずexit 20、SYSTEM/BATCH alert。Lock file本体を手動削除して解除しない。
- 各stepは`batch_runs`へRUNNINGをINSERTし、成功/WARNING/FAILED/SKIPPEDで完了。Process異常のRUNNING残留は
  次回起動時にABANDONED相当のFAILEDとし、同じrun IDの新attemptで再開。

## 4. 05:00計画停止・update・reboot

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
| `CLEAN_LOG` | 90日超、security hold除外 | 10,000 | Chunk単位再開 |
| `CLEAN_BATCH_RUN` | 400日超、RUNNING/FAILED調査中除外 | 1,000 | 証跡保護を優先しskip |

SQL、lock、delete順は332 §11を正とする。Batch roleは基底tableを直接DELETEせず、331 §3.3のallowlist済み
maintenance functionを呼び出す。各chunk commit後にcountを更新する。
Process kill後は未削除rowだけ残り、同cutoff再実行で0件/残件を冪等処理する。

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
