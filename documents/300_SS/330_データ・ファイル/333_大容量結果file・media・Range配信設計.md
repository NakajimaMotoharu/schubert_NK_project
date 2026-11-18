# 大容量結果file・media・Range配信設計

## SSC308 取得前port構築・factory内IO所有とdescriptor wrapper先行確保

完成ownerへの内部移管補足（BUG1414/YKT1178、2026-10-19）：`ResourceScope.handoff(Acquire<R,E>,Release<R>,OwnedAction<R,T>)`は既acquireと同じ取得/失敗優先規則の上で、Rの完全なowner Tを組み立てて渡す内部補助とする。全portのnonnull検証・primitive移管状態・条件付release/assembly callbackはR取得前に構築する。組立/検証中はRを保護し、完成Tのnonnull確認が成功した最後だけprimitive状態を移管済みにして即返却する。移管後の補助releaseは事前構築したno-opであり、Rを閉じる責任は返却済み完成ownerだけにある。未完成/null T、組立IO/Runtime/Errorでは同一Rを一度解放し既Reason/unknown identity/秘匿suppressed/複合優先規則を適用する。factory失敗/null Rは既acquire同様body/release0、成功移管を業務完了やkernel close成功へ読み替えない。

この補助はfactory内部のDirectory→Files/匿名wrapper→上位ownerの連鎖でも各完全組立境界で適用し、取得後かつ保護外でnew/lock/policy/残callbackを作らない。失敗時の未確定ownerを再利用せず、返却後の元所有者による二重close/権限拡張・外部success入口は追加しない。原237use候補外の直接open/TWR/手動tryも別母数で照合し、検索だけで全体完了にしない。

StartupAdmissionFile.ViewOwner追加詳細（BUG1414/YKT1178、2026-10-18）：private readonly viewの全取得予定数はroot1＋runtimeのN segment＋app1＋entry1＝N+3。owner/primitive int slot/failure scratch/全portを最初のnative open前に有限確保する。各openRoot/openDirectory/openEntryはclosed/容量を取得前に検査、有効かつ既保持FDと異なる返却値の後はprimitive比較/格納/返却だけとし、Integer boxing・List grow・callback/new・追加Java helper呼出しを挟まない。負値は新所有なし、既保持FD自身の返却も新所有とせず拒否し元FDを一度だけ消費する。runtime/固定名/権限/NOFOLLOW/host-private照合と外部能力は変更しない。

同ViewOwnerのcloseは既消費flagを先に確定し全保持FDへ逆順に一度ずつnative closeを試みる。drain中はcallback/配列/例外/suppressed等を新規確保せず、事前scratchへ失敗を記録し全試行後だけ既ResourceScopeと同じIO Reason/unknown identity/複合優先順位・秘匿suppressedを組み立てる。消費済みは再close/再openへ使わず、native closeが例外を返した事実をkernel解放成功へ読み替えない。失敗FD数値の再試行や別authorityによるcloseは禁止。単なる検索/use置換や実heapOOME未再現を完了根拠にせず、独立fault matrix/実bytecodeと必要同source全体/nativeで別資格する。

native FD横展開の確定詳細：LinuxFileLockのopen/dup及びLinuxSealedProofのmemfd/reserved取得では、全portとprimitive保持wrapperを取得前に確保し、有効FD取得後は非負確認/primitive格納/返却だけとする。dupが元FD自身を返す異常は新所有ではなく元FDの二重closeをしない。factory後にInteger boxingやObjects/literal解決を挟まない。元flock/flags/seal/mode/write/範囲/close優先順位と消費回数を保持する。

実装詳細の確定補足：factoryの戻りをslotへ格納した直後からIO/Runtime/Error保護域へ入り、標準nonnull検査もその保護域内で行う。null返却はNPEを伝播しbody/release0、非null資源の失敗時だけreleaseする。成功資源を保護域外のliteral解決/明示例外確保/boxingへ露出させない。これは既null拒否/例外優先順位を変えず、静的解析の抑制も追加しない。

BUG1414/YKT1178、FIL001009/OPS009・UI237251、WBS-P003-08（共通scope）/P003-04（保持directory）。RD/UI/外部file/HTTP/権限契約変更不要。既ResourceScope.useの引数検証・IO正規化/既Reason・unknown例外優先順位はそのまま保持する。追加factory所有入口ではAcquire<R,E extends IOException>/Release<R>/OwnedAction<R,T>を全て取得前に構築・nonnull検証し、helper内で同一Rを取得した直後から保護域に入れ、releaseへ当同一objectを一度だけ渡す。factoryのchecked E・Runtime/Error失敗はbody/release無しで元identityを伝播、null返却はfail-fast。bodyのnullable結果契約は既use同様に明示して許容する。

