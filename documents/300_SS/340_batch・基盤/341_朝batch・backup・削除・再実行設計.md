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

SSC055/PG163（先行898cc267）: 親step履歴は331 §8.3のBatchRunRepository。root原本/OS lock/子終端を確認したcallerがbegin/finishとcommitを所有する。runとstep時刻を分け、当日非backup成功済みだけ新attempt SKIPPED、backup2stepは毎回実行する。残存RUNNINGは明示同run回復時だけABANDONED相当FAILED、別run/不明root/99超/時計逆転は保全拒否。今回attempt件数とrun累積を混同しない。各step終了値の完全一致再試行だけ冪等にし、未確認child/backup/cleanupをSUCCESSへ補完しない。詳細型・固定診断・transaction・24PTは331 §8.3/017021～024を正とする。

SSC-055/PG-D-158: 固定namespaceの原本file lifecycleは343 §6.15。親はOS flockの内側でscopeを開き、start成功後だけ停止/updateへ進み、reboot後resumeで同activation/cutoffと前回完了の有無を区別する。completeには実子終端・許容morning終端・step永続記録を先に確認する。file側の全graph検証をDB legacy ID非衝突/親の成功証明へ代用しない。

SSC-055/PG-D-156（先行b6b5f0f6）: run_id/cutoffの唯一の原本は343 §6.13のroot永続anchor。DBが停止してもreboot後に同じbyteを復元できる。各保守起動/明示resumeには別activation UUIDを用い、completionはそのactivationにだけ対応する。過去completionを新activationの成功として使わない。原本→activation begin→activeをdurable公開するまでは停止/update/rebootを行わず、親の許容morning終端を確認してcompletion→active消去をdurable確定する。backup失敗時の削除skip/起動継続をこの追加metadataで禁止しない。途中失敗/不明完了はactiveと原本を保全する。原本fileの完成だけで親全体・永続step・GCを実装済みにしない。

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

### 6.4 MANIFEST.jsonの値・byte契約（SSC058/PG165）

先行8a606fc7。以下はmanifest内容の契約であり、実artifact検証・DB成功・root/OS/子終端の代用品ではない。

