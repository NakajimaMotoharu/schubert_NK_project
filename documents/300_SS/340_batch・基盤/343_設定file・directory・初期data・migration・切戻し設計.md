# 設定file・directory・初期data・migration・切戻し設計

SSC063継続/PG174・BUG195/YKT154: ConfigurationGroupResolverの3stdio・reader executor・join前TERM・最外TERMを明示scopeにする。IO/Interrupted primaryと未知Runtime/Error cleanupの競合は未知cleanup優先、Interrupted flag保持、未知primaryとcleanupは元identity＋固定IOException secondaryとする。IOだけの失敗は既存固定IOException、非同期readResultのRuntime固定診断・Error identity・NSS65537byte境界・5秒/全getter後null検査/TERM-before-join/全buffer消去を維持。StopGate専用scopeでIOExceptionを別の公開例外へ変換せず、このclass内のchecked IO用scopeを使う。executorは所有reader終端までjoinし、TERM無効・OS/NSS無応答を成功と扱わない。JDBC契約の横展開は別途残す。

SSC063継続/PG173・BUG195/YKT154: SystemctlStateSourceのstdout/stdin/stderr・照会process TERMを、InspectorUnitProbeと同じ既知Stop/IO/Interrupted対未知Runtime/Errorのclose優先順位へ統一する。同じ例外のself-suppressionを禁止し未知bodyを同一identity＋固定Stop secondary、既知body＋未知cleanupは未知cleanupと割込flagを保持する。Probeの既存狭いscopeをpackage内ProcessResourceScopeへ移し両照会から利用する。Systemctlの全getter取得後null検査・逆順stdio close・最後に生存childだけTERM・5秒/固定8引数/1025byte上限・固定環境を変更しない。戻す予定の読取byteは全cleanup成功前に返さず失敗時消去する。サービス変更/SIGKILL/外部診断やcredentialの出力は禁止。ConfigurationGroupResolver/Future/JDBCの残候補は別段。

SSC063継続/PG172・BUG195/YKT154: MaintenanceFileLockのrun/app取得・再照合、InspectorEnvironmentFilesの5 root取得・再照合、MaintenanceRunFilesの6 root取得・再照合とnames列挙を共通ResourceScopeへ横展開する。取得順・取得直後のadmission順・逆順一度close・Session無効化の時点・static参照byte消去・失敗時run環境保持・borrowed能力を変更しない。DirectoryIteratorExceptionは列挙body内で既知IOへ固定化してからcloseし、未知cleanupを隠さない。未知bodyと同じThrowableをcloseが投げても元identity＋固定secondary1、既知IO bodyと未知cleanupは同じ未知cleanupを伝播する。Runtime/NPE/Errorを正常化せず、入力null契約と公開仕様を維持する。process/JDBC候補は別段で未完了を維持する。

SSC063継続/PG171・BUG195/YKT154: 同じIO close優先順位をDurableRecordFiles.readFile/write/force、InspectorEnvironmentReader.readFile、InspectorEnvironmentPublisher.writeNew/forceExisting、ExistingFileAccess.walkのchannel/childへ適用する。nullable IO resourceは従来の固定IO拒否（ExistingFileAccessのnonnull channelは境界NPE拒否）を所有受領前に実施し、callbackの値/IO順/サイズ/metadata/partial保全/借用root・非公開能力を変更しない。8所有scopeを既知IO＋未知cleanup/同一未知body＋cleanupの各Runtime/NPE/Error3型で独立再試験する。Directory/Process/JDBC等の残候補は別段で未完了を維持する。IO型と回復責務を変える一般frameworkや追加coverage除外は採用しない。

SSC062/PG169: 341§6.7のreaderはcallerがadmitした保持backup rootから正規単一子/MANIFEST.jsonだけを読む。専用backup UID/GIDの0700 root/子とroot:root0600/link1のfile、同device/ACLなし/RW、typed前後属性と1～4096byte/canonical/原本両handleを確認する。rootのCREATE_NEW生成・FS durability/NAS保証・実archive生成/再hash/7世代は別責務であり、readerの成功を代用しない。既存directory/config/credential配布先や権限を変更しない。

SSC060/PG167（先行81e0e64b）: 341 §7.4の固定Inspector unit18property・GetUnitProcesses空配列と前後snapshotを、親のfresh終了観測へ使用する。実InvocationID/commandline/process一覧は設定/証跡へ保存せず、独立合成vectorだけで単体検証する。現行unitのRemainAfterExit=no/固定起動wrapperは本変更で変えない。古い状態の流用、query process終了を実検査unit全終端へ代用、start結果不明のままOS lock解除は不可。018021～024/UNIT001～016を追跡し、実親start/stop/quarantine/原本・DB結線は引き続き未完了。

## 1. 目的・追跡

SSC-049/PG-D-148: read-only照会は`/usr/bin/systemctl --system --no-pager --no-ask-password show --property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID <固定APIまたはWeb unit>`だけ。子環境はclear後にPATH=/usr/bin:/bin、LANG/LC_ALL=C、SYSTEMD_COLORS=0、TERM=dumbのみ設定し、親credential/envやbus address overrideを引き継がない。stderrはdiscard、stdoutは終了後最大1025byte読取で過長を拒否、固定projectionを出す信頼OS binaryが前提。5秒wait timeout時は照会子processへTERMを要求し失敗、SIGKILLやservice stopへ置換しない。全stdio close完了前の成功返却は禁止。敵対rootがbinary/systemdを差替える場合や、TERMを無視するOS障害の強制解消は保証しない。実対象unit不在でもcommandがexit0/inactiveを返すため、必ずLoadState=loadedを検証する。PTでは実read-only診断と制御Process portを区別して記録する。

SSC-049/PG-D-147: root管理のboot時tmpfiles設定は/run/schubert-nk0755、maintenance0700、maintenance.lock0600を固定root:rootで配布する。既存service子directoryの到達性を保つため共有親を0700へ変えない。lockfileは空regular/単一link、local /runのRW tmpfsだけ許可し、稼働中の再作成・削除・権限修復を禁止する。MaintenanceFileLock公開factoryは固定pathとnative portだけを生成し、実行時UID0を先に検査する。保持inodeのmetadata/ACL/FS・再open identityを検証して既存LinuxFileLockへ接続、path/FD/例外causeを結果へ公開しない。PTのroot metadata合成は非特権fixtureの実Linux IO/flockとの接続検証であり実root配置の合格ではない。起動時tmpfiles実行・権限配布・privileged親unit・停止/backup/DB引渡しは後続gate。

SSC-049/PG-D-146: maintenance.lockは親root管理のlocal runtime namespaceへ配布し、保守中にpathを置換/削除しない。低位LinuxFileLockは保持済み/proc/self/fd能力を借りてflockするだけで、root/file owner・ACL・regular type・link・配置を検証するfile adapterの代替ではない。任意path/符号付き・範囲外FD表記/未知platformを拒否し、native診断/physical pathを例外へ出さない。親の配布・起動結線は別PG/PT gate。

Source/release/config/credential/data/log/runtimeの配置、環境差分、設定key、初期data、Flyway DB migration、
現行asset/metadata移行、切替・切戻しを実行前checkと証跡を含めて定める。

- 上位設計: UI 243、251、253～254、261、264
- 関連RD: SCP-002～SCP-005、MIG-DAT-001～MIG-DAT-008、MIG-001～MIG-008、SCM-001～SCM-006、
  FIL-001～FIL-005、TST-001～TST-005
- 関連QA/RDF/UIC: QA-007、QA-012～QA-016、QA-022、QA-024、QA-043、RDFなし、UIC-003
- 関連SS: [331_DB物理・DDL・index・権限設計](../330_データ・ファイル/331_DB物理・DDL・index・権限設計.md)、
  [342_Caddy・systemd・PostgreSQL・Java設定設計](342_Caddy・systemd・PostgreSQL・Java設定設計.md)

## 2. Directory・owner・Git管理

| Path | Owner/mode | 内容 | Git/release |
|---|---|---|---|
| `/opt/schubert-nk/releases/<version>` | root:schubert 0750、file 0640 | Immutable jar、DB migration、ops tool、manifest | Artifactはrelease package、sourceはGit |
| `/opt/schubert-nk/current` | root所有symlink | Active releaseへのatomic pointer | Git対象外、ターゲットversionはmanifest |
| `/etc/schubert-nk` | root:schubert 0750 | Rendered非秘密YAML/env/config manifest | TemplateだけGit |
| `/etc/schubert-nk/credentials` | root:root 0700、個別root:service 0600 | DB/MQ/AES/HMAC/backup credential source | Git/artifact/normal log禁止 |
| `/srv/schubert-nk/data/assets` | data owner:schubert-read 0750 | Scenario/audio/video/musicの永続実体 | Asset本体はGit禁止、manifestは取扱承認後 |
| `/srv/schubert-nk/data/transfer` | schubert-api:schubert-web 0750 | API `.part/.ready`、Web read | Git禁止、次回朝削除 |
| `/srv/schubert-nk/backup` | schubert-backup 0700 | 7世代dump/config | Git禁止 |
| `/var/lib/schubert-nk/artemis` | schubert-artemis 0700 | Broker instance/journal/paging | Git禁止、config templateはrelease |
| `/var/lib/schubert-nk/maintenance` と `runs`/`attempts` 子dir | root:root 0700、file0600。共有祖先はroot:root0755 | SSC-055の不変run原本・activation/完了・active metadata。local永続RW、tmpfs不可 | 実体Git禁止、provisioning雛形/独立fixtureだけGit |
| `/var/log/schubert-nk` | service group 0750、file 0640 | File logを使う場合のみ | Git禁止、journald優先 |
| `/run/schubert-nk/<service>` | systemd RuntimeDirectory | Lock/socket/temp metadata | Rebootで消去可 |
| `/srv/schubert-nk/staging/<run-id>` | migration user 0700 | 移行中asset/manifest、対象run限定 | Go/切戻し完了まで隔離 |

Directoryはprovisioningで明示作成し、application起動時に不明rootを自動作成/chmodしない。
SSC-079/BUG-253/YKT-191: release/configの`root:schubert`0750/非秘密file0640は両Java serviceが`schubert`補助groupを明示して読む。service専用primary groupと既存asset/transfer用補助groupは不変。`/etc/schubert-nk/credentials` root:root0700とservice private LoadCredentialを`schubert`へ公開しない。実OS account provisioningとsystemd起動後読取・秘密拒否はLinux ITで検証し、templateのdirective照合だけで実配布済みとはしない。
SSC-020: Transfer rootはschubert-api:schubert-web 0750を維持する。APIは専用primary group＋schubert-web supplementary membershipで、新規作成した保持inodeだけをchgrpし、date0750/part0640へ確定する。既存date/part/readyのmode/groupを補正して受理しない。API/Web credentialとprivate runtimeの600境界を維持し、共有group追加を秘密fileの公開理由にしない。
Asset/transfer/backup/log/Artemis/stagingを同一または相互配下、またはsymlink接続しない。