取得後のbody/close規則：成功はbody結果→release、IOはStorageIoExceptionの既path-free固定messageへ変換し、既storage reasonはsuppressed無しの場合だけ保持する。primary IOにsecondary Runtime/Errorならsecondaryを優先、その他はprimaryを保持しsecondaryを固定StorageIoExceptionで秘匿suppressedへ追加、同一object/self-suppressionを新規導入しない。Java TWRの別優先順位へ置換しない。Acquire以後・保護域前のcallback/new/boxingをなくし、実Java25 bytecodeと独立matrixで確認する。新公開Java helperは内部adapterの所有補助でありHTTP/CLI/ENVから資源能力を追加しない。

OwnedTransferDirectoryのstateLock等のJava wrapperはnative open前に確保する。openRoot(DirectoryCalls)を既openRoot能力の同一FD wrapperとして追加し、設定pathのopenがroot '/'を拒否する既制約は変更しない。openExistingDate/Childはwrapper確保→open→descriptor格納→返却、open/openDate/createPrivateChild/publishChild等のowned scopeは上記factory入口で取得から保護する。EntryHandleもEntryOpenのprimitive int取得前にobject確保し、取得後boxingやcallback確保をしない。既NOFOLLOW/segment/名前/CREATE_NEW/0640・0600/0700/同期/非上書き・rename後不確実性/descriptor消費前close・借用path非exportを維持、転送は新wrapper構築成功後だけ元descriptor=-1とする。

まずRoot ELF/待機の同経路と共通directoryの取得siteを是正する。全Main68file237 ResourceScope.use候補は各外側保護域/既所有者/transfer/borrowを個別判定し、修正又は非該当根拠と再発防止PTまで記録する。候補検索だけでYKT1178をcloseしない。元e8ec全体/旧native/原本/成功・失敗証拠は保全、新sourceへ旧成功を輸入せず、未是正sourceは配備しない。

SSC063継続/PG171・BUG195/YKT154: 同じIO close優先順位をDurableRecordFiles.readFile/write/force、InspectorEnvironmentReader.readFile、InspectorEnvironmentPublisher.writeNew/forceExisting、ExistingFileAccess.walkのchannel/childへ適用する。nullable IO resourceは従来の固定IO拒否（ExistingFileAccessのnonnull channelは境界NPE拒否）を所有受領前に実施し、callbackの値/IO順/サイズ/metadata/partial保全/借用root・非公開能力を変更しない。8所有scopeを既知IO＋未知cleanup/同一未知body＋cleanupの各Runtime/NPE/Error3型で独立再試験する。Directory/Process/JDBC等の残候補は別段で未完了を維持する。IO型と回復責務を変える一般frameworkや追加coverage除外は採用しない。

SSC063/PG170・BUG195/YKT154（先行6e59c153）: resource bodyとcloseの複合は標準TWR self-suppressionへ依存せず明示的に解決する。Storage.ResourceScope.use(Closeable,Action<T>)は受領したcloseを全経路で1回だけ実施し、body成功後のclose成功まで返さない。close/action nullは所有受領前に拒否。generic callbackの明示nullable結果は透過し、呼出側の既存null契約を変えない。

bodyが未知Runtime/Errorの場合は同じprimaryを保持し、closeがIO/Runtime/Errorで失敗しても新しい固定StorageIoExceptionをsuppressed1件だけ追加する（同一throwable再送を含む）。bodyが既知IOExceptionでcloseが未知Runtime/Errorならcloseの元unknownを優先する。既知IO同士なら非成功UNAVAILABLE、bodyだけのStorageIoExceptionはsuppressedなしのreasonを保ちraw causeを除去、それ以外のIOはUNAVAILABLE。成功bodyのunknown closeはそのまま非正常伝播、IO closeは固定失敗。catch NPEによる正常復帰、close再試行、resource以外の所有物のcloseを禁止する。nested scopeも内側から順に全closeを行い、この同じ規則でprimaryを保つ。

直接適用はOwnedTransferDirectoryのopen/openDate/withEntry、LinuxFileLockのowned descriptor、BackupArtifactVerifierのchild/rebound/entry経由/channel/names、BackupManifestReaderのchild/rebound/entry経由/channel。根元ArenaはJDK実体で外部close portがなく、既存所有・close回帰を維持する。これらのI/O順・file/DB/OS操作と正常結果は変更しない。未知provider自身の例外は元identityを保持するが、そこからraw messageを監査/UIへ出してよいという意味ではない。