- Production型は .batch.backup.BackupFileDigest(size,sha256)、BackupVersions(host,app,schema,os,jdk,postgresql,artemis,age)、BackupManifest(databaseStep,configurationStep,startedAt,contentFinishedAt,versions,recipientSha256,dump,configuration,credentials)。file byte codecは .batch.file.BackupManifestCodec.encode/decode。record accessor、計数/名前導出、全内部parse/renderを017033～036/BAT178～193で追跡する。
- 両stepは既存BatchStepAttemptの完全handle（id/run/cutoff/step/attempt/startedAt/skipped）。databaseStepはBACKUP_DB、configurationStepはBACKUP_CONFIG、両skipped=false、idは相異なる、run/cutoffは同一。attempt番号・開始時刻は同一である必要はなく、各完全handleを記録して取り違えを拒否する。DBの実在/状態・同一bundleへの永続bindingは後続で別検証する。
- startedAtは内容生成の開始、contentFinishedAtはdump/list/tar/ageの内容生成終了の観測時刻。両UTC0001～9999・µs、startedAt>=両step.startedAt、contentFinishedAt>=startedAt。fsync/atomic確定/再hash後の最終step.ended_atとは区別する。名前に使うstartedAtのJST年は0001～9999。
- directoryNameはstartedAtのAsia/Tokyo yyyyMMdd-HHmmss＋ハイフン＋canonical run UUID。µsはmanifestに保持し、directory名だけ既定の秒表示。既存同名/partとの衝突は後続CREATE_NEWで拒否し、上書きやsuffix推測をしない。
- 3file名は schubert_nk.dump / config.tar / credentials.tar.age の固定集合。各sizeは正long、SHA256はlowercase64hex、3size合計はlong overflowしない。configurationBytesは後2fileの合計、totalBytesは全3file。manifest自身のsize/hashを内部へ循環記載しない。recipientSha256もlowercase64hexで、元public recipientのfingerprintをcallerが独立算出する。
- host/app/os/jdk/postgresql/artemis/ageは各ASCII1～128byte、先頭英数字・後続英数字または . _ + - の非秘密release token。schemaは001～999の3桁。任意command出力/path/credential/JSON/制御文字を受け入れず、versionが実環境と一致するかは生成側で別確認する。public診断toStringは値全体をredactする。
- 全nullはconstructor/API境界で拒否し不変条件を先に確立する。型/範囲/format不正は固定IllegalArgumentException、NULLはnull契約違反。decodeでJDK/parseのraw入力をcause/suppressedへ出さない。入力byte/返却byteのmutable所有を共有せず、同一不変modelの並行encodeを許す。
- Canonical JSONは下記順・key名と固定database名、ASCIIのみ、余白なし1行＋末尾LF1つ、最大4096byte。数値は符号/先頭0なし10進（size/id/attemptは正）。UUIDはlowercase36、時刻は必ずyyyy-MM-ddTHH:mm:ss.ffffffZ。意味上同じでもkey順違い/空白/CRLF/BOM/escape/大文字hash/省略µs/指数数値/unknown/duplicate/欠落/NULL/末尾追加は拒否。全string値が上記ASCII許可集合に収まるためescapeを生成しない。
- decodeは固定schema全fieldを構築し、再encodeとのbyte完全一致も確認する。dateの自動補正/別表現を許可しない。独立goldenをProduction encodeで生成しない。
- 形式: {"format":"NKBACKUP1","database":"schubert_nk","runId":"<UUID>","cutoff":"<UTC6>","startedAt":"<UTC6>","contentFinishedAt":"<UTC6>","databaseStep":{"id":<N12>,"attempt":<N2>,"startedAt":"<UTC6>"},"configurationStep":{"id":<N12>,"attempt":<N2>,"startedAt":"<UTC6>"},"versions":{"host":"<token>","app":"<token>","schema":"<N3>","os":"<token>","jdk":"<token>","postgresql":"<token>","artemis":"<token>","age":"<token>"},"recipientSha256":"<hex64>","files":{"schubert_nk.dump":{"size":<positive long>,"sha256":"<hex64>"},"config.tar":{"size":<positive long>,"sha256":"<hex64>"},"credentials.tar.age":{"size":<positive long>,"sha256":"<hex64>"}}} LF
- 制約として、この型は「申告された観測値」が整合することだけを保証する。actual dump/list/age/restore・3file metadata/hash・全file集合・原本/DB両stepへの信頼binding・成功後7世代削除は別必須。archive平文/秘密key、任意path、未検証claimからSUCCESSを生成しない。

### 6.5 実backup artifactのread-only検証（SSC059/PG166）

先行4da9e96b。BackupArtifactVerifierは「信頼されたmanifest申告値と現存byteの一致」を検証する。生成/復元/age実行・fsync/rename・DB成功・rootのmanifest binding・7世代管理は別必須であり、本部品成功で補完しない。

