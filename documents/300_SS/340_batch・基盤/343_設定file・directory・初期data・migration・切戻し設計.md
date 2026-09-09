# 設定file・directory・初期data・migration・切戻し設計

## 1. 目的・追跡

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
| `/var/log/schubert-nk` | service group 0750、file 0640 | File logを使う場合のみ | Git禁止、journald優先 |
| `/run/schubert-nk/<service>` | systemd RuntimeDirectory | Lock/socket/temp metadata | Rebootで消去可 |
| `/srv/schubert-nk/staging/<run-id>` | migration user 0700 | 移行中asset/manifest、対象run限定 | Go/切戻し完了まで隔離 |

Directoryはprovisioningで明示作成し、application起動時に不明rootを自動作成/chmodしない。
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

成功/保護あり結果はroot closeを含む全終了後だけ返す。root open/close、credential load、構成不正/暗号primitive故障は例外で終了し、途中結果を返さない。通常DB障害/割込/時間超過は既存InspectionExecutionの非成功を保持する。ここでroot権限を緩和したり、DB credentialを他processへ渡したりしない。ログ/HTTP/JMS/別processを生成しない。PTは実保持inode/file/JDBC/永続SQLと明示synthetic OS属性・fault portを組合せる。実systemd credential正系、Java main/unit、親flock/backup実体/朝batch全順序は別gateであり本接続だけを完了証明にしない。

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