InspectorUnitProbeは専用の同等scopeでstdio/QueryProcessを管理し、既知StopGate/IOException/InterruptedExceptionとunknown Runtime/Errorを区別する。primary unknown＋cleanup失敗は固定StopGate(COMMAND_FAILURE) secondary、primary既知＋cleanup unknownは元unknown、既知同士は元停止理由を外側でredact。早期stdin/stderr closeは既存once状態を維持し、未取得streamをcloseしない。取得済output byteはclose失敗を含む全異常終了で消去し、途中配列を正常結果へ返さない。systemctl command/timeout/TERM/環境と既存Test oracleを不変更。

018027/028・PT-OPS-RSCOPE-001～008が共通scope単体（NULL/nullable/全IO理由・未知3型/同一・別例外/close1回/並行・nested）。既存BAT204/235、UNIT015、Storage保持inode/lockの追加反例と正式全reactorで各呼出箇所を検証する。全line/method/class/branch100%、新たな解析抑制/coverage除外なし。未修正箇所を検索済みだけで横展開完了にしない。

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
| `MediaQueryService.describeAudio/describeVideo/describeMusic` | actor context、media type/logical ID、mode | 検証済metadata descriptor | API側のrole/DB metadata/manifest検証。311/323のAPI責務名へ統一 |
| `MediaRangeService.deliver` | HTTP Range、descriptor、response | void/HTTP status | Web側の要求対応・path・size・MIME再検証、stream。311のWeb責務名へ統一 |
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

SSC-049/PG-D-153（先行67148c13）: shared storageへ保守file adapter専用のprivate能力を追加する。DirectoryCalls.createPrivateFileは同じopenat CREATE_NEW/NOFOLLOW/CLOEXECでmode0600を要求し、既存createFile0640は不変。未対応実装のdefaultは無操作UNAVAILABLEで拒否する。OwnedTransferDirectory.createPrivatePart(UUID,callback)は生成時点のinodeを保持し全終了close。publishAs(UUID,単一名)はUUID.partから同directoryの単一targetへ既存RENAME_NOREPLACE、その後directory fsync。unlinkEntry(単一名)はcallerが証明済みのentryだけをunlinkat→directory fsync。空/`.`/`..`/slash/NUL/null・closed rootは無操作拒否。root/階層の削除はなく、既存target衝突時はpart/targetを保持する。rename/unlink後のfsync/close失敗は不確定な非成功で、逆操作や他file削除で隠さない。

上記能力自体はfileのowner/ACL/expected runのpolicyではない。callerが保持inode属性/同run byte・namespace/OS排他・子停止を確認してから使う。通常Transferの0640/.readyとWeb read-only、従来no-replaceの契約は変更しない。作成した0600 fileもumask/ACL/所有を上位で再検証し、不明既存fileの自動chmod・truncate・削除をしない。実nativeと公開SPI faultのPT-OPS-PFILE-001～008で確認し、runtime publisher完了とは分離する。

SSC-021でReaderも同じ低位能力を共有する。Writerのmkdir/非上書きatomic公開はJava25の公開FFMからLinux libcのopenat/mkdirat/renameat2/unlinkat/fsync/closeを呼ぶ限定portで実現する。Preview、JDK internal API、private FDのreflection、shell subprocessを使用しない。Rootは`/`から全segmentをO_DIRECTORY/O_NOFOLLOW/O_CLOEXECで相対openし、起動時の所有者/permission/非重複検査後も自分で取得したdirectory FDを保持する。

日付directory作成とUUID entry操作はそのFD相対だけで行う。FileChannelでのCREATE_NEW/read/attribute取得に必要なpathは、自processが保持中のFDを指すkernel procfs `/proc/self/fd/<owned fd>/<validated generated name>`に限定する。利用者pathや置換可能な元root pathを再解決しない。FDは操作中close/reuseされない寿命管理を行い、close失敗時に同じ番号を再closeしない。File名の最終symlinkは常にNOFOLLOWで拒否し、nlink=1等の既存検査を省略しない。

Linux/glibc、native access、procfs、必要attribute、directory fsync、同filesystemのRENAME_NOREPLACEが揃わない場合はreadiness false。未検証network filesystemは使用しない。Root作成/chmod、check-then-move、hard-link公開、通常renameへのfallbackは禁止する。JVM設定と実機適合試験は342/354へ追跡する。