## 3. Release package構成

```text
releases/<version>/
  web/schubert-nk-web.jar
  api/schubert-nk-api.jar
  batch/schubert-nk-batch.jar
  lib/schubert-nk-protocol.jar
  lib/schubert-nk-storage.jar
  db/migration/V*.sql
  config/templates/*.yml
  config/caddy/Caddyfile.template
  config/artemis/broker.xml.template
  systemd/*.service
  systemd/*.target
  systemd/*.timer
  operations/bin/schubert-nkctl
  operations/runbooks/
  VERSION
  RELEASE-MANIFEST.json
  SHA256SUMS
```

`RELEASE-MANIFEST.json`はapp/protocol/schema/config version、Git commit/tag、JDK/build tool/dependency/BOM、OS対応、
全artifact hashを持つ。Release directory全fileを検証後にread-onlyにし、稼働中の上書きを禁止。
SSC-021のstorage version/hashもmanifestへ記載し、Web/API（batch使用時も）で同一artifactを使用する。Executable内へ同梱する場合もSBOM/hashの一致を検査し、異なるnative能力実装を混在させない。

## 4. Config file・設定sourceの優先順

| 優先 | Source | 用途 |
|---:|---|---|
| 1（低） | Jar内default | 上位で確定済みの非環境値、安全なfail-closed default |
| 2 | `/etc/schubert-nk/common.yml` | protocol/timezone/monitoring共通 |
| 3 | `/etc/schubert-nk/<web|api|batch>.yml` | Process別port/pool/path/retention |
| 4 | `/etc/schubert-nk/<service>.env` | JVM option、config file location等の非秘密 |
| 5（高） | systemd credential/config tree | DB/MQ password、AES/HMAC key、backup recipient等のsecret |

Command line引数でapplication property実値を上書きしない。未知key、重複・非推奨alias、placeholder未解決、
secretのYAML/env格納、型/範囲不正は起動失敗。Effective configはsecret値を`<redacted>`にしcanonical hashを保存。

## 5. 主要設定key

### 5.1 Common・Web

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.protocol.version` | `001` | 完全一致、UI 232 |
| `nk.time.display-zone` | `Asia/Tokyo` | Wire/viewだけ、DB/JVM UTC |
| `nk.monitoring.mode` | `STANDARD` | STANDARD/DEBUG、UI 252 |
| `nk.web.http.address/port` | `127.0.0.1` / `8080` | Loopback |
| `nk.web.management.port` | `8081` | Loopback、Caddy非proxy |
| `nk.web.mq.reply-timeout` | `2s` | 100ms..2s、UI 212/253 |
| `nk.web.mq.wait.initial/max` | `12` / `20` | max<=20 |
| `nk.web.session.idle-timeout` | `8h` | UI 226、無断短縮禁止 |
| `nk.web.session.max-per-user` | `2` | APIが最終強制 |
| `nk.web.storage.asset-root` | `/srv/schubert-nk/data/assets` | absolute real dir/read-only |
| `nk.web.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | absolute real dir/read-only |
| `nk.web.media.max-streams` | `20` | 1..20 |
| `nk.web.media.max-range-bytes` | `1048576` | UI 223/237と完全一致 |