- 親rootはOS排他とbackup rootの設定/非重複/realpath/FS権限・durability能力を別途確認してから、保持したOwnedTransferDirectory、専用schubert-backupのUID/GIDを渡す。UID/GIDは1～unsigned32上限、実効UID0。rootを閉じたり任意pathを再解決せず借用する。NASのサーバ側ACL/fsync保証を単なるUnix mode/読取成功で証明したことにしない。
- verify(BackupManifest)はdirectoryNameで既存子だけをNOFOLLOWで保持する。backup rootと子は専用backup UID/GID・0700・directory/nlink>=2、RW・ACLなし。子は親と同device。子の全entryはMANIFEST.json/schubert_nk.dump/config.tar/credentials.tar.ageの正確な4件（重複/NULL/未知/不足を拒否）。part名や別runへfallbackしない。
- dumpは専用backup UID/GID・0600、config.tar/credentials.tar.age/MANIFEST.jsonはroot:root0600、regular/nlink1。全fileは子と同deviceで、manifest3fileの正sizeと一致する。MANIFEST.jsonは341 6.4のcanonical encode長とbyte完全一致。親rootが最終manifestを作成する責務をここで固定するが、格納先親がbackup主体所有であるため別の信頼bindingなしにmanifest自身を信頼しない。
- 各保持inodeのmode/uid/gid/nlink/size/dev/ino/mtime/ctime・ACLをIO前後に照合。読取り前後のchannel.sizeを別観測し、最終EOFも確認する。65536byte bufferでstreaming SHA256、残長を超えて読み進めず0byte進捗も固定失敗。fileの途中短縮/過長/変更/同名差替えを成功にしない。MANIFESTの期待byte/hashはcallerの信頼manifest由来だがPTの期待値はProduction codecから生成しない。
- 全4file読取後、全entryを名前から再保持して元snapshotと照合し、正確な全file集合と子snapshot・親から再openした子identity・借用root snapshotを再確認。byte内容を変えず通常readによるatime更新は比較しない。敵対rootや検査後の第三者変更をこの一回の検査で封じ込めたとは主張せず、親排他/actor停止・最終使用時再検証を維持する。
- 全操作はinstance内直列化し、所有child/entry/channelを閉じた後だけ実測MANIFESTのBackupFileDigestを返す。path/FD/channel/ファイル集合やarchive内容を結果へ公開しない。既存fileの作成/chmod/chown/書込/unlink/sync・root closeをしない。
- 単調時計30分と割込を各IO境界/読取loop前後・最終帰還前で確認する。期限以上/割込は固定非成功・flag保持。blocking OS readをJava協調検査で強制中断できるとはしない。clock引算は既存30分契約同様wrapを許し、逆転は拒否する。
- nullは境界/invariant契約違反として拒否しNPEを正常化しない。IO/既知不正状態/crypt provider失敗は固定StorageIoException、raw path/bytes/cause/suppressedを出さない。未知Runtime/Errorのidentityを保持し、cleanup IO失敗を添える場合も固定診断だけ。bufferは全終了で消去し、close失敗を成功へ算入しない。
- Production class/内部port・snapshot/安全close helperは.file.BackupArtifactVerifierの責務内、全public/private methodを017038/039/PT-BAT-194～209へ追跡する。package/module依存は既存Storage/Batch/Java標準のまま。PTは実Linux保持inode・公開合成byteと非特権metadata adapterを区別し、実root配布/NAS/IT/STの完了を宣言しない。

### 6.6 root manifestとbackup両stepの原子的確定（SSC061/PG168）

先行26fb3bad。root生成manifestを信頼binding recordとして扱うが、単なるJava値の受領は信頼確立ではない。rootが内容生成成功・実byte照合後にCREATE_NEW/0600でmanifestを生成し、writerを全close、fsync/atomic確定/再hashすること、読取側がuid0/gid0/0600/nlink1/ACLなし・保持inode/前後属性・canonical byte・namespace・原本run/cutoffを確認することが別の必須条件。backup user作成inodeのchownで真正化しない。低権限者が親directoryを変更してもroot所有file内容は改変できず、別の真正manifestへの入替えは全handle/name/hash照合で拒否、同一真正bundleの再使用だけ冪等である。root侵害や保守中の管理者変更を本方式が封じ込めるとはしない。PG166の期待値照合だけで生成元を証明せず、生成・信頼readerは後続実装する。