Writerのsize/hash再検証では、名前の事前検査とFileChannel openの間の差替えを避けるため、FD相対openat(O_PATH/O_NOFOLLOW/O_CLOEXEC)でentry inodeを先に保持する。O_PATHはsymlink自身も保持できるので、own FDのprocfs magic link経由で得たUnix属性の通常file0640・owner/group・nlink=1・sizeを確認するまでread channelを開かない。確認後も同じ保持inodeのprocfs handleからだけreadし、元entry名は再解決しない。Symlink/device/socketは属性段階で拒否する。Scoped entry FDはcallback完了/例外で必ずcloseし、複合I/O/close故障は外部pathを含まない一時障害へ再構成する。

SSC-019/PG-D-059補足: partの初回作成もopenatのO_CREAT/O_EXCL/O_WRONLY/O_NOFOLLOW/O_CLOEXEC・0640で行い、CREATE_NEW時点からそのinode FDを保持する。生成後の名前再解決からmode/groupの変更先や書込み先を決めない。FileChannelは保持FDのprocfs capabilityから開き、channel/native FDの双方を明示closeする。全件byte配列を準備せず、PayloadCodecの単一record encodeを共用し、全件sequence検証と1件ずつの事前byte検査後、4,800byteずつ再encode/writeする。Data/headerを捏造してfile recordをencodeしない。

### 7.4 起動時の診断専用probe（SSC-022）

SSC-162/BUG519：RW検査は保持FDの現在mountについて既存LinuxInodeSecurity/statvfs ST_RDONLYで確認する。ProtectSystem=strict内のTransfer限定RW bindをcanonical FileStore readonlyで誤拒否しない。ext4/SDS・所有/modeと以下の実probeは必須のまま。保持mount readonly/観測失敗は起動拒否し、Files.isWritableだけの代用やsandbox緩和はしない。A06-MOUNT001/002と実通常API経路で検証する。

業務producer/HTTP受付前かつ他writer/batch停止のexclusive startup区間で、実Transfer filesystemの新規group/mode設定、file force、directory fsync、atomic no-replaceを検査する。Rootは自動作成/chmodしない。診断日付はJST正規date、新規dateだけをSSC-020の属性へ確定し、既存dateは検査だけとする。

CSPRNG UUIDの診断partをCREATE_NEWで保持し、秘密を含まない4800byte固定pattern Aを書いてforce/属性/独立hashを検証、readyへnative no-replace公開する。同UUIDの新しい診断partに異なるpattern Bを書き、readyへの二度目の公開がCOLLISIONとなりA/B双方のbyteが保たれることを検査する。通常rename/置換へのfallbackはない。Probeのfileは業務結果ではなく、descriptor/Inbox/業務message/HTTPへ返さない。

ProbeはCREATE_NEW成功で所有を確認したpartと、公開成功を確認した**自分の診断readyだけ**をその保持dateから清掃し、directory fsyncする。Ready清掃前に保持inodeの属性とdiagnostic A hashを再確認し、変質/検査不能なら保全する。既存衝突先、所有不明entry、公開結果不確定のreadyは削除しない。清掃失敗/close失敗/不確定公開は起動不合格とし、全体scan/ready成功へ算入しない。残った診断entryは既存の次回朝清掃/運用調査対象とする。新規empty dateは無断削除しない。

この限定された起動診断の清掃を、通常writer/readerや業務ready削除へ流用しない。通常のlarge-result lifecycleは従来どおり次回朝batchへ委ねる。Probe成功後の完全scanだけで容量を初期化し、single-instance/exclusive保証・full root検査・service readinessへの結線を別途検証する。

### 7.5 既存子directoryの非上書き公開（SSC065/PG176）

先行d744fb57。OwnedTransferDirectory.publishChild(String pending,String ready)は借用した単一親capability内の既存directoryだけを公開する。両名を既存単一segment規則で検証し、同名はIllegalArgumentException、NULLは境界NPE、closed親はUNAVAILABLE。入力検査前のnative操作はしない。backup正規名/owner/ACL/device/内容のpolicyはbatch caller側に残し、Storageへ業務型依存を入れない。

親のprivate lock内でpendingを既存O_DIRECTORY/NOFOLLOW/CLOEXECで保持し、既存DirectoryCalls.publish（renameat2 RENAME_NOREPLACE）→親sync→所有child closeの順で終了する。mkdir/file作成/通常renameへのfallback/chmod/chown/unlinkはしない。parentはcloseせず、child closeは成功・失敗とも一度だけ。資源複合はResourceScope/SSC063の安全なprimary優先順位を使用する。

missing source、非directory/symlink sourceは非成功、targetがdirectory/file/symlinkのいずれでも衝突は保全。rename後のsync/close失敗では公開済targetを巻き戻さず、失敗前のpart/targetも自動削除しない。借用親の元pathが置換されても保持FD側だけを操作する。