### 5.2 API・JMS・DB

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.mq.url` | `tcp://127.0.0.1:61616` | Loopback/coreのみ |
| `nk.mq.sync-request/reply` | UI 231のAddress名 | 321のallowlistと完全一致 |
| `nk.mq.async-work/web-log/dlq/expiry` | UI 231のAddress名 | Unknown禁止 |
| `nk.api.sync-consumers.initial/max` | `4` / `8` | DB pool<=8 |
| `nk.api.async-consumers` | `1` | 固定、変更禁止 |
| `nk.db.url` | `jdbc:postgresql://127.0.0.1:5432/schubert_nk` | Loopback、parameter allowlist |
| `nk.db.pool.api.max/min` | `8` / `2` | UI 253 |
| `nk.db.pool.web.max/min` | `2` / `1` | UI 212の初期上限2、Technical schema専用 |
| `nk.db.connect-timeout` | `3s` | UI 212 |
| `nk.api.storage.asset-root` | `/srv/schubert-nk/data/assets` | read-only |
| `nk.api.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | write、secure root |
| `nk.inbox.reference/update-retention` | `24h` / `7d` | UI 251、324 |
| `nk.outbox.sent-retention` | `7d` | PENDING/ERRORは無期限 |

### 5.3 Batch・backup

SSC068/PG186: 新規backup子directory用のprivate0700/create-new/保持FD能力を333§7.6へ定める。配布root・既存UID/GID/modeを変えず、生成主体はbackup専用UID/GID、root callerは独立metadataと停止/排他を確認する。実環境権限未検証を一般native temporary PTの成功へ含めない。

SSC059/PG166: 実artifact read-only照合は341 §6.5。root親が作るconfig.tar/credentials.tar.age/MANIFEST.jsonはroot:root0600、DB worker dumpは専用backup UID/GID0600、backup root/子は同専用UID/GID0700。親が信頼manifest bindingとroot admission・NAS能力を別確認し、保持inodeの全4file/metadata/hash/byte・再bindingを照合する。検証は生成/暗号化/fsync/DB成功を代替しない。実装/16PTは017038/039へ先行する。

SSC058/PG165: backupのMANIFEST.json固定値/byte schemaは341 §6.4を正とする。version8項目・recipient fingerprint・固定3fileとrun/両完全backup step handleを保存する。内容生成終了時刻とatomic確定後のstep終了を混同しない。codec成功だけで実file/hash/秘密暗号/DB binding/7世代を検証済みにせず、実体gateと世代管理は別必須。実装/独立16PTは017033～036へ追跡する。

| Key | Initial | Validation |
|---|---|---|
| `nk.batch.zone/schedule` | `Asia/Tokyo` / `05:00` | systemd timerと照合 |
| `nk.batch.backup-root` | `/srv/schubert-nk/backup` | absolute real dir、other root非重複 |
| `nk.batch.backup-generations` | `7` | 固定、短縮禁止 |
| `nk.batch.transfer-cleanup` | enabled | 取得ACKなし、次回朝 |
| `nk.batch.expiry-retention` | `7d` | DLQに適用しない |
| `nk.batch.log-retention` | `90d` | Security hold除外 |
| `nk.batch.run-retention` | `400d` | FAILED調査中除外 |
| `nk.batch.chunk-size` | notification/question 1000、log 10000 | 1..defined max |

## 6. Credential catalog・rotation

| Credential ID | Consumer | 形式・rotation |
|---|---|---|
| `db-api`,`db-web`,`db-batch`,`db-migration` | 対応process | PostgreSQL SCRAM password、service別。`db-batch`はdumpへ使用しない |
| `db-backup` | backup unit | QA-043/UIC-003承認済みの`schubert_backup`専用SCRAM password。`schubert-backup` OS userだけへ配布 |
| `db-inbox-inspector` | 非公開Inbox保守検査processのみ | QA-046/UIC-006/SSC-049の`schubert_inbox_inspector`専用SCRAM password。batch/Web/backup/通常APIへ配布しない |
| `mq-web`,`mq-api`,`mq-maintenance`,`mq-ops` | 対応process | Artemis credential、Address権限別 |
| `web-session-aes-current/previous` | Web | AES-256-GCM、key version付き |
| `web-revoke-aes-current/previous` | Web | Pending context revoke暗号、session keyと分離 |
| `api-context-aes-current/previous` | API、非公開Inbox保守検査process（SSC-049/QA-046） | `auth_sessions.context_ciphertext`暗号、key version付き。batch/Web/backupへ配布不可 |
| `api-inbox-response-aes-current/previous` | API、非公開Inbox保守検査process（SSC-049/QA-046） | Inbox replay response暗号、context keyと分離。検査はreadのみ、batch/Web/backupへ配布不可 |
| `operation-hmac-current/previous` | API | 256 bit以上、HMAC-SHA-256 |
| `web-log-aes-current/previous` | Webのみ | Technical outbox保存・復号。API ingestへ配布しない（SSC-007） |
| `backup-age-recipient` | backup unit | 公開keyのみserver保持、private keyはoffline |
| Caddy TLS key/state | Caddy | Caddy専用OS権限、fingerprint管理 |

Symmetric keyは最低32 byte、自動生成passwordは最低32 byte相当のCSPRNG出力とし、ID/versionと有効日だけmanifestに記録。Rotationは「previousを配備→current切替→
旧ciphertext/HMAC保持期間の読取確認→previous除去」の順。Unknown key versionはdeny closed、運用介入とする。

SSC-049/PG-D-122: 検査processの鍵は起動時に読取り後、不変のcurrent/previous snapshotとしてprocess終了まで保持する。鍵rotationは同じ保守OS lockの下で検査process停止を確認して行い、検査から削除までの途中close/rotationを禁止する。HMAC秘密値は検査へ渡さず、保持中HMACの読取り可能version名だけを非秘密設定として固定する。

### 6.1 Inbox検査のAES credential byte形式（SSC-049、PG-D-131）

検査へ配布するapi-context-aes/current・previousおよびapi-inbox-response-aes/current・previousの各fileは、ASCIIで `NKKEY1 LF version LF base64 LF` とする（斜線表記は本節の説明上の略称、正式IDは上表のハイフン名）。versionは既存codecと同じ1～16 byteの `[A-Za-z0-9][A-Za-z0-9._-]{0,15}`、keyはAES-256の32 byteを標準Base64・必須padding・canonical表現の44 byteへ符号化する。全54～69 byte、LFのみ、BOM/CRLF/空白/余分field/末尾data/未padding/非canonical末尾bitを禁止する。値そのものはGit/argv/env/ログ/証跡へ記録しない。今回の形式確定は内部credential搬送であり、保存済AES envelopeや電文を変更しない。

InspectorAesCredential.consume(byte[])は入力arrayの排他的所有を引き受け、正常/不正いずれもfinallyで消去する。versionだけを非秘密Stringとして保持し、base64/keyをString化しない。decodeしたkeyは長さ/canonical検証後にprivate所有とし、失敗時のtemporaryも消去する。copyKeyは独立arrayを返しcallerが使用後消去、closeはprivate lockの下で所有keyを消去して冪等終了、close後copyKeyは禁止。version/状態だけの診断で値を出さない。Java/JCA内部の不可制御copyまで物理消去を保証したとは述べず、所有bufferの明示消去・heapdump非生成・process寿命の管理を組み合わせる。

元file0600とsystemd配布後のruntime権限は別物である。systemd 259の実装はroot所有fileへ対象UIDのACLを追加する経路と、対応filesystemによって所有者を移す経路を持つ。単に「runtime file owner=serviceかつmode0400だけ」とする実装は採用しない。後続readerは保持inode、regular/symlink/hardlink/サイズ、readonly/owner/実効ACLの専用主体限定、読取/close失敗を検証してからmaterialを渡す。ACL検証未実装を緩いmode判定で代用せず、main/専用unit/親processの鍵配布を完了にしない。[systemd 259 credential実装](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/exec-credential.c)、[公式credential契約](https://raw.githubusercontent.com/systemd/systemd/v259/man/systemd.exec.xml)を参照（2026-09-09確認）。

### 6.2 Runtime credential権限の限定（SSC-049、PG-D-132）

非公開検査processは非rootの専用UID（1～4294967294）で動作する。保持inodeの属性とaccess ACLは以下の2形式だけを許可する。ACL検査単体はfileを読まない。後続IO adapterが同じ保持inodeから取得した型付き属性、実際のfilesystem readonly flag、`system.posix_acl_access`を渡し、取得失敗を空ACLへ変換しない。

| 形式 | Directory | AES file | Access ACL |
|---|---|---|---|
| system manager root所有＋専用UID ACL | type directory、mode0550、nlink>=1 | type regular、mode0440、nlink=1、size54～69 | owner root、USER_OBJ=r-x/r--、USER=専用UID:r-x/r--、GROUP_OBJ=---、MASK=r-x/r--、OTHER=---の5 entryのみ |
| 専用UID所有fallback | type directory、mode0500、nlink>=1 | type regular、mode0400、nlink=1、size54～69 | access ACLなし、owner=専用UID、実filesystem readonly必須 |

typeを含むunix modeの完全一致を使い、symlink/FIFO/device/socket、setuid/setgid/sticky、write bit、fileのexecute、余分なhardlinkを拒否する。root+ACL形式は専用UIDがchmodできず、plain-directory fallbackでも安全性を保てる。専用UID所有形式はchmodでwriteを取り戻せないようreadonly filesystemを必須とする。root所有なのにACLなし、他owner/他UID/他group/余分entry（権限0でも）、mask/other許可、byte順/ACL version/entry順/不足/末尾dataの相違を拒否する。規定形式を満たさない現物のchmod/chown/ACL補正はreaderの責務にせず、設定不正で停止する。

Linux UAPI形式はlittle-endian version2の4byte headerと8byte entry（tag u16、perm u16、id u32）。5entry=44byte、名前なしentryのidはFFFFFFFF、tag順は1/2/4/16/32。modeのgroup bitはACL maskであり、GROUP_OBJ権限と混同しない。上記は汎用ACL parserではなくsystemd配布形の厳格allowlist。根拠: [Linux ACL xattr UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.16/include/uapi/linux/posix_acl_xattr.h)、[tag/permission UAPI](https://raw.githubusercontent.com/torvalds/linux/v6.16/include/uapi/linux/posix_acl.h)、[systemd v259 file/directory権限設定](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/exec-credential.c)。環境259.5実測と保持inode/native読取/close/親gateは別PTで確認するまで未完了とする。

### 6.3 保持inodeからのaccess metadata読取（SSC-049、PG-D-133）

storageのInodeSecurityCalls/LinuxInodeSecurityはOwnedTransferDirectory callback内のcanonical `/proc/self/fd/<0..2147483647>`だけを受け、libc getxattrの固定名system.posix_acl_access、statvfsのST_RDONLY、geteuidを読む。API file adapterは同callback内でunix属性・ACL・filesystem flagを取得し、型/owner/permissionを確認してから内容を開く。FD/pathをcallback外へ保持・返却・記録しない。final symlink自体を保持するO_PATHは、readerのunix type検査で先に拒否する。

ACLはcaller指定上限1～65536byteの単回読取（inspectorは44）。size照会→再allocateのraceを作らず、ERANGE/上限超過/0byte成功/不正returnは拒否する。ENODATA/EOPNOTSUPPだけは「ACL値が取得されない」空結果であり、ACL不存在や権限許可の単独証明ではない（ENODATAはアクセス不可も含み得る）。その他EACCES/EPERM/EIO/ENOENT等は固定StorageIoExceptionで停止する。空結果は§6.2のroot+ACL形式では必ず拒否され、専用UID所有・mode0400/0500・filesystem ROの全条件を別途満たす場合だけ内容読取へ進める。POSIX ACLのgroup class mask0/other0は他主体の実効accessを許可しない。Read失敗を成功へ変換しない。Linux systemd local credential filesystemを対象とし、NFS等の異種ACLを一般に認可する機能ではない。

Java25公開FFMでLinux/glibcのLP64 x86_64/amd64/aarch64 ABIに限定し、必要symbol/OS/archが不明なら起動不可。statvfsは当環境libc6-dev2.43-2ubuntu2.4の/usr/include/x86_64-linux-gnu/bits/statvfs.hと照合した112byte/align8、f_flag offset72、ST_RDONLY=1。実PTは当機x86_64、他archの実動作は後続環境確認事項であり未実測を合格へ加えない。固定binding部分だけ既存PG-D-055同様restricted FFM warningを理由付き限定抑止し、null/他warning/coverageは除外しない。Test用call portはnative戻り値・errnoを決定的に注入し、実LinuxのACL/保持inode/UID/100並行と合わせて検証する。

根拠: [Linux getxattr契約](https://man7.org/linux/man-pages/man2/getxattr.2.html)、[statvfs契約](https://man7.org/linux/man-pages/man3/statvfs.3.html)、[glibc statvfs layout更新](https://sourceware.org/pipermail/glibc-cvs/2023q3/082782.html)、上記の導入済みheader。実credential・DB・service設定は変更せず、公開metadataだけの一時file/setfacl2.3.2をPT fixtureとする。

### 6.4 Private AES file reader（SSC-049、PG-D-134）

API file adapter InspectorCredentialLoaderはborrowed OwnedTransferDirectory、InodeSecurityCalls、専用EUID policyを使い、AesCredentialFileの4固定名（api-context-aes-current、api-context-aes-previous、api-inbox-response-aes-current、api-inbox-response-aes-previous）だけを読む。Caller入力から任意pathを組み立てない。currentは必須。previousはentry openがENOENTでcallbackに一度も入っていない場合だけOptional.emptyを許可し、permission・途中消失・metadata/ACL/closeエラーをprevious不在に変換しない。previousの有無を鍵内容やdecode結果から推定しない。

loadごとに保持directoryを検証し、entry O_PATHのunix typeがregularであることを最初に確認してからACL/readonly取得へ進む。symlink/FIFO/device/socketの内容openやACL経由のtarget追従を行わない。UID/GID/mode/nlink/size/dev/ino/mtime/ctimeを型確認し、§6.2を適用。FileChannel READだけを開き、前後のchannel size一致、最大70byte buffer（正常上限69＋過長検出1）、EOFと実読取長を確認する。0byte readを無期限retryせず不正停止。読取後channel closeを完了させ、同保持entryの属性/ACL/readonlyと開始snapshot一致を再検証、entry close後に同保持directoryも再検証する。検査対象root/fileのchmod/chown/repair/書込み/再openによる差替えはしない。

全IO・entry close・directory再検証成功後にのみ、有効長をcopyして§6.1.consumeへ渡す。操作中70byte bufferは全終了のfinallyで消去し、parse側の所有copyもconsumeが消去する。失敗は固定InspectorCredentialException、原因/suppressed/path/鍵値を外へ出さない。入力nullはconstructor/境界契約で拒否し、NPEをcatchして正常扱いしない。Readerはrootを閉じず、mainが鍵codec/resourceと共に所有・closeし、root close失敗をprocess成功へ算入しない。4鍵の読取後のcurrent/previous version整合とcodec作成、親backup/OS lock/専用unitは後段の別責務。

PT035は実public temporary file/FileChannel/保持inodeと、明示したOS metadata/call fault portを組み合わせる。権限policyとnative取得は031/033で独立検証済み範囲へ追跡する。root-manager由来の実credential正系を当機で起動したとは主張しない。当機sudoは対話認証が必要であり、daemon/認証設定は変更しない。正式unitの実権限配布確認は権限のある後続Linux環境へ引継ぎ、PG/PTの権限緩和で代用しない。

### 6.5 検査内部の鍵snapshot・run接続（SSC-049、PG-D-135）

InspectorProcessは公開HTTP/JMS入口やOS process起動ではなく、private oneshot内で一度だけ呼ぶ同期serviceとする。constructorはborrowed InspectorCredentialLoader、専用SqlConnectionProvider、読取可能fingerprint version名の不変集合を受ける。root/DB datasource/OS lockはcaller所有。productionはSystem.nanoTime、PTはpackage内の鍵source/clock portを使う。Null/空集合/未知version名を起動契約で拒否する。

execute(run)はnull拒否後にprivate AtomicBooleanで1回だけ実行権を取る。競合/2回目は固定例外で拒否し、鍵再読取・別runへの流用をしない。開始時割込はflagを保ち、鍵/DB未accessのINTERRUPTEDを返す。4固定credentialを順に読み、current必須/previous任意を§6.4と同じ契約で扱う。各materialは直ちに操作内の所有集合へ登録してからcopyKeyし、途中load/copy失敗も既取得material/copyをすべて消去する。閉じたmaterialは設定失敗とし、NPEをcatchしない。

同purposeのcurrent/previous version重複はcodec生成前に拒否。ContextとResponseの全存在世代の鍵byteを定数時間比較し、purpose間の同一鍵は拒否する（version文字列のpurpose間一致は可）。既存AuthContextCodec/ResponseSnapshotCodecの保存形式・previous読取契約をそのまま使用する。応答・認証参照inspector、非認証22route inspector、InboxCleanup、InspectionRunExecutorへ接続し、鍵生成/取得、codec構築を全てDB処理より前に完了させる。fingerprintのHMAC実体は取得しない。

各codecは実行thread内に閉じて公開せず、全run/chunk終了後にのみcloseする。正常/保護WARNING/期限/割込/DB失敗/想定外例外のすべてでcodec→所有copy→materialを回収し、鍵の途中close/rotationを許さない。Mandatory JCA algorithm取得失敗も成功へ変換せずcallerへ通知。診断は既存InspectionExecutionの許可済status/countのみ。Java/JCA内部copyの物理消去保証は§6.1と同じ限定。

返却0/10/50は内部run結果であり、mainのroot/datasource close・DB credential読取・親backup実体/OS lock・systemd unitの成功を保証しない。構成不正はmainが70へ分類し、想定外runtime故障は正常化しない。SSC-049/PG-D-139～141によりQuestion/通知7routeを含む全31responseの保守検査を接続した。非認証検査の元22という上段はPG-D-135の初期範囲であり、現行の固定routeはSS324 §12.8～12.9/331 §3.10～3.11を正とする。通常Question業務writer/replayや全PG/PT・実NK CHRの完了ではない。

### 6.6 検査専用DB credential・接続（SSC-049、PG-D-142）

`db-inbox-inspector`は352 §11.1のUTF-8 passwordとし、独自の暗号envelopeやversion prefixを加えない。fileは1～65536byte、BOMなし・不正UTF-8なし。終端の改行は1個のLFまたはCRLFだけ取り除く（改行なしも可）。残るpasswordは空/NUL/CR/LFを拒否し、それ以外のUnicode・前後spaceはtrim/正規化せず保持する。自動発行時のCSPRNG 32byte以上というcatalog要件はprovisioning側で維持し、parserが文字列からentropyを推定しない。

InspectorDbCredential.consumeは入力byteの排他的所有を引受け、成功/失敗いずれも入力とdecoder一時bufferを消去する。passwordはprivate char[]、copyPasswordは独立copyでcallerが消去、closeはprivate lockで冪等消去、close後copyは拒否。診断は固定redacted値のみ。JDBCが要求するStringやdriver/JDK内部copyを物理消去できるとは主張せず、長寿命field/診断への格納禁止・Propertiesの即時clear・process寿命/heapdump無効化で限定する。

InspectorCredentialLoader.loadDatabasePasswordは固定1file名だけを必須読取する。AES loaderの保持inode/type/owner/ACL/readonly/前後metadata一致・channel/entry/directory close成功条件を共用し、最大65537byte bufferで過長を検知する。§6.2のfile permissionと単一link条件は不変、password用サイズだけ1～65536、AESは54～69のまま。任意filename引数やACL緩和を追加しない。

InspectorDatabaseConnectionsはloaderから受けたmaterialの独立copyだけを所有し、専用role `schubert_inbox_inspector`へfresh JDBC接続を返す（pool/共有connectionなし）。URLはliteral IPv4 loopback `jdbc:postgresql://127.0.0.1:<1..65535>/<lowercase database identifier>`だけ、query/fragment/userinfo/複数host/escapeを拒否。本番値は§5.2の5432/schubert_nk、PTは隔離port/DBを使う。固定接続propertyはuser/password/connectTimeout=3/ApplicationName=schubert-nk-inbox-inspector、loopback SCRAMを使い任意propertyを受けない。接続時だけpassword Stringを作り、Propertiesをfinally clear、元copyをclose時に消去する。