- Production .repository.BackupStepRepositoryは借用親Connection、.backup.BackupCommitServiceは同借用Connectionのtransaction境界を所有する。原本/OS排他/停止/実artifactの継続保全はcaller、DB専用backup credentialは使わず既存schubert_batchを使う。新table/FK/DDL/grantは追加せずV001～020不変、400日/7世代保持不変更。
- inspect(manifest,observedAt)は親explicit read-write READ_COMMITTED transaction、自己DB advisory・run identityをRunReferenceRepositoryで前後検査し、2idを昇順FOR UPDATEで読取る。query timeout5秒。全14列id/run_id/business_date/step/attempt/started_at/ended_at/status/target_count/success_count/failure_count/byte_count/error_code/error_summaryの所有ResultSet/Statementを閉じるまで返さない。WHERE id INの行を信用せずmanifest完全handle2個と各列を照合し、欠落/余分/重複/NULL/未知/取り違えを拒否する。
- 観測時刻はUTC0001～9999/µsでcontentFinishedAt以上。DB/CONFIGの両方RUNNINGだけはended=NULL、4counts0、error2列NULLを要しOptional.empty（未完了）。両SUCCESSだけは共通ended>=contentFinishedAtかつ<=observedAt、µs、error2列NULLを要す。DB target=success=1/failure0/bytes=dump.size、CONFIG target=success=2/failure0/bytes=configurationBytes。これは対象file数でmanifest自体を数えない。片SUCCESS・異なるended・WARNING/FAILED/SKIPPED/未知status・別run/pair/handle・count不正を未完了から補完せず保全拒否。
- complete(manifest,endedAt)はinspectを先に行い、両SUCCESSなら保存済共通endedだけを返し現在時刻で書き換えない。両RUNNINGならBatchRunRepository.finishでDB→CONFIGの順に同一endedAt/SUCCESS/NONEと上記独立count/byteを記録し、再inspectで両確定値の一致を確認する。Repositoryはcommit/rollback/connection closeをしない。途中失敗は呼出側が全rollback、片方だけcommit禁止。
- BackupCommitService.complete(connection,manifest,endedAt)は入口autoCommit=true/read-write/READ_COMMITTEDを要求し、割込を前後確認、setAutoCommit(false)→Repository complete→commit→setAutoCommit(true)→割込再確認→保存end返却。既知SQL/Repository failureは固定BatchRepositoryException。transaction処理の失敗はrollback成功後だけautoCommitを復元し、rollback失敗なら復元しない。commit不明は成功にしないが次回同manifestのinspectで永続両SUCCESSを再読できる。後commitの復元/割込失敗も今回返却は非成功、保存済み結果を上書きしない。全障害後のconnection破棄はcaller必須。
- 未知Runtime/NPE/Errorを正常扱いせずprimary identityを保持、既知cleanup SQLのsuppressedは固定例外。input/cause/SQL/manifest値を診断へ出さない。全API nullを境界で拒否、Connectionはcaller単独所有、異なるconnectionの並行呼出しだけを許す。
- 017041～044/BAT210～225で独立合成manifest/SQL後条件、borrowed read/complete・全列/全JDBC位置/NULL/close/割込/commit不明/rollback/2connection・同ID再試行を検証する。new部品の全line/method/class/branch100%、全既存PT/static/traceを再実行。成功rowだけでcleanup許可せず、生成/信頼reader/最新真正bundle選択/親全体/7世代/実NK CHR/IT/STは未完了。

## 7. Business/technical cleanup

### 7.1 必須gate

SSC-049/PG-D-148: 親OS lock保持下で、削除開始前にAPI/Web各unitのId/LoadState/ActiveState/SubState/Job/MainPID/ControlPIDを固定systemctl showで読み、対象Id一致・loaded/inactive/dead・Job空・PID各0を全件確認する。not-found/masked/failed/active/遷移中/残job・PIDは通さない。7fieldは各1回、ASCIIのみ・末尾LF1つ・1～1024byte、未知/重複/欠落/CR/NULは失敗。unitごと5秒、非zero/IO/close/timeout/interruptは無条件に後続不可、割込flagを保持する。前後の割込確認と再実行時のfresh観測を必須とし、古い結果をcacheしない。これは停止実行やcgroup全検査ではない。親は保守中の再起動を禁止し、通常stop timeout/TERM/復旧の既存設計を維持する。

- 同じ`business_date`のBACKUP_DBとBACKUP_CONFIGがSUCCESS。Dump/manifest directoryが現存しhash再照合済み。
- `run_started_at`を全DELETEのcursor/cutoffに使い、実行中の現在時刻で対象を広げない。
- API/Webはinactive、DB batch advisory lock取得済み。未満足は削除0件でSKIPPED/FAILEDを記録。

### 7.2 Step順