この操作はcallerの連続排他・actor停止・元inode/確定後inode照合の代替ではない。openしたsourceとrename時のnamespaceが敵対actorによって差替えられないことはcaller責務で、openDirectory成功だけで真正なbundleやbackup完了を認定しない。batchの全file force/子sync/確定後Reader＋ArtifactVerifier/DB pair確定はSS341の別必須段。

PT-OPS-PDIR-001～008/018029で実Linux inode/no-replace/sync、入力全不正・close/不確定結果・compound・並行とborrowed ownershipを検証する。既存0640file/0600private file/Transfer公開のoracleは変更しない。

### 7.6 private子directoryの新規作成（SSC068/PG186）

backup pending用に既存0750日付directoryとは別の0700/new-only能力を設ける。DirectoryCalls.createPrivateDirectoryは未対応adapterではmutationせずUNAVAILABLE、Linuxは保持parent FDに対するmkdirat(mode0700)を使用する。umaskは権限を縮小し得るためcallerがmetadataを確認し、chmod/chownで補修しない。既存nameはdirectory/file/symlinkを問わずcollision、既存openへfallbackしない。

OwnedTransferDirectory.createPrivateChildは単一segment/null/closed検査後、private lock内でmkdir→NOFOLLOW child open→child fsync→parent fsyncを行い、全成功時だけ独立所有child FDを返す。失敗時は取得済child FDを一度だけ消費し、部分生成directoryは消さず保全する。rootは借用のまま。既知/未知close複合の順位はResourceScopeに従いself-suppressionを作らない。

この低位能力はmkdir/open間のnamespace真正性、backup owner、root admissionを証明しない。callerが専用backup OS UID/GID、親排他/他actor停止、parent/rootとの同device、inode/owner/mode/ACL前後一致を確認する。rootで生成してbackup所有を装うこと、既存directory修復、partialの無条件再利用は禁止。archive生成・backup確定・7世代・NAS durabilityは別の上位責務であり、ここだけのPT成功で完了としない。関連RD BAK/BKO/OPS009、UI251、SS341§6.1/343§5.3、018031/032・PT-OPS-CDIR-001～008。

## 8. Media認可・descriptor

1. Browser requestごとにWeb HTTP session、CSRF不要のGET、認証contextの有効性をAPIで検証。
2. APIはIF-009/012/016でlogical ID、media type、inline/download modeを受け、DB metadataとmanifestを参照。
3. Descriptor DATAにlogical ID、storage relative path、safe file name、byte size、SHA-256、allowlisted MIME、modeを設定する。
   Message/correlation IDは共通headerに設定し、承認済みMQ経路でWebへ返す。
4. Webはdescriptorと要求URLのlogical ID/type/modeを再照合、secure open後のsize、必要時hashを検証。
5. Authorization済みchannelだけをstreamし、pathはBrowser/HTML/HTTP header/logへ出さない。

DescriptorはHTTP session cacheの権限正本にせず、各GETでAPIへ照会する。ID不存在・非scopeは404、
API/MQ/file integrity障害は503。内部理由をBrowserへ区別表示しない。

SSC-030: 旧記載のsigned/署名/MQ HMAC検証済responseは要求Inbox fingerprintと応答検証の混同であり、独立した応答MAC/signatureを意味しない。RD MQ-020、UI231 §5/10、232 header、235 MEDIA1024、237 §8を正本とする。Operation HMAC keyはSS343どおりAPIだけが保持し、Webへ配布しない。Wire/property/credentialへ未定義の署名field/keyを追加しない。APIの全Request HMAC・暗号化snapshotの完全性検査はSS324の既存契約を維持する。

Webはloopback Brokerの認証・Address別role（reply送信はAPI）、JMS/body属性一致と共通codec検証、待機correlation/deadlineを既存MQ層で保証する。その上でMediaResponseDecoderが元の3 descriptor要求を検証し、対応response layout、request Message IDへのcorrelation、同一認証context（constant-time比較）、全body長・result profile、成功時のtype/logical ID/disposition・path/MIMEを再照合する。Error profileはdescriptorを生成せず元result codeを維持する。不一致はfileを開かず503相当の安全な検証失敗とする。これらは各GETのAPI認証/manifest確認、Web物理検証・起動権限の代替ではない。

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

