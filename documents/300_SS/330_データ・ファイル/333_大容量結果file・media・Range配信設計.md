# 大容量結果file・media・Range配信設計

## 1. 目的・適用範囲

Scenario大容量結果fileの生成・descriptor・完全性検証・朝削除と、audio/video/musicの認証済み
HTTP配信、path検証、Range応答、file名/MIME/header安全化を定める。

- 上位設計: [223_現行機能画面設計](../../200_UI/220_画面・認証/223_現行機能画面設計.md)、
  [237_大容量結果・メディア配信設計](../../200_UI/230_インターフェース/237_大容量結果・メディア配信設計.md)、
  [243_ファイル・データ配置設計](../../200_UI/240_データ/243_ファイル・データ配置設計.md)
- 関連RD: MQ-019～MQ-020、MQ-039～MQ-041、MSG-F01～MSG-F09、FIL-001～FIL-009、PER-004～PER-006、OPS-013、MON-009
- 関連QA: QA-001、QA-032、QA-033。RDF/UICなし

## 2. Root・OS権限・責務

| Root | 設定key | Writer | Reader | 権限・禁止 |
|---|---|---|---|---|
| Asset | `storage.asset-root` | 移行・保守account | API/Web | dir 0750、file 0640、serviceはread-only、Caddy非公開 |
| Transfer | `storage.transfer-root` | API | Web/batch | dir 0750、file 0640、APIはCREATE_NEW、Webはread-only |
| Backup | `storage.backup-root` | batch | restore operator | 0700、serviceから非公開 |

起動時に各rootを`toRealPath(NOFOLLOW_LINKS)`し、通常directory、root間非重複・非上下関係、所有者、
permission、Transferのatomic move対応を検査する。検査不合格はreadiness falseとし、自動chmod・root作成・symlink追従を行わない。

## 3. Class・method責務

| Class.method | 引数 | 戻り値 | 例外・責務 |
|---|---|---|---|
| `LargeResultWriter.writeScenario` | immutable record list、`Instant`、`UUID` | `LargeResultDescriptor` | 4,800 byte record、part/ready、hash/fsync/atomic move |
| `LargeResultReader.readScenario` | descriptor | `List<ScenarioRecord>` | descriptor/path/size/hash/record完全検証、最大10,000件 |
| `StoragePathPolicy.parseRelative` | root kind、wire relative path | `ValidatedRelativePath` | NFC、segment、suffix、depth、UUID検証 |
| `SecureFileResolver.openReadOnly` | real root、validated relative path | `VerifiedFileChannel` | SSC-021の共有native保持root/inodeでNOFOLLOW segment walk、同一inodeの通常file/nlink等を検証後read |
| `MediaQueryService.describeAudio/describeVideo/describeMusic` | actor context、media type/logical ID、mode | signed descriptor | API側のrole/DB metadata/manifest検証。311/323のAPI責務名へ統一 |
| `MediaRangeService.deliver` | HTTP Range、descriptor、response | void/HTTP status | Web側の署名・path・size・MIME再検証、stream。311のWeb責務名へ統一 |
| `HttpByteRangeParser.parseFirst` | Range header、file size | `Full/Partial/Unsatisfiable` | 最初のrangeだけ解析、1MiB cap |
| `TransferCleanupService.clean` | run cutoff | `CleanupResult` | app停止/batch lock必須、非follow walk、対象別計数 |

`VerifiedFileChannel`closeはtry-with-resourcesで強制する。File pathの`String`/`Path`をController/View Modelへ返さない。

## 4. Large-result判定・レイアウト

| 項目 | 値 |
|---|---:|
| 対象response | `SCNRSP01` Scenario明細 |
| Inline上限 | 200 recordかつ電文body 1,000,000 byte以下 |
| File record | 4,800 byte固定、UI 234のSCNRSP01 record定義 |
| File record数 | 1～10,000 |
| File byte数 | `4,800 * recordCount`、最大48,000,000 |
| File body | Header/BOM/改行/区切りなし、recordを連結 |
| Path | `yyyyMMdd/<lowercase UUID>.ready`、wire上256 byte以下 |