返却前にautoCommit=true/readOnly=false、current_user/session_userが両方専用role、current_databaseが設定DBと一致、回復中でないことを固定SELECTで検証する。違反/SQL故障/検証用資源close故障は接続も閉じて固定SQLExceptionだけを返す（原因/suppressed/credential/URL/SQL値を公開しない）。正常返却connectionはcaller所有、provider closeと競合するopenはprivate lockで直列化、既返却connectionを勝手に閉じない。DB role権限と保持・backupは既存SQL/owned cleanupが別途再検証する。専用process main/OS lock/実backup検査/unit起動の成功をこの接続部品だけで保証しない。

### 6.7 専用検査の操作内resource寿命（SSC-049、PG-D-143）

InspectorSettingsは非秘密のcredential directory path、§6.6 canonical JDBC URL、読取可能fingerprint version集合の不変snapshotを持つ。Pathは絶対・正規化済み・rootそのもの以外、URLは既存専用providerと同じ検証、versionは§6.5の非空集合/1～16byte形式。null/空/未知値はIO前に拒否し、toStringは設定実値を表示しない。既存InspectorProcess/providerの同じ検証をこの設定契約へ共有し、判定を複製しない。ここはenv/file parserではなく、後続launcherが渡す値の型境界である。

api.fileのInspectorApplicationはfile adapterとして低位DirectoryCalls/InodeSecurityCallsだけを使用する。execute(run)ごとに(1)全path segment NOFOLLOWでrootを開く、(2)既存readerでdb-inbox-inspector materialを所有、(3)固定role providerへ独立copy、(4)同rootのreaderとproviderからInspectorProcessを生成・同期実行、(5)provider/password/rootを逆順close、の順とする。鍵4個/copy/codecは既存InspectorProcessが操作内で所有・消去する。runはIO前にnon-null確認。各executeは独立寿命で、同run再開は永続状態を正とする。

成功/保護あり結果はroot closeを含む全終了後だけ返す。BUG-134/YKT-105: 開始時割込はrun null確認後・root/password IO前に判定し、flagを保持してINTERRUPTED/最後の確認状態なしを返す。読取途中の割込は既存IO失敗として全資源を閉じ、成功にしない。root open/close、credential load、構成不正/暗号primitive故障は例外で終了し、途中結果を返さない。通常DB障害/割込/時間超過は既存InspectionExecutionの非成功を保持する。ここでroot権限を緩和したり、DB credentialを他processへ渡したりしない。ログ/HTTP/JMS/別processを生成しない。PTは実保持inode/file/JDBC/永続SQLと明示synthetic OS属性・fault portを組合せる。実systemd credential正系、Java main/unit、親flock/backup実体/朝batch全順序は別gateであり本接続だけを完了証明にしない。

### 6.8 非公開launcherの入力・receipt・credential profile（SSC-049、PG-D-144）

SSC-049/PG-D-151（先行85eef317）: root静的fileのrender結果は`NK_INSPECTOR_DB_URL=<URL>`＋LF、`NK_INSPECTOR_FINGERPRINT_VERSIONS=<comma列>`＋LFの順に固定する。2行以外・空行・CRLF・引用/escape/コメント/space・未知/重複/alias key・run/credential設定混入は不正。URLは§6.6と同じ`jdbc:postgresql://127.0.0.1:<port>/<database>`、portは先頭0なし1～65535、DB名は`[a-z_][a-z0-9_]{0,62}`、query/userinfo/remote host不可。versionは1～65536 ASCII文字、comma区切りの各要素`[A-Za-z0-9][A-Za-z0-9._-]{0,15}`で空/重複不可。file全体は1～65848byte（key/各値の既定上限/LFの合計上界）。全byteを照合し、UTF-8非ASCIIも拒否する。親のInspectorStaticEnvironment.requireValidは固定診断だけを返し、nullはprogramming契約違反。任意shell/systemd構文を評価しない。親の保持inode/bounded IO/属性検査で得たsnapshotに使用し、子launcherの型検査・DB接続時の再検証を省略しない。雛形はDB名等をrenderし本検査に合格してから配置する。秘密実体・環境全体は保持/出力しない。

公開HTTP/JMSではないInspectorLauncher.mainをprivate unitの必須wrapperから呼ぶ。argvによる設定上書きは禁止し引数0個だけ。設定は以下の非秘密環境値から一度だけ型化し、現在日時や別runへ補完しない。password/AES/HMAC実値をenvへ渡さない。

| Key | 受理契約 |
|---|---|
| `CREDENTIALS_DIRECTORY` | systemdが設定するprivate root、1～4096文字、InspectorSettingsの絶対正規化path（`/`不可）。特定の未保証systemd内部path prefixを推測しない。保持inode/専用UID/ACL/ROは既存readerが毎回検証 |
| `NK_INSPECTOR_DB_URL` | 1～256文字、§6.6のcanonical loopback専用DB URL |
| `NK_INSPECTOR_RUN_ID` | canonical小文字36文字UUID、parse後toStringが原値と一致 |
| `NK_INSPECTOR_CUTOFF` | 1～32文字、UTC Instant canonical文字列と完全一致、InspectionRunの年/精度契約（microsecond以下）を維持。offset別表現/補完/丸め禁止 |
| `NK_INSPECTOR_FINGERPRINT_VERSIONS` | 1～65536文字のcomma区切り、空要素/重複不可、各versionは§6.5の1～16 ASCII。HMAC秘密値は含めない |

上記必須値の欠落/null/空/過長/NUL/CR/LF、`NK_INSPECTOR` namespaceの未知key・大小文字alias、CREDENTIALS_DIRECTORYの大小文字aliasをCONFIG70とする。無関係なOS環境値は保持・出力せず無視する。Map化前に消えるEnvironmentFile内重複やsource優先順は配備側validatorの責務であり、このlauncherのMap検査で検出済みとしない。外側null引数/portはprogramming contract違反であり、NPEを正常へ変換しない。

root所有の`/etc/schubert-nk/inbox-inspector.env`にDB URL/version名だけを置く。run ID/cutoffだけはroot所有maintenance controllerがOS flock保持下で`/run/schubert-nk/maintenance/inbox-inspector.env`（parent root:root0700、file0600）へ原子的にpublishし、systemd managerがEnvironmentFileとして読む。batch accountにこのfileの任意編集、任意環境/汎用systemd-run/sudo権限を付与しない。親の停止/lock/実backup・設定fileの検証/原子publishとrun bindingの実装は別必須gate。ここで未実装の親gateを代行済みとしない。

SSC-049/PG-D-149（先行17b06c0c）: 親が生成するrun専用fileは`NK_INSPECTOR_RUN_ID=<UUID.toString()>`＋LF、`NK_INSPECTOR_CUTOFF=<Instant.toString()>`＋LFの2行だけをASCIIで持つ。UUID/cutoffは既に確定したBatchRunと同一とし、現在時刻取得・丸め・再採番・推測補完をしない。InspectorRunEnvironment.encodeはcaller所有の新規byte配列を返し、requireMatchesは期待BatchRunから得るcanonical全byteとの完全一致だけを受理する。別run/別時刻、重複/追加key、引用符/space/CRLF/extra LF/NUL/高bit/欠落は拒否、nullは明示契約違反。非秘密identityだけでpassword/鍵/pathを含めず、固定診断に実値を出さない。file read前の容量・root所有/ACL/NOFOLLOW・実lock保持・atomic publish/再読/同inode・子の未稼働確認はpublisher/caller側の別必須条件で、このbyte codecでは認定しない。SSC-055の永続anchorを生成fileやメモリBatchRunで代替しない。

設定不正・credential読取/形式不正・暗号primitive構成不正はreceipt70、StorageIoExceptionは50、通常の実行結果はInspectionExecutionの0/10/50を維持する。予期外runtime故障は成功receiptを出さずJVM異常終了とする。mainの未捕捉例外handlerは固定`inspector failed`だけstderrへ出し、Throwable/値/stackを出さない。出力stream障害も非成功。全resource close後の結果からだけASCII `NKINSPECTOR1 <code> LF`をstdoutへ一度出す。JVM exit0はreceipt発行成功であって業務成功ではない。

必須POSIX sh wrapperは固定Java/artifact/classpathを実行し、JVM非zeroまたは不明/欠落/余分text/extra LF/不明codeを50へ分類する。exact receiptの0/10/50/70だけ対応exitで返す。引数/未render placeholderは70。SSC-053/BUG-137: shell変数はNULを保持できないためraw receiptを直接代入しない。Java stdoutへ終了code0ならASCII dot、非zeroならASCII !を付加し、固定`/usr/bin/od -An -v -tx1 -w64`へpipeする。全byteをhex化してからcommand substitutionへ入れ、正規4receipt＋dotの固定hex列だけ受理する。NUL・高bit・末尾LF数・不明byteを正規化しない。odの非zeroも50。末尾markerとhex化によりJVM異常/byte欠落を成功へ変えない。PTでは固定od呼出しだけ一時fixtureへ差替えたfault注入を明記し、本番の任意tool差替え権限を設けない。任意command/evalやsecret表示は禁止。これがOSへ公開する唯一の実行entryであり、Java main単独のexit0をparentが成功判定に使わない。親は同run/cutoffの永続progressを別途読んでattempt差分/最終件数を記録する。