SSC118実装補足：日付は実在するcanonical yyyyMMdd、UUIDは小文字canonicalを要求する。mtimeがcutoffと等しいentryは境界保全し、strictly-beforeだけ対象。保持root/日付はAPI UID・schubert-web GID・0750、fileは同UID/GID・0640/regular/nlink1・同device・ACLなし/localRWを前後実再観測する。内容sizeが0又は48MB以上でも古い正規regularの清掃を妨げず、生成側のrecord-length制約は清掃へ流用しない。不明entryは保全件数としてWARNING（個別path出力なし）。根本gate/親guard不明は全体非成功、確認不能をemptyへ補完しない。空の正規日付だけ親FD＋single-segment unlinkat(AT_REMOVEDIR)/fsyncで削除し、host read-only adapter・recursive API・configured root削除は使用しない。既存batch_runsのtarget/success/failure/byteと固定reasonを保存し、保全件数は独立集計証跡へ残す（新DDLなし）。

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

## SSC-439 純例外policyの非instance namespace責務（2026-11-16）

MorningSqlFailuresとJdbcResourceFailuresは例外優先順位だけを扱う非instanceのpackage-private static namespaceとし、final class宣言とprivate空constructorだけをstatic-only package-private interfaceへ置き換える。全static method名・descriptor・注釈・bodyを逆展開byte exactで保持し、既知SQL/IO/catalog判定・null契約・primary/secondary優先・suppressed固定診断・Error cause/suppressed/SQLnextのidentity付き有限BFS順・閉じたredactionを変更0。新instance/abstract method/field/portを導入せず、型のpackage可視性は不変。型kindがclassからinterfaceになるため旧Methodref callerbinary混用は禁止、全十sourcecallerのpath/hash/owner/static呼出箇所を保存、将来releaseは全caller/fullmoduleをfresh再compileする。今回は実JDBC-DBやHOLD依存の全callerをcompile/実行せず、二純helperを呼ぶ元Morning12/JDBC8を全source byte exact保持し、新たな独立StorageReason固定3値のvalues/valueOf/ordinal/defensivearray/未知空大小文字/null/固定Storage診断契約1だけを加え、新source同一run21で四Main五Codeclassの全分岐・raw四counter100/RootNullAway/全静的/currentCRC-initXMLを検証する。StorageIoExceptionのproduction bodyは変更0、実DB接続/driver/transaction/credential/Root2Actual4/鍵/VM/native/aru/permit等のHOLDを代替せず、旧二sourceのraw不足や成功は歴史証拠で別保持する。BUG3087/YKT2559/YKT2431、SS332333354。private反射/空instance生成/除外/到達不能扱いで未網羅を埋めない。内部責務の詳細補足のみでRD/UI/QA/承認DIF変更不要、全caller/451/正式受入は未達条件が閉じるまで更新しない。

状態:設計確定・main反映前、PG/PT/全caller/正式未完。

## SSC-440 public純utilityの非instance責務と局所pattern（2026-11-16）

ResourceScope・InspectorRunEnvironment・InspectorStaticEnvironmentの非instance責務をpublic static-only interfaceで表す。publicfinal宣言/空privatectorを除去し、既static methodとResourceScopeの四nested functionalinterface、MAXIMUM_BYTES定数は既public descriptor/型注釈/可視性/値を保持、interfaceで暗黙publicになる冗長modifierだけを除く。ResourceScope/RunEnvironment全method bodyは逆展開formatted exact。StaticEnvironmentのprivate int二値・Pattern二式はrequireValidのmethodlocal finalへ移し、既regex文字列/判定/ループ/固定例外は識別子置換を逆展開して保持する。private Patternをpublicfieldへ公開せず新port/設定/権限/instanceを導入0、MAXIMUM_BYTES65848/最大names65536/TCP65535/ASCII sourcegrammar/version1-16/重複拒否/NN/UTF8規則を変更0。Patternは各呼出の既NN-サイズ検査前に元の順で構築し非共有、型初期化cacheから局所へ移るallocation差を記録、fatalErrorをcatch/正常化せず実heapOOMEやIT性能は未測定として後続へ残す。class→interfaceの旧Methodref binary混用は禁止、全Main参照sourceのpath/hash/owner/行を列挙し全caller/fullmodule fresh再compileを将来release条件にする。今回は元ResourceScope8/Factory18/RunEnv4/StaticEnv6の全36Test source/独立期待byte exactを保持し、既StorageIoException/Reasonの公開catalog・有限identity BFSを独立新2、BatchRun全NN・年1..9999・µs拒否/recordを新1で補い、新source同run全39/freshMain5Root/全静的/physical10中Code6と自然Code0四interface/CRC-initXML/raw必須四100で確認。無意味instance/私有反射/除外/到達不能扱いをしない。callbackの取得-返却-移管-一回解放/IO対unknown優先/固定suppression、runfile/静的fileのbytesと全診断を不変更。実FD/VM/DB/JMS/credential/鍵/Root2Actual4/aru/HOLDや全callerを代替0、旧Core5aの無関係Data59の確認再演やoldexec合算0。内部詳細の範囲でRD/UI/QA/DIF変更不要、BUG3090/YKT2562/YKT2431、SS333343354、全451/全caller/正式未受入を維持する。