Record数取得とsnapshot取得は332のread-only transaction内、file I/Oはcommit後。Record順は
SSC-017によりUI223/234に合わせ`entry_index,display_order,id`から採番したEntry sequence、同entryのaudioはlink `display_order,audio_file_id`から採番したAudio sequenceで固定する。閾値は音声展開後record数であり、DB IDの大小を表示順と取り違えない。

## 5. Large-result生成algorithm

1. Record listを最大10,000件へboundし、codecで1件ずつ4,800 byteにencodeできることをI/O前に検証する。
2. JSTの生成日`yyyyMMdd`をdirectory名とし、設定root直下の日付directoryだけをpermission 0750で作る。SSC-020: 新規作成した保持inodeだけへschubert-web group/modeを確定しdirectory fsync。既存dateは所有者/group/modeを検査するだけで修正しない。
3. CSPRNG UUIDで`<uuid>.part`を`CREATE_NEW,WRITE,NOFOLLOW_LINKS`でopen。Collision時は最大3回新UUID（初回＋再試行3回まで）、超過は異常。新規保持partだけへschubert-web group/0640を確定してからwriteする。
4. 64KiB以下のbufferでrecordを順番writeし、同時にSHA-256とwritten byte数を更新する。
5. `FileChannel.force(true)`、close、実size、`recordLength * count`、digestを照合する。
6. 同directoryの`<uuid>.ready`へatomic・no-replace公開する。SSC-019により保持済みdirectory FD相対のLinux `renameat2(RENAME_NOREPLACE)`を使用する。Java `Files.move(ATOMIC_MOVE)`は既存target置換が実装依存なので代替しない。Directoryもfsyncする。
7. Ready fileをNOFOLLOWで開き直し、file ID/path/size/hash/record length/countからdescriptorを生成する。

Encode/write/moveの失敗は`.part`を即時best-effort削除するが、削除失敗を元例外で隠さない。
`.ready`移行後のresponse失敗でfileを削除せず、次回朝処理へ委ねる。

## 6. Descriptor検証・取得

Webは電文decode後、以下の順を変えずに検証する。最初の不合格で打ち切り、fileは利用・削除しない。

1. Delivery mode=`F`、UUID、relative path、size、lowercase SHA-256、record length=4,800、count 1..10,000。
2. `size == recordLength * recordCount`およびsize<=48,000,000。Overflowを`Math.multiplyExact`で検査。
3. Relative pathが`yyyyMMdd/<same UUID>.ready`の正規形、ASCIIであり256 byte以内。
4. Secure resolverによるroot配下の通常file、symlink/hard-link攻撃の防止、設定root外でないこと。
5. Open後attributeのsizeとdescriptor size、SHA-256。
6. 4,800 byteごとに完全readし、各recordの固定長・NFC・充填・項目上限をcodecでdecode。末尾余り0。
7. Decode数=count、Entry sequence/Audio sequenceの組が正順、record重複がないこと。同Entry sequenceのEntry ID/本文等は一致し、IDの大小自体は順序条件にしない（SSC-017）。

Hashはconstant-time比較。検証中の最大memoryをrecord listのView Model相当へboundし、file全byteを1配列へ読まない。
不合格は`FILE_DESCRIPTOR_INVALID` / `FILE_INTEGRITY_MISMATCH`の分類で503、request ID/file ID/検証stepだけlogへ出す。

### 6.1 APIの再送file確認と再生成（SSC-027）

APIはcaller所有の保持Transfer rootを検査後、既存dateとready inodeをNOFOLLOWで開き、通常file/owner/group/mode/nlink/size、4800byteずつのexact EOF/hash、読取後属性を照合する。ここでの確認は物理完全性であり、record decode/View Model生成はWeb readerの責務として維持する。通常の検証はfile/directoryを作成・初期化・変更・削除しない。