unitのLoadCredentialは常にDB/current2の絶対source pathを指定する。previous2はroot管理rotation profileに応じて固定path行を追加する選択drop-in（なし/contextだけ/responseだけ/両方の4構成）。宣言しないpreviousだけreaderで不存在可。配布宣言したsourceの欠落/読取不能はunit起動失敗とし、空defaultへ置換しない。source省略によるmanager/credstore検索やSetCredentialの空値fallbackは使わない。rotation/profile切替は同じ保守OS lock下でprocess停止→credential/profile整合→daemon reload→次回起動とする。systemd259.5の導入済みsystemd.exec(5) LoadCredential/SetCredential節で確認（2026-09-09）。実root配布はLinux serverのITで確認し、PTの合成metadataで代用済みとはしない。

### 6.9 親の保持inode環境file reader（SSC-049/PG-D-152）

先行58f7e8b7。InspectorEnvironmentReaderは親file adapterが既に固定pathからNOFOLLOWで保持したdirectoryを借用し、既存名`inbox-inspector.env`だけを保持して読む。読取中は親がOS flockを保持しroot設定変更/子起動を禁止する。root/ancestorの固定namespace再検証は親が行う。readerが借用rootのpath選択やclose/作成/chmodをしない。

- euid0必須。static directoryはroot:schubert0750、fileはroot:schubert0640。期待schubert GIDは信頼できるaccount設定から解決した1～4294967295をconstructorで受け、対象fileのGIDから自己生成しない。runtime directoryはroot:root0700、fileはroot:root0600。
- directoryは通常directory/nlink2以上、fileは通常file/nlink1、同device。static fileは1～65848byte、run fileは1～110byte（§6.8のkey/UUID/32文字cutoff/LFの上界）。各metadataはmode/uid/gid/nlink/size/dev/ino/mtime/ctimeの型付き必須値。型判定前にcontent open・path-following xattr/FS照会をしない。
- access ACLなし。staticはext2/ext3/ext4/xfs/btrfs/tmpfsのlocal FS（RO可）、runtimeはRW tmpfsのみ。未知FS/属性/欠落/別inode/過長/不明read結果は拒否。default ACLは既存inodeを読む権限を付与せず、このreadonly部品の検査対象外。新規作成時のACLはpublisher側で別検証する。
- 上限+1のbufferと保持inodeへのread-only channelを使う。開始/終了sizeとmetadataを照合し、EOFまで読んだ長さが元sizeと同じことを確認する。read0、不正count/position、短縮/伸長/close失敗は非成功。追加1byteは過長判定専用で受理しない。
- 同名をもう一度O_PATHで保持してdev/ino・mode/UID/GID/nlink/size/mtime/ctime/FSと元snapshotを完全照合する。directoryのidentity/属性も前後照合。entry/channel全close後にstatic内容検査または期待BatchRunへの全byte照合を行い、caller所有の新規配列を返す。型/IO異常は固定StorageIoException、byte設定不正は既存固定IllegalArgumentException、null caller依存は明示契約違反。診断にpath/内容/cause/suppressedを出さない。

本部品は既存fileの読取だけであり、atomic publisher/親起動・子終了/backup/永続run原本を完了にしない。合成root/GID/tmpfsの単体fixtureと実root配備のITを区別する。

### 6.10 private原子公開の低位能力（SSC-049/PG-D-153）

先行67148c13。SS333 §7.3のprivate0600 CREATE_NEW/保持inode・単一名RENAME_NOREPLACE・directory fsync・検証済みentry unlinkを再利用する。上位publisherはroot:root0700の固定runtime・OS lock・子非稼働・期待BatchRunを確認してから、新規UUID.partへcanonical2行だけを書き、file fsync/byte再照合後に固定inbox-inspector.envへ公開する。既存targetを通常renameで置換しない。同runの既存公開fileは再読取/再同期で判定し、別run/不正fileは勝手に置換しない。公開後の終了/再試行・known partialの扱い・親からの固定namespace結線は上位publisherの次の詳細化/PGPT対象であり、本低位能力だけでは認定しない。

### 6.11 親run環境publisher（SSC-049/PG-D-154、先行aa2baa3a）

InspectorEnvironmentPublisherは借用runtime rootでprepare(BatchRun)/retire(BatchRun)を行うfile adapter。親は固定namespace/OS flockの全区間保持、root設定変更禁止、子unitが終端であること、永続原本に一致するBatchRunを独立して保証する。部品の成功をこれらの証明に使わない。借用rootを閉じず、private monitorで同instance操作を直列化する。

- 全入口はnull拒否、割込flag保持/euid0、§6.9のroot:root0700・RW tmpfs・access ACLなし・型付きmetadataを検査。共通EnvironmentInodePolicyへreadonly readerの判定を抽出し、静的root/file仕様は変えない。新規空fileだけsize0を作成直後の検査に許可し、公開/読取は1～110を維持する。新規fileにもaccess ACL不在を必須とし、継承ACLを含む不明grantは拒否する。
- 最初の固定target openだけがENOENTで、callbackに一度も入らずclose等の失敗もない場合を不存在とする。存在時は同runのcanonical全byte/属性を保持inodeから検証し、file force(true)→close→directory sync→同inode/全byte再読→root identity再検証の全成功でprepareを冪等成功とする。別run/cutoff/不正byte/型/ACLは置換せず拒否。
- 不存在時はrun.idのUUID.partを0600 CREATE_NEWで作成し即時FD所有。既存partはCOLLISIONで保全し、期待run名というだけで削除/再利用しない。上位運用が過去不確定・所有・子停止・公開状態を確認して解決する。最初に空file属性/同device、書込みはcanonical110byte以下・進捗count/position一致・0/不正結果拒否、開始size0/終了size一致、force(true)、全channel closeとinode再検証を行う。
- partを§6.9相当のbounded readで同run全byte照合してから固定targetへRENAME_NOREPLACEしdirectory syncする。公開targetのdev/ino/所有/mode/link/size/mtime/FSが書込済みpartと同じことを確認（renameに伴うctime変化は許容）、再度全byte/属性とroot identityを検証して返す。directory内容変更によるsize/mtime/ctime変化は許容するがdev/ino/owner/mode/link/FSの変化は拒否。途中に他root管理者が名前を書換えないことは親lock運用の前提。
- retireは同runの公開fileを保持/全byte/属性検証し、同名identity再確認後だけunlink+directory syncする。最初から不存在だけ冪等成功でrootを再確認。途中消失/別run/壊れたfile/close/sync/割込は成功へ補完しない。子非停止中のretireは禁止で、親が実終端を確認してから呼ぶ。
- 成功/失敗にかかわらず任意既存fileのchmod/chown、上書きrename、部分fileの無条件削除、失敗したrename/unlinkの逆操作を行わない。作成/公開/削除後sync失敗は不確定として保全・非成功。caller-owned一時byteは消去、IO診断は固定StorageIoExceptionでcause/suppressed/値を出さず、未知runtimeを正常化しない。runを新規採番/現在日時へ補完しない。

PTは孤立実inode/FFM・合成root/tmpfs属性・明示IO faultで全分岐を検証。実root/manager/親全順序/永続anchorは別PGPT・後続IT条件を維持する。

### 6.12 固定namespace・account解決と環境寿命（SSC-049/PG-D-155、先行023017b2）

BUG-155/YKT-120（先行d0308b55）: 正常上限がpipe容量を超えても終了待ちとwriterが相互待機しないよう、所有virtual taskでstdoutを並行drainする。親は5秒のprocess待機/exit検証後に読取結果を受け、失敗時は生存lookup子へTERMを要求してから全task終端を待ち、全stdioを閉じた後に返す。task終了前に共有byteを消去しない。既定のtrusted OS/NSSと子孫がpipeを保持しない前提のもと、TERM/pipe終端を待つcleanup時間を5秒の成功保証に含めない。TERMを無視する異常OSの強制終端を約束せず、その状態で成功返却しない。実pipe4096で65536byteの正常vector、超過、途中失敗、停止/割込と消去を再発防止試験にする。

ConfigurationGroupResolverの公開入口は引数なしresolve()だけ。固定argv `/usr/bin/getent group schubert`をshellなしで実行し、NSSの名前照会からGIDを独立取得する。group列挙・gshadow・任意key/optionsを扱わない。環境はPATH=/usr/bin:/bin・LANG=C・LC_ALL=Cだけ、stderr破棄、親env/secretは継承しない。5秒待機・stdout最大65536byte（65537で過長検知）・exit0・全stdio closeの成功を必須とし、timeout/非zero/IO/不明read/close/割込は固定IOException、割込flagを維持する。失敗後の生存lookup子にだけTERMを要求しSIGKILLは使わない。任意子孫がpipeを保持しないtrusted OS tool/NSS設定を前提とし、実際の未停止子検知は非成功のまま運用へ引継ぐ。

stdoutは13～65536byte、prefix `schubert:`、colon合計3個、終端LF1個、内部NUL/制御ASCII/DEL/追加LF/CRを拒否する。password/member fieldは空でもよく、内容を解釈/表示/保存しない（非ASCII byteはこの2fieldに限りopaqueとして扱う）。GID fieldは先頭0なしASCII数字1～10桁、1～4294967295。別名/別group/欠落/多行/空GID/未知byteは拒否。全stdoutをString化せずGIDだけ積算し、byte配列を全終了時に消去する。nullはprogramming契約違反として正常化しない。lookup失敗を対象fileのGIDで補完しない。参照資料: host GLIBC2.43-2ubuntu2.4、Linux man-pages6.17 getent(1)、2026-09-12。

InspectorEnvironmentFilesの公開factoryは固定/etc・/runとnative portを生成する。execute(BatchRun, Operation<T>)は開始時null/interrupt/euid0を検査し、親のOS flock保持・root管理変更禁止・現在子終端・backup/永続run原本一致を必須preconditionとする。Operationは同じrunの子処理が終端となるまで復帰せず、親file/root/namespaceを操作しない。