状態:設計確定・main反映前、PG/PT/全caller/正式未完。

## SSC-443 PathSyntax非instance字句検査と二callerの現source契約（2026-11-16）

BUG3107/YKT2579のうちPathSyntax責務だけをpackage-private static-only interfaceへ整理し空privatectorを除去する。二私有Patternの正規表現文字列を完全保持し、各利用method内のlocal Patternへ移す。interface fieldの暗黙public化で私有cacheを外部公開することは禁止、型はpackage-privateのまま・三static methodの暗黙public内部flag差を記録する。旧静的cacheからmethod毎compileへallocation timingが変わる内部差を明記し、PG/PTで性能又はIT/STを承認しない。先頭slash/backslash/ASCII drive prefix・slash/backslash区切り親segment・ISO control判定の順序/short-circuit/診断/Unicode処理を保持し、Pattern変数名/宣言scopeと型/ctor以外の実bodyを逆展開で一致証明する。二実Main caller RelativePath/DisplayPathはstrictUTF16検査を含む現sourceを不変のままfreshcompileしInterfaceMethodrefと両factory実行を確認、旧helper binaryと新callerの混用禁止。二path公開ABI/正規化/length/segment/equals/hash/redactedtextは不変。独立new3通常PTで境界255/256segment・512/513 UTF8total・空/絶対/drive/root/末尾separator/空dotdotsegment/control・NFC/多byte・同値異値null異型/独立JavaString hash/実HashMapを確認、既PathUnicodeBoundaryTest全2をbyte不変で必要回帰する。三Main/三physicalCode/currentCRC-initXML/freshRoot/static/同run全5/raw四100が限定条件。ProtocolValidatorの別空ctorは未修正OPENとして残し、この範囲へ成功加算しない。元Protocol120/124/accepted17全面requal/旧exec合算0、privateReflection/無意味instance/除外禁止。SS323333354914を製造前にmainへ反映、RD/UI/DIF変更不要。Root2Actual4/DB鍵nativeVMaru等HOLDと全451/正式未受入を維持する。

状態:設計確定・main反映前、製造/通常PT5/全module/正式未完。

## SSC-451 Protocolの非instance namespaceと明示dispatch（2026-11-17）

BUG3111/YKT2583・YKT2647の残る四空privatector/17switchを詳細化する。FieldCodec/LargeResultRecordCodec/MediaDescriptorValidator/PayloadSemanticValidatorをpublic static-only interfaceとし、全public static methodの名前・引数・戻り値・例外・null契約を保持する。private static helperはprivateのまま、既private定数と不変Pattern/Map/Setは同一packageの非公開companion interfaceへ移す。companion型は公開namespaceへextendsせず、publicfieldを公開namespaceに増やさない。class初期化による不変cacheの一回生成・安全公開、matcher毎call分離を維持し、空instance/guard呼出/private反射でcoverageを稼がない。public型kindと呼出constant-poolのInterfaceMethodref差はJava内部ABI変更として記録し、旧class/helper/callerの混在禁止。Protocol全Mainと参照477Mainを当sourceでfreshcompileする。四held型を含むAPI/Webの全再構築はQA056成立後の終了依存として残し、当局所結果を全六module認定にしない。

PayloadCodec四、MediaDescriptorValidator二、LayoutFieldCatalog七、file.ContentDisposition一、PayloadSemanticValidator三の計17switchを、selectorの一回評価とnonnull契約を保つ明示比較へ置換する。Stringは同じcase literalのequals/同じ順序/default body、closed enumは既定数をif/elseで対応し新enum追加時は設計・全対応試験の変更を必須とする。case body/固定diagnostic/先行後続処理/64layout389field/69型/golden byteを保持する。javac専用hash/ordinal map/defaultを生成不要にする責務整理で、仮想enum注入/到達不能扱い/coverage除外/旧exec合算を行わない。変更前17case表と逆展開比較、全公開API差/物理class増減・debug差を記録する。

原35Testsource152と独立TSV/期待値は保持し、namespace四の公開型・publicstatic API集合/非instance契約を新四Testで確認、private memberアクセス無し。必要な変更後whole156を同sourceで一回実施し、全actualCodeのline/method/class/branch100、全例外・境界、NullAway/PMD/Checkstyle/format/SpotBugs・XML/CRC/init/独立postを要求する。新不足は修正前BUG起票、未達を合格へ換算しない。RD/UI/DIF/外部利用者挙動変更不要。SS322323333354/914をPG前にmainへ反映する。全Root/実DB/JMS/VM/native/認証/鍵/intent等HOLD・QA051/056/057・451・正式1964/53・元17/190/工数nullを維持する。