MISSINGを返せるのはroot検査成功後の既存date open、またはdate属性成功後でready inode取得前のnative ENOENTだけ。保持inode callback内のNoSuchFile、root/属性/hash/crypto/権限/close/不明I/OはUNAVAILABLEとし、不在へ補完しない。Close失敗を伴う不在は再生成候補にしない。FD番号の再利用と所有を混同せず、callbackのresource所有範囲を字句的に限定する。

不在を確定したcallerだけが、DB snapshotのmetadata全8論理fieldと元snapshotのmetadata（file descriptor部を除く）、record数、4800byte record streamのSHA-256を照合する。原本と一致する場合だけpublisherを1回呼ぶ。新descriptorも元のcount/hash（sizeは4800×count）へ再照合し、key/date/UUID以外の内容を差替えない。生成前の不一致ではI/Oを行わず、生成後の失敗ではreadyを削除しない。既存成功の再生成不能・容量不足を保存ERRORへ上書きせず、一時障害として元Inboxを保持する。保持header/state/ref/completed_at/24h期限を変えないdescriptor置換の最終DB手順は324 §7.1による。

## 7. Path検証の実装規約

### 7.1 論理検証

- Relative pathはNFC、`/`だけをseparatorとする。空、先頭`/`、NUL/control文字、backslash、drive/UNC形式を禁止。
- `.` / `..` / 空segment、末尾slash、二重slashを禁止。Asset relative pathは512 UTF-8 byte以下、
  Transferは256 ASCII byte以下・2 segmentに固定する。Storage pathの各実file segmentは255 UTF-8 byte以下。
- Assetの許可先頭は`scenario/`、`video/`、`music/`。Descriptorのmedia typeと先頭が対応しなければ拒否。
- Display pathはfile解決に使わず、HTML escape後の表示だけ。

### 7.2 OS・TOCTOU対策

SSC-028: Asset adapterは共通`OwnedTransferDirectory`の既存保持能力へ追加する`openExistingChild(singleSegment)`と`atExistingEntryHandle(singleSegment, callback)`を用い、事前に検証済みRelativePathをsegmentごとに辿る。これらはopenだけでmkdir/属性変更/rename/deleteをしない。名称は単一segment、空/`.`/`..`/slash/NULを能力境界でも拒否する。Native実装の複製や元path再解決を行わない。Childは独立FDを所有し親の名前差替え/closeに影響されず、entry callback完了時だけ所有FDをcloseする。Read channelをcallback外へ持ち出さない。

保持Unix通常file/owner/group/mode0640/nlink1/size一致の共通`existingFile`照合は正のlong sizeを扱う。Media callerは先にMEDIA1024のN12上限を検証し、Transfer専用`file`入口は従来の1～48,000,000byteを検査した上で共通照合へ委譲する。MediaをTransferの48MB上限に誤って制限せず、逆にTransferの上限を緩和しない。属性照合はmanifest/hash/readiness/認証の代替ではない。

SSC-021: Readerも共有storage libraryの保持rootから全segmentをO_DIRECTORY/O_NOFOLLOW/O_CLOEXECで相対openし、最終entryをO_PATH/O_NOFOLLOW/O_CLOEXECで保持する。自分が保持しているinodeのprocfs handleでUnix通常file/owner/group/mode/nlink/sizeを確認した後にだけ、その同じinodeからread channelを開く。SDSの名前属性検査と後のchannel openを同一inodeと推測しない。公開FileChannel/PosixFileAttributesはnlink取得APIを持たないため、private FD reflectionや元pathの再解決へfallbackしない。