1. 独立GIDを取得。全segment NOFOLLOWで/etc→schubert-nk、/run→schubert-nk→maintenanceを各独立FDとして保持する。/etc・/run・/run/schubert-nkはroot:root0755通常directory、configはroot:schubert0750、maintenanceはroot:root0700。access ACLなし・同階層device一致、/etc系は既定local FS（RO可）、/run系はRW tmpfs。rootそのもの/固定祖先の作成/chmodはしない。
2. static fileのSnapshotとcanonical byteを保持rootから取得し、同inode/全byte/属性を検証する。runtime publisher.prepare(run)を実行する。
3. 直前に固定pathを全て開き直して各保持rootのidentityと比較し、独立group照会も同GID、static fileも元Snapshot/byteと一致することを確認してからOperationを1回呼ぶ。runtime fileも期待runへ再読照合する。根拠をcallbackへ渡すpath/FD/secretとして公開しない。
4. Operationの正常nonnull終了後に同じnamespace/group/static/runtime確認を再実行し、同runretireを行う。全所有root close成功後だけ結果を返す。callbackが例外/nullで終了した場合はretireせずruntime fileを保全し、親が子終端/復旧を判断する。途中IO/close失敗で成功を補完しない。
5. 各directory比較は内容変化で変わるsize/mtime/ctimeを除いた型/owner/group/link/dev/ino/FS/ROを一致させる。static fileは変更を許可せずctimeを含む全snapshot＋byte一致。同階層を同deviceとし/etcと/runのdevice違いは正常。最後の割込も非成功、IO診断は固定cause/suppressedなし、未知runtimeは回収後にescapeする。

固定pathに対するportability警告はBUG142/YKT112と同じ理由で公開factoryのexact diagnosticだけreview可能（owner NK-OPS-001、PG gate/OS/path変更時再審査）。coverage/null/securityの除外ではない。実root/systemd/OS lock連続性は本PTの合成属性だけで認定せず、子制御の実装と後続ITを維持する。

### 6.13 永続run原本・activation・completion（SSC-055/PG-D-156、先行b6b5f0f6）

DB停止前/reboot後の原本は`/var/lib/schubert-nk/maintenance/runs/<run UUID>.run`。runのUUID/cutoffを一度だけ固定し、batch_runs.started_at/現在時刻/既存progressで補完しない。DBはstep履歴であり原本の第二コピーを後付けしない。既存runで原本がない場合はresumeを拒否し、履歴とfileを保持する。runなしの新規開始にだけ親がUUID/時刻を採り、公開後に生成し直さない。

再開単位をrunと区別するためactivation UUIDを持つ。`attempts/<activation UUID>.begin`はrun/activationを束縛し、固定`active`はそのbeginと同じbyteを持つ。`attempts/<activation UUID>.done`はそのactivationの親morning完了であり、別activation/別runへ流用しない。既存UUIDの上書き再利用は禁止。completionはSUCCESS(0)/WARNING(10)だけ。個別backup失敗→削除skip→正常起動の許容WARNING経路を維持し、個別FAILED調査中を完了recordで解除しない。

全rootはprovisioningで作成済み、private root/runs/attemptsはroot:root0700、recordはregular0600/nlink1・root:root・access ACLなし。共有祖先root0755を勝手に0700へ変更しない。local永続RW filesystemで、tmpfs/remote/readonly/unknown・symlink/不明属性を拒否する。保持directory/inodeでのmetadata/名前の再取得identityを操作前後に照合する。全scopeを親OS flockで保持し、保守中のroot管理者によるnamespace変更を禁止する。原本の有効なbyteだけを読めたことでは配布・所有・排他を証明しない。

状態遷移とcrash条件:

1. 新規run原本をCREATE_NEW0600のpartへ書き、file force→no-replace公開→directory sync→保持readbackを確定する。続いてbeginを同じ手順で確定し、最後にactiveを確定する。active確定前に停止/update/reboot等の副作用へ進まない。
2. Reboot後はactive→begin→原本の全値一致を確認して同cutoffを復元する。active/原本不明・複数未完了begin・異なるrun・不明partは推測補完/無条件消去せず停止。active公開前の単独未完了beginを見つけた場合の再接続は、明示resumeが同runで全identityを再確認した場合だけ。自動的に別runへ取り替えない。
3. 明示resumeはactiveが同runなら同activationを継続する。既doneがあれば、親は既完了activationの回復として読み、前回の副作用を再実行したと数えない。activeがなく、そのrunの全activationが完了している場合にだけ新activationを作る。前回completionを今回成功に使わず、必要stepのskip/新attempt/backup例外をSS341に従って実施する。
4. 親が許容morning終端・実子終端・step記録を確認後、doneをdurable公開してから同じactiveを限定unlink/syncする。終了timeはrun cutoff以上、microsecond精度・UTC年0001～9999。process exitだけを完了にせず、失敗/interrupt/commit不明はactive/原本を保全する。同じdoneの再確認は全値完全一致だけを認め、別時刻/別statusへ上書きしない。
5. `runs`の原本退役は最新completionから400日超、全activation完了、active/未公開part/不明fileなし、batch_runs/Inbox progress/log progressの参照0をOS/DB lock下で再確認した場合だけ。先にrun限定のretirement markerをdurable確定し、既知のbegin/done/原本だけを限定削除、最後にmarkerを消す。中断時はmarkerを保持して新resumeを拒否し、同じ限定対象の参照0を再確認して冪等再開する。未完了・FAILED調査中・DB不通・不明runは保全。marker具体byte/DB照会/GC callerは後続PG/PTで先行仕様化し、本項目全体の未完了条件として残す。

PG-D-156のcanonical record（各行末LF、ASCII、以下の順序、空白/quote/CRLF/BOM/追加行/aliasなし）:

| 種別 | 行1 | 続く行 | byte長 |
|---|---|---|---:|
| anchor | `NKRUN1` | run UUID、cutoff | 72 |
| begin/active | `NKACT1` | run UUID、cutoff、activation UUID | 109 |
| done | `NKDONE1` | run UUID、cutoff、activation UUID、ended_at、`0`または`10` | 140/141 |

UUIDはlowercase36文字、時刻は`uuuu-MM-dd'T'HH:mm:ss.SSSSSS'Z'`の27文字、BatchRunの年0001～9999/µs範囲を維持する。business_dateは既存SQLと同じAsia/Tokyo変換から導出しrecordへ別値として重複保存しない。canonicalでない同値表記・うるう秒の自動正規化を受理しない。parserは構造的に有効な別runも値として復元するが、file store/親が期待する原本と全値一致を別途検証し、parser単体を所有/認証/同run保証にしない。

MaintenanceRecordsは3種encode/decode、MaintenanceActivationはBatchRun/activation UUID、MaintenanceCompletionはactivation/ended_at/0・10の型付きOutcomeを保持する。nullは境界で拒否し、byte入力の不正はraw cause/suppressedを含まない固定IOException、constructor不変条件違反は固定IllegalArgumentException。配列を保持/共有せず、recordのtoStringはidentityをredactする。記録実体はGitへ保存せず独立synthetic goldenだけを試験に使用する。永続file store・親unit/reboot・GC/DB照会の実装はcodecだけでは完了しない。

### 6.14 借用rootの永続record IO（SSC-055/PG-D-157、先行19e22eb4）

BUG159/YKT124（先行12446fed）: removeで最初からentryが不存在でも、親directoryのsync成功を必須とする。前回unlink成功→sync失敗の可視不存在を耐rebootの確定と混同しない。再同期に失敗すれば不存在でも非成功。純readのOptional.emptyは存在観測だけであり、永続化を約束しない。

DurableRecordFilesはpackage内のfile能力であり、既に固定namespaceを認可したOwnedTransferDirectoryを借用する。任意pathのopen/provisioningやroot closeをしない。各操作をinstance内で直列化するが、callerは別instance/processも排除するOS flockとroot管理者の変更禁止を全区間で維持する。private root0700、regular0600/nlink1、root:root・ACLなし、同device、既定local filesystem（ext2/ext3/ext4/xfs/btrfs）のRWだけを受理し、tmpfs/remote/unknown/readonlyを拒否する。既存static/runtime環境fileの契約は変えない。

read(name)の名前は固定activeまたはcanonical lowercase UUID＋.run/.begin/.doneだけ。.runは内容のrun UUID、.begin/.doneはactivation UUIDと一致必須。activeはactivation構造だけを保証し、begin/anchorとのgraphはcallerの別責務。nullはprogramming契約、名前不正は固定IllegalArgumentException、byte/IO不正は原因/suppressedなしのStorageIoException。不存在は最初のentry openがcallback未開始でMISSINGのときだけOptional.empty。途中消失/close失敗は不存在扱いしない。保持root/full file snapshot・bounded142byte読取・channel size/position/EOF・読取後の同inode/full metadataと同名再open・root前後を検証し、全資源close成功後だけcaller所有byteを返す。読取bufferはfinally消去。

publish(name, canonicalBytes, partUUID)はbyteを独立copyし名前/値を検証してからmutationへ進む。既存は全byte/元inode一致だけforce/syncし、内容を一切変更しない。新規はcaller指定UUID.partのCREATE_NEW0600→bounded全byte write/size/force→保持再読と元snapshot照合→no-replace公開/dir sync→公開直後snapshot・再読・同名の全metadata/ctime再照合。renameだけのctime変化は許すが、その後の変化を許さない。既存part・競合target・部分失敗は保全し、自動上書き/再生成/消去はしない。part UUIDは非秘密の操作識別子でありrun原本の再採番ではない。

remove(name, expectedBytes)はcallerが完了/GC条件を別に確認した後だけ使用する。初回不存在だけ冪等成功、存在時は全byte/元inode・直前full snapshot一致の後に限定unlink/dir sync。失敗時は逆操作や補完をせず不確実性をcallerへ返す。公開/削除のrootはidentityを前後比較し、自身のmutationによるdirectory size/時刻変化だけを許す。開始/終端割込とEUID0を検査し割込flagは保持する。owned channel/entryは全終了で閉じ、IO診断はscope終了後に固定化、未知runtime/NPEを正常化しない。

PT-BAT-046～057/017の009・010はliteral72/109/140/141byteと実隔離inode/native no-replace/fsyncに合成root属性・fault portを組み合わせる。固定namespace/実root配備・state graph/OS lock/親終端/400日GC/DB参照判定はこの低位能力で認定しない。

### 6.15 固定永続namespaceとrun lifecycle（SSC-055/PG-D-158、先行36b5f85b）

SSC055/PG159追補（先行4c5dcb85）: 新run start前のDB既存ID確認とresume整合・GC同run参照は331 §3.12/332の限定readを使用する。親がOS/DB排他を維持して全3参照0/identity整合を確認し、DB不通/不明/nullを不存在扱いしない。原本なしlegacyはprogressから復元しない。GCはread成功だけで開始せず、既定400日/全activation完了/marker確定の全条件を別途満たす。RunReferenceRepositoryの実装・単体合格は親/GC実装の完了を意味しない。

BUG159/YKT124（先行12446fed）: 再開は既存byteの可視性だけを成功条件にしない。全graph/対象条件を検証した後、選択runのanchor→対象begin→既done（存在時）→active（存在時）の順に同byte force/dir syncで再確定してから、active再利用結果を返す。activeなしresumeはanchorを再同期し、未完了beginならそれも再同期、新beginなら新規公開し、最後にactiveを公開する。completeはanchor→begin→active（存在時）を再同期した後、同値確認済みdoneを新規公開または再同期し、active退役・不存在を含めた親dir syncを確定する。全force/syncの失敗・null part supplierは非成功とし、前回の未確定commitをsuccessへ変換しない。byte/UUID/cutoff/mtimeは変更せず、全graphの期待値を再照合する。