SSC057/PG164: 非Log/非秘密Inboxの7kindは331 §3.14のStepCleanupService→CleanupStepRepository→V020を使用し、DELETE/step累積を一緒にcommitする。borrowed親Connectionはchunk間だけautoCommit=true、既取得自己session lock/OS排他を保持し、各chunk前後に30分・interruptを検査する。完了はchunk0＋残候補0の実確認後、FKdeferredは保全した非完了として親へ返しWARNING/次回保持の判断を維持する。backup/lock/SQL/commit不明は未完了、rollback成功前のautoCommit復元は禁止。shared step内の別kind累積・今回service差分を区別し、finishは親が全kind・実Inbox/Log等を照合した後だけ行う。実親結線/全清掃完了はこのserviceだけでは成立しない。

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

SSC049/PG162（先行d23b1afd）の親summary・attempt照合: 子へのDB引渡し前に331 §3.13の同run summaryをOptionalで読み、未開始0行は「未開始」として保持する。子のfresh起動・実終端・wrapper結果を別途確認してDB lockを再取得した後、同run/cutoffのsummaryを再読する。after不存在/未END/別identity、receiptが0/10以外、保護あり累積とreceipt10の不一致は非成功。beforeが存在すれば同identityで全3累積の非減少が必須。before既ENDならafterのcounts/ENDが完全不変でなければ非成功。attemptはafter累積−before累積（before不存在の差分基準だけ0）、run累積と分けて記録する。既完了再開のattempt0でも累積保護ありならWARNING10を維持する。現在時刻/推測cursor/receiptだけから件数を補完しない。純照合関数は不正を固定IllegalArgumentException、nullは契約違反とし、引数値を診断へ出さない。返却型もattempt各値<=cumulative、0/10と累積保護の整合をconstructorで保持する。実子unit・OS排他・実backup/親step記録の接続は引き続き別必須条件。

UIC-006の検査をbackup成功後のcleanup内部で実施する。通常API/Web inactive条件、固定run/cutoff、backup gateを維持する。検査中はHTTP/JMS Consumerを生成せず、DB snapshot/参照の検査だけを行う。batchのadvisory lockを別connectionから二重取得して自己deadlockさせないよう、検証・削除chunkのconnection/lock所有者を実装前に明示する。検査前後のlock断絶や他runの結果流用を許可しない。異常行は削除せず固定理由・件数だけを返し、暗号文・平文・鍵をbatchへ渡さない。SQL/権限/oneshot wiringのPT完了まで本stepを完了扱いしない。

SSC-049/PG-D-122のlock所有: 親batchはOS flockを保守全体で保持する。検査を開始する前に前段transactionを完了しDB session advisory lockを解放し、専用processが自身のDB transactionで71419602を取得してから候補を検査する。検査・DELETE・commitの間にlockを渡さない。親はprocess終了後にDB advisoryを再取得して後続へ進む。引渡し区間に別DB主体がlockを取得した場合、検査側/親の再取得失敗は失敗として停止し、検査未実施を成功にしない。OS lockを放す実装や、検証済結果を別transactionへ渡す実装は不可。実oneshot/異常終了の試験は後続gateとし、SQL単体PTで実運用結線完了とはしない。

SSC-049/PG-D-150（先行0797b369）: InspectorLockHandoffは親の単独所有Connectionを借用する同期境界。開始割込・nullを拒否し、autoCommit=true/readOnly=falseを確認。pg_catalog.pg_locksの自身backend・現在DB・classid=0/objid=71419602/objsubid=1・ExclusiveLock/grantedを照会して既保持を確認する（shared/two-int別namespace不可）。pg_advisory_unlockを1回だけ行い、自己保持なしを再照会する。再入取得が残る場合、余分なunlockで強制解除せず子0回で失敗。各SELECTはqueryTimeout=5秒、結果1行/non-null Booleanだけ、全ResultSet/Statement close故障も非成功とする。