SDS利用可能性の既存起動検査も維持し、unknown filesystem/providerは拒否する。実file openは上記native inode保持へ統一する。Readerは既存childのread-only openだけを呼び、mkdir/CREATE_NEW/chmod/chgrp/rename/deleteは呼ばない。OSのWeb read-only mount/permissionも別に必須とし、共通libraryの存在をwrite権限付与と解釈しない。`normalize().startsWith(root)`だけのfallbackは禁止する。

Hard link対策としてasset/transfer filesystemの書込権限を専用accountに限定し、Unix `nlink=1`を対応環境で検査する。
不明なfile store/attributeはdeny closed。

### 7.3 API writerのdirectory capability（SSC-019）

SSC-021でReaderも同じ低位能力を共有する。Writerのmkdir/非上書きatomic公開はJava25の公開FFMからLinux libcのopenat/mkdirat/renameat2/unlinkat/fsync/closeを呼ぶ限定portで実現する。Preview、JDK internal API、private FDのreflection、shell subprocessを使用しない。Rootは`/`から全segmentをO_DIRECTORY/O_NOFOLLOW/O_CLOEXECで相対openし、起動時の所有者/permission/非重複検査後も自分で取得したdirectory FDを保持する。

日付directory作成とUUID entry操作はそのFD相対だけで行う。FileChannelでのCREATE_NEW/read/attribute取得に必要なpathは、自processが保持中のFDを指すkernel procfs `/proc/self/fd/<owned fd>/<validated generated name>`に限定する。利用者pathや置換可能な元root pathを再解決しない。FDは操作中close/reuseされない寿命管理を行い、close失敗時に同じ番号を再closeしない。File名の最終symlinkは常にNOFOLLOWで拒否し、nlink=1等の既存検査を省略しない。

Linux/glibc、native access、procfs、必要attribute、directory fsync、同filesystemのRENAME_NOREPLACEが揃わない場合はreadiness false。未検証network filesystemは使用しない。Root作成/chmod、check-then-move、hard-link公開、通常renameへのfallbackは禁止する。JVM設定と実機適合試験は342/354へ追跡する。

Writerのsize/hash再検証では、名前の事前検査とFileChannel openの間の差替えを避けるため、FD相対openat(O_PATH/O_NOFOLLOW/O_CLOEXEC)でentry inodeを先に保持する。O_PATHはsymlink自身も保持できるので、own FDのprocfs magic link経由で得たUnix属性の通常file0640・owner/group・nlink=1・sizeを確認するまでread channelを開かない。確認後も同じ保持inodeのprocfs handleからだけreadし、元entry名は再解決しない。Symlink/device/socketは属性段階で拒否する。Scoped entry FDはcallback完了/例外で必ずcloseし、複合I/O/close故障は外部pathを含まない一時障害へ再構成する。

SSC-019/PG-D-059補足: partの初回作成もopenatのO_CREAT/O_EXCL/O_WRONLY/O_NOFOLLOW/O_CLOEXEC・0640で行い、CREATE_NEW時点からそのinode FDを保持する。生成後の名前再解決からmode/groupの変更先や書込み先を決めない。FileChannelは保持FDのprocfs capabilityから開き、channel/native FDの双方を明示closeする。全件byte配列を準備せず、PayloadCodecの単一record encodeを共用し、全件sequence検証と1件ずつの事前byte検査後、4,800byteずつ再encode/writeする。Data/headerを捏造してfile recordをencodeしない。

### 7.4 起動時の診断専用probe（SSC-022）

業務producer/HTTP受付前かつ他writer/batch停止のexclusive startup区間で、実Transfer filesystemの新規group/mode設定、file force、directory fsync、atomic no-replaceを検査する。Rootは自動作成/chmodしない。診断日付はJST正規date、新規dateだけをSSC-020の属性へ確定し、既存dateは検査だけとする。