MaintenanceRunFiles.createは固定/varとnative能力だけを構成する。公開execute(Operation)はcallerが保守OS flockを獲得し、root管理者のnamespace変更を禁止した区間でのみ使用する。/var→lib→schubert-nk（共有root:root0755）→maintenance→runs/attempts（private root:root0700）をNOFOLLOWで6個の独立FDとして保持する。全scopeはlocal永続RW・ACLなし、private3rootは同device、共有祖先の別local mountは許すが毎回identity/属性を固定確認する。applicationによるmkdir/chmod/修復なし。操作前後と各record mutationの境界で固定namespaceのfresh6rootを再openし元snapshotのidentityと比較する。自身のmutationによるdirectory size/mtime/ctimeだけはidentity比較の対象外、scan内はfull snapshot一致を要求する。

callbackへ渡すSessionはscope内だけ有効。各操作をprivate lockで直列化し、execute終端で無効化してから全rootを逆順closeする。callback例外/null/割込/任意close失敗では成功を返さず、既公開fileを逆操作で消さない。close後に保存したSessionを使用しても拒否する。操作を実行中の別threadがある場合はその終了を待って無効化し、owned資源を使用中にcloseしない。callerはcallback外へSessionや非同期処理を持ち出してはならない。IOはscope終了後に原因/suppressedなし固定StorageIoException、未知runtime/NPEは非成功を維持する。

scanはmaintenanceの全直下名（runs/attempts/activeだけ）とruns/attemptsの全直下名を、保持directoryのDirectoryStreamを閉じてから検証する。既知名だけをfilterして不明を見落とさない。null/重複/別parent/不正segment/stream故障・途中mutationは不正。runsはcanonical UUID.run、attemptsはUUID.begin/UUID.doneだけ。unknown/.part/GC markerは保全し通常new/resume/completeを拒否する。GC markerからの限定退役再開は別GC機能として未完了。既知fileは§6.14で全byteを読み、name↔ID、begin↔anchor、done↔begin↔anchor、active↔beginの全値一致を確認する。別cutoff/孤立begin/done、複数未完了beginを拒否する。

anchorだけでbeginがない状態はanchor公開後の中断を表すpendingとして扱い、明示同run resumeでのみ再接続する。未完了beginもpendingであり、pendingは全runで最大1つ。activeがあるときはそのbeginと同一で、他pendingは認めない。active＋同activation doneだけは完了後active消去前の回復状態として認める。複数孤立anchorや未完了beginとの混在は曖昧なため保全拒否する。過去の全完了runは複数保持できる。

| Session操作 | 前提と順序 | 結果/中断保全 |
|---|---|---|
| start(BatchRun, activationUUID) | null/型検証→全scan、active/pendingなし、run UUID未登録、activation UUIDは全履歴未使用。callerがDB既存legacy ID非衝突を別照会。anchor→begin→activeを各durable公開→全graph期待値と照合 | 同じ固定activationを返す。各公開途中の失敗は原本/partを保全、停止/update等はcallerがこの成功後だけ行う |
| resume(runUUID, nextActivationUUID)・activeあり | 全scan、active.runが指定runと一致 | 同activationとOptional completionを返す。doneありは回復状態であり今回の副作用実行成功とは数えない。勝手にactiveを消さず、親終端確認後completeへ |
| resume・activeなし/未完了beginあり | pendingが指定runだけ、anchor/未完了begin完全一致 | 同beginからactiveだけ再公開、同activationを返す。nextActivationUUIDへ取り替えない |
| resume・activeなし/anchorのみまたは全activation完了 | 原本必須、他runのpendingなし、nextActivationUUID未使用 | 新begin→active、原本cutoffを変更しない。旧completionを新activationへコピーしない |
| complete(MaintenanceCompletion) | 全scan、指定activationとanchor/begin一致、activeは同activationまたは同done確定済みの不存在。別active/別既done・doneなしでactive不存在は拒否。callerは実子終端/親の許容morning終端/DB stepを別確認 | 同doneは全値一致だけ、新doneはdurable公開→同activeだけ退役→全graph照合。同じcompletion再試行は冪等。別終了時刻/0↔10で上書きしない |

Session内の各publicationは非秘密UUID supplierからpart identityを採り、null/既存part collisionを成功にしない。run/activation UUIDやcutoffはcaller指定の検証済み値を再生成/丸めず、supplier値で代用しない。read-only scanで正常化/DB補完をしない。返す状態はimmutable activationとOptional completionだけで、directory/byte/FD/秘密値を公開しない。

本scopeは原本file lifecycleのPG/PTであり、OS flock実獲得・親process/DB stop/reboot/実子起動・step/backup・legacy DB衝突・400日GC/参照照会は別未完了条件。fixtureの合成root権限を実root配備済みとしない。PT-BAT-058～081/017の011・012で全namespace/全graph/crash/fault/close/null/並行/再開の独立期待値を検証する。

### 6.16 完全な退役計画による原本GC（SSC-055/PG-D-161、先行4d534ba9）

BUG172/YKT133修正前追補: metadata-only recoveryのanchor不存在は前回unlinkの耐reboot確定を意味しない。対象originalが全て不在と照合した後、planを一つでも消す前にmaintenance/runs/attemptsの3private rootをsyncし、前回の未確定unlinkをdurable化する。同期失敗では残存plan/markerを保持し非成功。最後だけのsyncではmetadata先行消去を防げないため代替不可。

§6.13のactiveなしは対象runのactiveなしを意味する。別runの有効なactive/pendingは§6.15の最大1件条件で保全し、現在のmorningのcompletion確定前に過去runのGCを行える。全namespaceのunknown/partは拒否する。通常start/resume/completeはplan/markerがあれば非成功、中断GCの回復を先に実行する。親の連続OS flock、同一borrowed ReadCommitted transaction/backendのDB advisory自己exclusive保持、子終端、管理者によるnamespace変更禁止を全区間で要求する。GC部品はOS lock獲得や親終端を代行しない。

Session.retirementCandidates()はimmutableなrun UUID文字列順のBatchRun一覧。planまたはmarkerがあればその唯一の対象runだけを返す。それ以外は全activation完了かつactive対象外のrunを返す。age/DB参照はこの列挙だけで許可済みにしない。Session.retire(run, now, RunReferenceRepository)の結果はABSENT（原本/plan/markerの初期不存在で退役成功とは区別）、TOO_YOUNG（最新completionから400日以下）、PROTECTED（対象active/未完了、または初期DB参照あり）、RETIRED（限定退役・最後の同期/照会まで成功）。run/now/repositoryのnullは契約違反、nowはUTC年0001～9999/µsであり現在時刻の内部取得・丸めをしない。原本の同UUID異cutoff、DBidentity不整合/不明/不通、plan開始後の参照復活は固定非成功で保全する。

退役は次の順序を変更しない。

1. 全namespace/full snapshotを安定読取、対象の全activation完了・active対象外・最新終了から厳密400日超・同run DB3参照0/identity一致を確認する。
2. `attempts/<activation UUID>.plan`へ各doneと完全同byteのNKDONE1をdurable公開/再同期する。全planは対象run一つだけ。marker前の部分plan再開は元の完全graphとの一致を確認し、不足分だけ追加する。既存不同byte・不明partを上書き/推測修復しない。
3. 完全plan集合のcountとdigestを確定し、`maintenance/<run UUID>.retire`をdurable公開する。digestはASCII `NKPLAN1\n`の後にactivation UUID文字列順の各canonical NKDONE1全byteを連結したSHA-256小文字hex。countは1～2147483647の正規十進で恣意的activation上限を設けない。
4. markerが保持されanchorが存在する間は全plan集合のcount/digest/最新完了を照合する。残存originalは必ず同planに一致し、planにないoriginalは拒否する。完全planから仮想完全graphを再構成して別runを含む全参照を検証し、削除済みoriginalを現在時刻や残存doneで補完しない。各activationのdone→beginを同byte限定remove/dir sync、その後anchorを限定remove/syncする。anchorが残る間はplanを一つも消さない。
5. anchor不存在時は対象original attemptが0であることを要求し、残存planはmarkerのrun/最新終了以下・canonicalであることを照合して限定remove/syncする。最後にmarkerだけをremove/syncする。削除済みplanを再生成しない。全plan/marker消去後も3private rootをsyncして不可視の前回unlinkを確定する。

各plan/marker公開・original/plan/marker削除の前、および最終scan後にRunReferenceRepository.readを再実行し3参照0/identity一致を要求する。最初から参照ありのPROTECTEDは副作用0、準備開始後の参照ありは非成功。各mutation境界で保持namespace、期待graph/plan集合を再照合し、他runのrecordを変更しない。これは排他規約を破るDB superuserとのatomicity保証ではない。部分失敗で逆操作・recursive delete・DB参照の期限による無視をしない。

| record | 正規ASCII LFの順序 | 長さ |
|---|---|---:|
| plan | 既存NKDONE1をそのまま使用。nameはactivation UUID | 140/141 |
| marker | `NKRET1`、run UUID、cutoff、latestEnded、preparedAt、count、digest、最後LF | 195～204 |

時刻は§6.13の27byte。latestEnded>=cutoff、preparedAt-latestEnded>400日、全時刻年0001～9999/µs。MaintenanceRetirementは不変型・null拒否・toString redact、MaintenanceRecordsは独立byte所有・再encode完全一致・固定不正診断。DurableRecordFilesの限定名へ.plan/.retireを追加し各内容IDと束縛、bounded bufferは205byte（最大+1）とする。old record/原本内容/外部処理は不変。SHA256取得失敗は資源close後固定IO非成功、未知runtime/NPEは成功化しない。

017/015・016/PT-BAT-090～113の独立literal/digest、厳密400日、全8参照組合せ、全crash phase/IO位置/close/並行/nullで検証する。GC成功はこの部品の条件だけであり、親morning/backup/実server/IT/ST完了を意味しない。SSC055は親への実接続まで継続。

## 7. 環境差分


| 項目 | Local dev | PT/IT | Production |
|---|---|---|---|
| PostgreSQL/Artemis | Container/専用instance可、実製品同major | Java 25/PG18/Artemis導入minor | 単一server、loopback |
| DB | 個人専用DB | Testごと初期化 | `schubert_nk`、real data |
| Port/root | Workspace専用非衝突値 | Test host専用 | 本書のdefault |
| Credential | Test限定のrandom secret | CI secret store | systemd credential、0600、Git禁止 |
| TLS | Loopback/test CA | Test CA | Caddy internal CA/IP |
| Monitoring | DEBUG可 | DEBUG/STANDARD両方 | STANDARD |
| Asset | 最小fixture＋必要時read-only copy | Full sanitized/real authorized copy | Full 59,627 file baseline |