状態:設計確定・main反映前、製造/PT156・全六module・正式未完。変更前source db668dd02b/製品Core0a2b32d0、予定.50/1.80/4.50 cap5、費用F03一回、他program論理owner参照は二重課金0。

## SSC-452 digest生成の内部namespace可視性（2026-11-17）

BUG3182/YKT2650。SSC451のclass→interfaceではpackage-private static methodを同じ可視性で保持できないため、LargeResultRecordCodec.digestFor(String)をpackage-private companion interface LargeResultDigestのstatic digestFor(String)へ移す。公開facadeはwrite/decodeだけ、private sha256Digestが同じliteral SHA-256で内部関数を呼ぶ。LargeResultDigestは非公開型で外部公開APIを増やさず、元digestForのbody/NoSuchAlgorithmException→同IllegalStateException/診断/cause/null挙動を保持する。公開facadeの追加digestForはBUGとして不受理。元LargeResultRecordCodecTestのnegative一箇所は呼出型のみLargeResultDigestへ変更し、Test ID/入力not-an-algorithm/期待例外・cause全assertionは保持する。期待値をproductionから生成しない。interface暗黙publicの内部methodは非公開型内の境界に閉じ、空constructor/private反射/ダミーinstanceを作らない。新Mainは169・physical176（新helper一つ）、既152＋新namespace四=156を当sourceで一回実行し、全actualCode/NullAway/PMD/CS/format/SB/全publicABIを確認する。四namespace全method/172共通classのpublic surfaceを再照合、旧public型kind四差以外の公開method/field差0を要求し、全caller480→481Mainをfreshcompileする。旧失敗Core3b275/PG37624・compile失敗/原証拠を保全し成功へ合算0。RD/UI/DIF変更不要、SS322323333354914をPG前にmainへ反映。全HOLD/451/正式1964-53・17/190・工数null維持。

状態:設計確定、main反映前、製造/PT/全六module/正式未完。元SSC451群開始見積.5/1.8/4.5cap5は保持、当見落しの手戻りを内訳へ記録し新規原受入に加算0。

### SSC451/452 main反映と製造・PT限定結果（2026-11-17）

設計はPR415/416・main23aea46eへ反映済み。製品Corea013a6d676454082de3c59bc199e87f37fefe159／Unitf08897ce8742091dbf1c7575e25780d31b30c089、PG37652当156件は成功156・F/E/S/notrun0。169Main/176physical・162Code/1432method、単一execの独立XML/CRC/init及び未filter raw3638行/1432method/162class/1078branch/20347instruction全miss0、自然NoCode14は除外せず0/0 N/A。原152の独立期待値は保持（digest negative一箇所の呼出型と整形だけ逆変換SHA exact）、公開namespace四を追加。全literal/initializer645一致・172共通public ABIは承認済四型kind差以外同一、Root四module481Main・Protocol176byte一致、NullAway/SpotBugs176/CS/format0、PMD46は元個別anchor・適用根拠を照合し未分類0。新37指摘を無条件非該当とせず是正、元失敗を保持した。MIME内部helperはnullable-returnを明記し元reject結果を保持するPG-D1176。

公開証跡: [PG37674 Protocol品質結合](https://github.com/NakajimaMotoharu/schubert_NK_project/blob/2009b097ce44a1374219d53b92e9526c3186ca57/evidence/01_PT/018_NK-OPS-001/evidence/PG37674-ssc451452-protocol-module-criteria-return-v1/manifest.json)。BUG3111/YKT2583のProtocol全raw不足は閉鎖。全六module、API/Web QA056、実Root/DB/JMS/VM/native/鍵/権限等HOLD、451全体、正式1964PT/53scope・元17/190・工数nullは維持し、本限定結果で全PGPT/ITSTの完了を宣言しない。未受入実装/工具/証跡はmainへ混入せず、実施branchの公開証跡を参照する。


## SSC-461 Throwableの追加辺を受け取る純graph

StorageIoExceptionにThrowableの追加辺を供給するオーバーロードを置く。追加関数はnonnull、戻りnullは追加辺なし。未訪問の非Error nodeだけで一度評価し、既causeと順序付きsuppressedの後ろへ積む。直接Errorのidentity、先行辺による優先、有限帰還を維持。FileOperation内を含む既1引数入口の結果は移管期間中維持し、全caller証明までこれを削除しない。