CSPRNG UUIDの診断partをCREATE_NEWで保持し、秘密を含まない4800byte固定pattern Aを書いてforce/属性/独立hashを検証、readyへnative no-replace公開する。同UUIDの新しい診断partに異なるpattern Bを書き、readyへの二度目の公開がCOLLISIONとなりA/B双方のbyteが保たれることを検査する。通常rename/置換へのfallbackはない。Probeのfileは業務結果ではなく、descriptor/Inbox/業務message/HTTPへ返さない。

ProbeはCREATE_NEW成功で所有を確認したpartと、公開成功を確認した**自分の診断readyだけ**をその保持dateから清掃し、directory fsyncする。Ready清掃前に保持inodeの属性とdiagnostic A hashを再確認し、変質/検査不能なら保全する。既存衝突先、所有不明entry、公開結果不確定のreadyは削除しない。清掃失敗/close失敗/不確定公開は起動不合格とし、全体scan/ready成功へ算入しない。残った診断entryは既存の次回朝清掃/運用調査対象とする。新規empty dateは無断削除しない。

この限定された起動診断の清掃を、通常writer/readerや業務ready削除へ流用しない。通常のlarge-result lifecycleは従来どおり次回朝batchへ委ねる。Probe成功後の完全scanだけで容量を初期化し、single-instance/exclusive保証・full root検査・service readinessへの結線を別途検証する。

## 8. Media認可・descriptor

1. Browser requestごとにWeb HTTP session、CSRF不要のGET、認証contextの有効性をAPIで検証。
2. APIはIF-009/012/016でlogical ID、media type、inline/download modeを受け、DB metadataとmanifestを参照。
3. Descriptorにlogical ID、storage relative path、safe file name、byte size、SHA-256、allowlisted MIME、mode、
   message/correlation IDを入れ、MQ HMAC検証済みresponseとしてWebへ返す。
4. Webはdescriptorと要求URLのlogical ID/type/modeを再照合、secure open後のsize、必要時hashを検証。
5. Authorization済みchannelだけをstreamし、pathはBrowser/HTML/HTTP header/logへ出さない。

DescriptorはHTTP session cacheの権限正本にせず、各GETでAPIへ照会する。ID不存在・非scopeは404、
API/MQ/file integrity障害は503。内部理由をBrowserへ区別表示しない。

MEDIA1024の許可MIMEとstorage file拡張子は次の完全一致allowlistとする。大文字小文字や別名を推測して受理せず、DB/manifest、descriptor、
拡張子の組合せが不一致なら配信しない。これはSSC-004により、UI 221/223/235/237の現行互換規則を実装可能な値へ具体化したものである。

| 種別 | Storage拡張子 | Descriptor MIME | Disposition |
|---|---|---|---|
| Audio（IF-009） | `.ogg` | `audio/ogg` | `I` / `A` |
| Video（IF-012） | `.mp4` | `video/mp4` | `I`のみ |
| Music（IF-016） | `.m4a` | `audio/mp4` | `I` / `A` |
| Music（IF-016） | `.mp3` | `audio/mpeg` | `I` / `A` |
| Music（IF-016） | `.ogg` | `audio/ogg` | `I` / `A` |
| Music（IF-016） | `.wav` | `audio/wav` | `I` / `A` |
| Music（IF-016） | `.flac` | `audio/flac` | `I` / `A` |

Attachment時もdescriptorには実体の上表MIMEを設定し、HTTP応答だけを`application/octet-stream`へ固定する。

## 9. Endpoint・HTTP header

| Endpoint系 | Mode | Status/header |
|---|---|---|
| `/audio/{id}` | inline | 200/206/416、検証済み`audio/ogg`等、`Accept-Ranges: bytes` |
| `/audio/{id}/download` | attachment | Rangeを採用せず200全長、`application/octet-stream` |
| `/animation/media/{id}` | inline | 200/206/416、allowlist `video/mp4` |
| `/music/media/{id}` | inline | 200/206/416、metadataと一致するallowlist audio MIME |
| `/music/download/{id}` | attachment | Rangeを採用せず200全長、`application/octet-stream` |