H2、in-memory JMS、UTF-8以外のwire、relaxed validation、ADMIN固定passwordでPostgreSQL/Artemis/securityを代替しない。
環境差分は`config/environment-matrix.yml`のallowlistと本表を照合し、業務仕様のprofile分岐を作らない。

## 8. 初期data

### 8.1 Migration固定master

| Data | 値 | 検証 |
|---|---|---|
| `games` | `(1,NUKITASHI1,NUKITASHI,1)`、`(2,NUKITASHI2,NUKITASHI2,2)` | 2件、code/order UK、UI 223一致 |
| Code/state/role | DB CHECKとJava enum | 全enumのDB/Java/wire照合 |
| Schema history | 期待Flyway version | checksum/installed rank正常 |
| MQ Address/Queue | 321の6組 | Auto-createではなくconfig初期化 |

### 8.2 Bootstrap account

- 現行`user_pass.txt`を移行せず、初期ADMINを安全なoneshot `schubert-nk-bootstrap-admin.service`で1件作成。
- Username/passwordはsystemd credentialから読み、passwordは画面と同じvalidation、`{pbkdf2-v1}`でhash化し、平文はmemory使用後zero。
- `app_users` 0件の場合だけ実行、複数回/既存Userありは無変更でexit 20。固定default passwordなし。
- 作成後に別sessionでLogin・password変更・ADMIN権限を確認。Bootstrap credential sourceは承認済み手順で無効化/削除。

## 9. Flyway migration

### 9.1 責務分離

- Migration実行は`schubert_migration`が`nk_owner`へ限定SET ROLEするoneshot。API/Web起動時にmigrate/repair/cleanしない。
- History tableは`schubert_meta.flyway_schema_history`、`validateOnMigrate=true`、`outOfOrder=false`、
  `baselineOnMigrate=false`、`cleanDisabled=true`。Migration checksum変更をrepairで隠さない。
- Application起動はmanifestのexpected schema version/checksumとDB historyをread-only検査し、不一致はreadiness false。

### 9.2 Initial sequence

| Version群 | 内容 | Transaction |
|---|---|---|
| V001 | extension/schema、owner/default privileges | DBA事前作業と分離 |
| V002 | Account/session/master table、PK/FK/UK/CK | 1 migration transaction |
| V003 | Question/message/log/batch/Web technical table | 1 migration transaction |
| V004 | Btree/partial index、小規模initial data | transaction |
| V005 | GIN/pg_trgm index、grant/view | Full data load前は必要indexだけ、後続で最終化 |

実装時の実version番号は上記責務順を崩さず、1つの巨大migrationへ集約しない。
`CREATE INDEX CONCURRENTLY`等のtransaction外DDLが必要な場合は個別migrationに分離し、失敗/再開手順を追記。

## 10. 現行data移行・inventory

| 対象 | Current baseline | NKの検証 |
|---|---:|---|
| Master file/総byte | 59,627 / 19,240,707,190 | 全file count/byte/SHA-256 |
| Scenario file/entry | 262 / 99,661 | DB count、display order、代表検索 |
| Audio metadata/link | 37,256 / 35,201 | File/hash、orphan/game不一致0 |
| Video | 20 | Stable logical ID/category/pair/order、Range |
| Music | 129 | SHA-256 logical ID、section/pair/order |
| Current log/account | 非移行 | NKは初期event/新規accountだけ |

### 10.1 ETL順

1. Current source/program/DB/materialのcommit/hash/path/mtime/size/countをread-only inventory。作業copyをstagingへ作る。
2. File pathをNFC・root-relative storage pathとsanitized display pathへ分離。絶対/path traversal/NUL/control/symlinkを拒否。
3. SHA-256/byteとcategory/pair、現行ID→NK ID/display order対応表をcanonical manifestへ作成。
4. `pg_temp`のstaging tableへCOPYし、件数・型・NFC/byte・参照を検査。Targetが空の初期DBへ1 transactionでinsert。
5. GIN/final index作成、ANALYZE、全FK/CK/UK/orphan/game不一致・link順を検査。
6. Asset staging全fileをmanifestで照合後、application停止中に確定asset rootへ同filesystemでatomic切替。
7. CHR、UI 254受入、backup/restore、morning runをrehearsalし、所要時間/disk peakを記録。

ID再採番は可だが、現行順を`display_order`に固定し、対応表をmanifestに残す。
Current bookmarkのDB ID互換を新しい要件として暗黙追加しない。

## 11. Deploy・application rollback

### 11.1 Deploy

1. Releaseを新version directoryへ配置、owner/mode/`SHA256SUMS`/manifest/signatureを検証。
2. Rendered configをstaging pathでschema/secret/path/port検証。Caddy/systemd/Artemis/PostgreSQLのvalidatorを実行。
3. Backup・停止・Flyway migrate・実効schema/grant検査。
4. `/opt/schubert-nk/current.new`を新releaseへ作り、`renameat`/`mv -T`相当で`current`をatomic切替。
5. Morning dependency順でstart/readiness/smoke、release/config/schema/protocol versionの一致を確認。

### 11.2 Application rollback

- Trigger: Startup/readiness、major functional/security/performanceのGo不可、またはmigration incompatibility。
- Caddy停止→Web/API/Artemis停止→NK可変data dump保全→schema compatibility判定。
- 旧applicationが新schemaを読めるadditive migrationなら`current`を旧releaseへatomic切戻し。
- 読めない場合は当日backupを別restore DBへ検証後、承認済みrestore手順でDB全体を戻す。Down migration/手修正しない。
- Rollback後も新release/config/data dumpを隔離保全し、調査前に上書き/削除しない。

## 12. 現行からの切替・切戻し

### 12.1 Cutover gate

- RD/UI/SSとQA/RDF/UICが必要状態、CHR baseline/harness、PT/IT/ST、full rehearsal、restore test、
  public 55160/TLS、定量count/hash/performanceが合格。
- 停止枠、Go/no-Go/切戻し判定者、判定期限、利用者周知、現行backup保持期間が承認済み。
- 現行program/DB/config/asset/Caddy/NAT/start手順はread-only保全し、NKが上書きしない。

### 12.2 Sequence

```text
Go一次判定
 -> 現行public入口停止
 -> 現行app停止＋最終inventory/hash/DB backup
 -> NK asset/DB最終load＋manifest照合
 -> NK PostgreSQL -> Artemis -> API -> Webのinternal acceptance
 -> Caddy/NAT 55160をNKへ
 -> external acceptance
 -> Go最終判定または切戻し
```

切戻し判定完了まで受入担当者以外の更新業務を開放しない。現行/NKを同時に本番更新可能にしない。

### 12.3 Rollback trigger・手順

Triggerはdata hash/count/FK不一致、Login/検索/media不能、message取違え/重複更新/質問消失、
security境界違反、backup/recovery不成立、公開TLS不能、停止枠内で是正不可能な性能未達。

1. NK Caddy停止、更新遮断。Web/API/Artemis停止。
2. NK切替後可変dataをtimestamp/manifest付きdumpとして隔離保全。現行へ自動マージしない。
3. 現行DB/program/config/asset hashを照合し、保全済み手順で起動。
4. Login/検索/Scenario/audio/video/music/logのsmoke、Caddy/NAT 55160/TLSを現行へ戻す。
5. External smoke後公開。原因、NK保全data、失われ得る更新、利用者影響、再計画を記録。

## 13. Migration/rollback証跡

- Source/target host、current/NK Git commit/tag、release/config/schema/protocol version、tool/hash、operator/判定者・日時。
- File count/byte/SHA-256、DB table/constraint/orphan、mapping count、表示順、CHR/test result、duration/disk peak。
- Backup/restore manifest、Caddy/NAT差分、public certificate fingerprint、Go/no-Go/rollback判定と根拠。
- Password/key/質問本文、credential実値、許諾上不要な個人・著作物pathは証跡へ出さない。

## 14. PT・IT・Rehearsal

- Configの未知/重複/範囲外/missing secret、root/port重複、effective hash drift、production profileのdebug設定。
- Clean OSでdirectory/owner/mode/systemd credential/release配置を再現、serviceごとの読み書き権限負test。
- Flyway validate/migrate/checksum mismatch/out-of-order/partial failure、applicationの自動DDL禁止、旧/new releaseのschema compatibility。
- Current full inventory、不正path/symlink/hash、件数差、ID再採番/display order、再実行、staging失敗・容量・中断。
- Release current切替直前/直後のkill、migration後旧app、backup restore、NK可変data保全、current公開への切戻し。
- 最低1回の全量rehearsalで所要時間、disk peak、停止枠、判定時刻を実測しrunbookに固定。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-039 | Config優先順をjar default→common→service→env→credentialに固定し、unknown keyを起動失敗 | 環境差分とsecret分離を再現可能にし、typo黙認を防ぐ | ConfigurationProperties/schema test |
| SS-D-040 | Flywayはapplication起動時validateのみ、migrateは専用oneshot、clean/repairは自動禁止 | 起動中DDL・checksum改ざんを防ぎ、rollback判定を明示 | Migration pipeline/IT/runbook |
| SS-D-041 | Current/NK切替中の一般更新を最終Goまで許可しない | 二重更新・自動マージ不能なNK質問/account差分を防止 | Cutover運用・ST acceptance |

## 16. 禁止事項

- Secret/asset/dump/log/runtimeをGit/release artifactへ含める、またはproductionの実値をdocument/templateに書くこと。
- Application起動時DDL update、Flyway clean/repair自動、適用済みmigrationのchecksum書換え、手動down migration。
- Current source/dataを移行toolから更新する、現行/NKを同時本番更新可能にする、Go前に現行保全を削除。
- 対象DB/root/release versionを識別せず、広範囲削除・schema drop・restoreを行うこと。
- H2/in-memory MQだけでPG/ITを合格、または環境profileでrole/owner/validationを無効化すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Directory/config/credential/initial data/Flyway/current migration/cutover/rollbackを詳細化。 |
| 2026-08-31 | 横断監査でmigration DB role名をUI 212の`schubert_migration`に統一。 |
| 2026-08-31 | 横断監査でWeb DB poolをUI 212の上限2へ修正し、Web revoke/API context/API InboxのAES keyを用途別に分離。 |
| 2026-08-31 | DB dump credentialをbatch保守用から分離する`db-backup`候補をQA-043/UIC-003回答待ちで追加。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、`db-backup`を専用backup unitだけへ配布するcredentialとして確定。 |
SSC061/PG168: 341 §6.6の真正root manifestはroot CREATE_NEW/0600・書込FD全close・fsync/atomic/再hashと、読取側のuid0/gid0/nlink1/ACL・namespace/全handle/name/hash検査を前提とする。backup user作成fileのchownで真正化しない。両step DB確定部品はこの前提の代用ではなく、生成/信頼reader・最新選択/7世代は後続で実装する。専用DB/OS資格と秘密鍵配布は変更しない。