上記完了後だけ同期callbackを1回呼ぶ。callbackは同runの検査子の終了確認まで復帰せず、親connectionを操作/共有せず、秘密情報を返さない。全callback終了（IO/Runtime/Error/nullを含む）のfinallyで親のautoCommit/readOnlyを再確認し、pg_try_advisory_lockと自己保持再照会により再取得を確認する。競合/SQL不明は失敗、待機lockやunlock反復をしない。全再取得/close確認後だけnon-null値を返し、最後の割込もflagを保った非成功にする。借用connectionのcommit/rollback/closeをせず、失敗後はcallerが必ず破棄する。SQL/IOのraw cause/suppressedは固定Failureへ正規化し、未知Runtime/NPE/Errorは正常化しない。callbackの結果だけでCLEAN_INBOX SUCCESSを記録せず、既存receipt/同run永続progress照合は別必須。OS lock・停止/backup・実子unit・credential/run束縛の確認はcallerの未完了gateとして残る。

SSC-049/PG-D-127再開状態: 専用processは331 §3.8の永続progressを同run/cutoffでlockして読み、候補処理とcursor/件数を同transactionで確定する。各row transactionを1件chunkとして使うため1,000上限を超えず、processは最大1,000回ずつのbounded呼出しを繰り返し30分のunit制限内でENDまで進む。途中中断は未完了、最終ENDでのみ検査stepをSUCCESS（保護0）またはWARNING（保護あり）へ集約する。未対応/不正rowもcursorを進めて保護件数へ加算し、先頭同一rowの無限再走をしない。commit不明時は同runでDB状態を再読取りし、削除済み行の件数を失わない。親attempt件数はそのattempt開始時/終了時の累積差分、run累積は別項目とする。既完了runは保存状態を返すだけ、鍵/参照修復後の再検査は新しい保守runで行う。CLEAN_BATCH_RUNでは完了progressの400日保持とRUNNING/FAILED調査保護を確認し、331の専用清掃関数で削除する。SQL/Javaだけでは専用unit/親のOS lock引継ぎ・backup実体gateは未完了。

SSC-050/PG-D-129: 全maintenance_cleanupの第2引数は固定run_started_atとし、log90日・batch履歴400日の保持閾値をcaller側で二重に差し引かない。SQL側でも当日backupの状態・終了・同runをrow lockの単一snapshotで再検証する。Batch履歴は完了ended_at基準、現在runと同run内のRUNNING/FAILED調査中を保持する。親processの実backup照合とOS lockは別途必須であり、このSQL補正で省略しない。

SSC-049/PG-D-130: run executorは324 §12.7の単調時計30分とinterruptを各最大1,000呼出しchunk前後で確認する。END/保護0だけSUCCESS、END/保護ありWARNING、途中停止/DB障害はFAILED相当50。最後の確認済み累積値を「最新総数」と誤記せず、次attemptは同runで永続状態を再読する。30分はprocess unit上限でも維持し、Java協調停止だけで長時間SQLの強制停止を保証したとしない。親の実backup/key/OS lock/終了後close検証は別gate。

### 7.4 Inspector unitのfresh終端観測（SSC060/PG167）

先行81e0e64b。これはread-onlyの観測部品でありstart/stop/OS排他/quarantine/DB summary接続ではない。341 §7.3の同期callbackは実子終端まで戻らず、古いunit結果やPID2値だけを終了証明にしない。