全media responseに`X-Content-Type-Options: nosniff`、`Cache-Control: private, no-store`、`Content-Length`を設定する。
`ETag`、`Last-Modified`、public cacheは初期releaseで使わず、conditional GETは200で応答する。

Descriptorの表示/download file nameはNFC、1～256 UTF-8 byte、CR/LF/NUL/quote/slash/backslash/control文字禁止。
これはstorage pathの実segment名（255 byte以下）と別metadataであり、OS path解決に使わない。
`Content-Disposition` attachmentはASCII fallbackを安全な`download.bin`等にし、
`filename*=UTF-8''<RFC 5987 percent-encoded>`を使う。Header valueにraw file nameを連結しない。

## 10. Range解析・応答

### 10.1 Grammar・判定

- Headerはcase-insensitiveの`bytes=`だけ。他unit、空spec、数値以外、負数、overflowは416。
- Commaがある場合は現行互換のため最初のspecだけをtrimして採用し、2件目以降を解析しない。
- `start-end`、`start-`、`-suffixLength`を受ける。`end < start`、suffix 0、start>=file size、file size<=0は416。
- Decimalは`Long.parseUnsignedLong`相当で上限検査し、演算は`Math.addExact/subtractExact`でoverflowを416にする。

### 10.2 範囲計算

```text
MAX_BODY = 1,048,576

start-end: start = requestedStart
           requestedLast = min(requestedEnd, total - 1)
start-:    start = requestedStart
           requestedLast = total - 1
-suffix:   start = max(total - suffixLength, 0)
           requestedLast = total - 1

last = min(requestedLast, start + MAX_BODY - 1)
length = last - start + 1
```

| 入力 | Status | Header/body |
|---|---:|---|
| Rangeなし | 200 | 全長、`Accept-Ranges: bytes`、正しいMIME |
| Valid単一/複数の最初 | 206 | `Content-Range: bytes <start>-<last>/<total>`、body最大1MiB |
| 不正/満たさない | 416 | `Content-Range: bytes */<total>`、bodyなし |
| DownloadにRangeあり | 200 | Rangeを無視し全長、attachment |

206の`Content-Length`=`length`、200の`Content-Length`=total、416は0。Channel positionをstartへ移し、64KiB以下のbufferで
ちょうどlength byteをstreamする。`InputStream.transferTo`等でendを超えない。HEADはGETと同じ認可/headerだけとしbodyなし。

## 11. Streaming中の異常

| 異常 | HTTP処理 | Log/metric |
|---|---|---|
| Open前の欠落/root外 | 404または503 | Logical ID、request ID、検証step |
| Size/hash/MIME不一致 | 503、stream開始しない | Critical integrity alert |
| Header commit後のread I/O | Connection close | Sent bytes、error code、physical pathなし |
| Browser/client abort | 追加responseなし | INFOまたはDEBUG、error alert除外 |
| 同時stream 20超 | 503または429相当 | Rejection count、Retry-After 1 |

Stream permitはprocess内semaphore 20、acquire wait 0。認証・descriptor検証後、file open前に取得し、
response完了/例外の`finally`で必ず解放する。

## 12. Transfer朝削除

削除はAPI/Web停止後、systemd batch lockとDB batch advisory lockの両方を取得して行う。

1. 起動時に保持したthe real transfer root directory handleから深さ2以内をNOFOLLOWで列挙。
2. 日付directoryは`^[0-9]{8}$`、fileはUUID＋`.part|.ready`のみ。起動cutoff以前に列挙した通常fileだけ対象。
3. Symlink、directory下の不明entry、device/socket、hard-link異常は削除せずwarning。Root自体は絶対に削除しない。
4. Fileごとにsizeを計数後、directory handleからentry名指定でdelete。空になった正規日付directoryだけ削除。
5. Target/success/failure/skipped count、byte数、最初error codeを`batch_runs`に記録。個々のphysical pathはlogしない。

Web取得成否、HTTP転送完了、descriptor replayの有無で日中削除しない。
File完了ACK・新規MQ layoutを追加しない。

## 13. Capacity・metric・alert

| Metric | Warning | Critical/処置 |
|---|---:|---|
| Transfer 1 file | 40MB | 48MB超は生成拒否 |
| Transfer root byte | 3.5GB | 4.5GBで新規生成停止、5GB設計上限 |
| Transfer file count | 5,000 | 9,000で新規生成停止、10,000上限 |
| Concurrent stream | 16 | 20超を即時拒否 |
| Integrity failure | 1 | 即critical、対象配信停止 |
| Cleanup failure | 1 | Warning、同一entry継続失敗はcritical |

Metric labelにpath、file名、user ID、media IDを設定しない。Type、status、error codeの低cardinalityだけにする。

## 14. Test matrix

### 14.1 Large-result

- 1/200/201/10,000/10,001 record、4,800 byte・48,000,000 byte境界、乗算overflow。
- `.part` open/write/fsync/atomic move/移行後responseごとのprocess kill。Existing UUID、同fst非対応。
- DescriptorのUUID/path/size/hash/record length/count改ざん、切れrecord、重複/順序逆転。
- Symlink全segment、hard link、root差替え、TOCTOU、device/socket、permission denied。

### 14.2 Media/Range

- Rangeなし、`0-0`、`0-1048575`、`0-1048576`、`1048576-`、`-1`、`-1048576`、suffix>file。
- End>file、start=end、start=file size-1、start=file size、end<start、空/負/非数/overflow/unknown unit。
- Multiple Rangeの先頭valid＋後続invalid、先頭invalid＋後続valid。前者は206、後者は416。
- Download Rangeは200全長、UTF-8 file名、CRLF/quote攻撃、MIME改ざん、auth/session失効。
- 20/21並行stream、client abort、header commit後I/O失敗、buffer上限・FD leak。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-030 | Path openはLinux `SecureDirectoryStream`と`NOFOLLOW_LINKS`を必須とし、非対応filesystemは起動失敗 | UI 237のroot/symlink防御をTOCTOUも含めて強制 | 実機filesystem適合IT、fallback禁止 |
| SS-D-031 | Media Range解析は最初specだけ採用、response bodyを1,048,576 byteへ切る | UI 223/237の現行互換、memory/帯域上限 | Range golden case/CHR比較 |
| SS-D-032 | Media descriptorをsession権限cacheにせず各GETでAPIに照会 | 無効化直後の既存URL配信を防ぎ、Webの業務DB非参照を維持 | MQ性能/10名並行IT、session revoke test |

## 16. 実装禁止事項

- Caddyのstatic file配信、asset/transfer rootのDocumentRoot化、Browserへのphysical/storage path開示。
- `Path.normalize().startsWith(root)`だけのpath検証、symlink follow、利用者入力file名でのopen。
- Hash一致を認可の代替にすること、またはMIME/file nameをHTTP headerへ無検証反射すること。
- File全体の`byte[]`読込、Range end超過転送、download endpointの206応答。
- Web取得後の日中transfer削除、ACK追加、root自体の再帰削除。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Large-result、secure path、media認可、Range、朝削除の詳細を作成。 |
| 2026-08-31 | 横断監査でmedia endpoint pathをUI 221/SS 313と同一の外部URLへ統一。 |
| 2026-08-31 | 横断監査でAsset 512/Transfer 256 byteのpath上限と、wire表示file name 256 byteをUI 235/237に統一。 |
| 2026-09-01 | SSC-003によりAPI descriptor発行を`MediaQueryService`、Web Range配信を`MediaRangeService`へ統一し、311/323との委譲関係を明確化。 |
| 2026-09-02 | SSC-004によりmedia descriptorの7拡張子/MIME組合せとHTTP attachment専用`application/octet-stream`を固定。 |