- .batch.platform.InspectorUnitSnapshotは固定unit schubert-nk-inbox-inspector.serviceのshow出力18propertyをparseする。Id/LoadState/ActiveState/SubState/Job/MainPID/ControlPID/InvocationID/ExecMainCode/ExecMainStatus/ExecMainStartTimestampMonotonic/ExecMainExitTimestampMonotonic/Result/Type/Restart/RemainAfterExit/KillMode/SendSIGKILL。順序は不問、各1回・集合完全一致、ASCII1～2048byte・各行LF・末尾LF1、CR/NUL/高bit/未知/重複/欠落を拒否する。値に任意path/command/改行を持ち込まない。
- Id完全一致、LoadState=loaded、Type=oneshot、Restart=no、KillMode=control-group、SendSIGKILL=noを必須とする。RemainAfterExitはyes/noの観測値（現行unit設定はnoを維持）。他状態・ResultはASCII小文字の英数/hyphen1～64token、Jobは空または1～uint32のcanonical decimal、PIDは0～uint32、ExecMainCode0～6/Status0～255、monotonic µsは0～uint64のcanonical decimal。先頭0/符号/空白/overflowを拒否し、InvocationIDは空またはlower32hexの非nil ID。すべて型/範囲を構築時検査し、不変snapshot/toString redactとする。
- snapshot.quiescentはJob空・MainPID/ControlPID0かつ inactive/dead、active/exited、failed/failedのいずれかの必要条件だけ。これ単独を全process終端証明にしない。fresh receiptはその条件に加え今回InvocationID非空/開始前のOptional IDとは別、ExecMainStart>0、Exit>=Start、ExecMainCode=1、ExecMainStatus=0または10、Result=success、active/exitedまたはinactive/deadが必要。failed/failedやsignal/timeout、開始未観測、古いIDはreceiptなし。0/10をsystemctl clientの終了codeへ混同しない。今回runとの対応は親が同run環境の寿命とfresh起動を別途保証する。
- InspectorUnitProbeはread()、quiescent()（Optional snapshot）、completionAfter(Optional<UUID>)を供給する。quiescentはread→必要条件→固定GetUnitProcessesの正確なASCII `a(sus) 0\n`→再readで全18property不変、全command成功/資源解放/割込なしの時だけ存在する。非空/未知/過長process出力は終了を認定せず、command内容やPID/commandlineをlog/evidenceへ保存しない。Main/Control PIDとcgroup再帰の独立確認を重ね、TasksCurrent欠落を0としない。
- showは /usr/bin/systemctl --system --no-pager --no-ask-password show --property=<固定18field> <固定unit>。process照会は /usr/bin/busctl --system --timeout=5s --no-pager call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager GetUnitProcesses s <固定unit>。shell/環境任意commandを介さず、既存NativeProcessのclear-env固定5変数（PATH/LANG/LC_ALL/SYSTEMD_COLORS/TERM）・stderr破棄を使う。show受信2049byte/process受信10byteで上限を検出、process空vectorは9byte。読取command各5秒、非0/IO/timeout/割込/null resourceは合格にしない。
- 全stdioを取得順に所有し、後続getter/IO/close失敗でも先行資源を閉じる。known IO/停止例外は既存StopGateExceptionの固定message/reasonへredactしcause/suppressedにrawを出さない。unknown Runtime/NPE/Errorは正常化せずidentity保持、既知cleanupのsuppressedも固定化。読取query自身へのTERMは可、SIGKILLは禁止。query子終了とInspector unit全終端は別概念。生byteはparse/比較後に消去し、値を外へ返す前にも割込flagを保持して再確認する。
- 未開始/GCによるInvocationID欠落、途中遷移、manager故障は成功ではない。現在RemainAfterExit=noなので取り逃した終端を古い結果で補完しない。後続controllerで結果保持設定/新起動barrier・起動不明時の停止待ち/OS lock寿命・SIGTERM shutdown・再開admissionを具体化する。期限を過ぎて子が残る場合に正常callback returnしてOS lockを閉じる実装は禁止する。
- OPS009/UI251/SS311/341/343、018021～024/PT-OPS-UNIT-001～016。単体は独立18field literal・公開process mockと実ローカルread-only tool確認、全resource/NULL/境界/並行/4coverage・静的解析を行う。本番root/systemd配布や実unit起動のIT/ST合格ではない。

一次資料（2026-09-13確認）: [systemd v259 D-Bus](https://raw.githubusercontent.com/systemd/systemd/v259/man/org.freedesktop.systemd1.xml)、[service](https://raw.githubusercontent.com/systemd/systemd/v259/man/systemd.service.xml)、[dbus-unit.c](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/dbus-unit.c)。GetUnitProcessesはcgroup再帰とmain/control PIDを集約する。ExecMain時刻は現在または直前の実行で、fresh対応を別途確認する必要がある。

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
