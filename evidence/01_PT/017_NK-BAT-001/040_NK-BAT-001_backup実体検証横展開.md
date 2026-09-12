# NK-BAT-001 backup実体検証横展開・独立試験監査

PG166/SSC059、BAK/BKO/UI251/SS341 §6.5・343 §5.3。現状は探索再試験成功、正式全reactor認定待ち。実生成/pg_restore/tar/age妥当性/信頼されたDB binding/7世代管理/親全体/IT/STの完了を主張しない。

## 1. 修正前起票と全対象

| 台帳 | 検出・原因 | 是正と再発防止 | 横展開の全対象・非該当根拠 |
|---|---|---|---|
| BUG184/YKT145、先行d7317d06 | compile1で未参照TWR owned変数2警告、-Werror失敗 | SafeClose<T>から本体resourceを利用し所有関係を型で表現、抑止/無意味参照なし | BackupArtifactVerifier names/read両箇所。OwnedTransferDirectory EntryHandle・Inspector resource/既存try wrapperは実使用または明示closeで正式09 compile成功。全Production SafeClose/new wrapper/try resourceを検索し、本修正以外の未使用警告はなし。全reactor compile再確認を要す |
| BUG185、先行2c041167 | explore2でFileTime import欠落、PT compile不可 | java.nio.file.attribute.FileTime明示import、期待値不変 | 新artifact test内唯一のFileTime使用。別subpackageをwildcardへ推測追加しない。全Batch test compileを再実行、共通原因追加なし |
| BUG186/YKT146、先行cc6639f1 | explore3、最終207番clock内で割込を立てると成功。clock前だけの判定が原因 | clock後に割込再確認、flagを消さず非成功。全207位置のBAT205に加え既存3classにも終端clock注入 | 下表の全4classを修正。clock以外の巨大IO強制取消・OS signalの保証を捏造しない |

| YKT146対象 | 修正／非該当の具体理由 | 再試験・独立期待値 |
|---|---|---|
| BackupArtifactVerifier.guard | clock取得後も割込チェック | BAT205、startを含む207位置すべて割込、206 timeout境界、成功禁止/flag保持/全資源解放/file不変 |
| LogCleanupService.check | 同構造を修正 | BAT024 interruptsRemainSet、空runのstart/preflight/post-commit全3位置。最終だけ既commit進捗0/0/0/true、borrowed connection非close/autoCommit復元 |
| StepCleanupService.check | 同構造を修正 | BAT174 timeoutInterruptAndClockWrap、start/preflight/2chunk前後の全6位置。1..3は未削除0、4..6は既commit1/1/0をRUNNINGに保持。誤成功/勝手な再実行なし |
| InspectionRunExecutor.stopReason | 同構造を修正 | DB-INBOX-101 interruptionRemainsVisible、空run3位置すべてINTERRUPTED/exit50。前2はlast空/DB進捗0件、最終は確認済0/0/0/true/DB1件、flag保持 |
| InspectorProcess | LongSupplierを自身で読まずInspectionRunExecutorへ渡すだけ | 上記executor修正のconsumer、既存InspectorProcessTestを全reactor回帰 |
| InspectorApplication、ApplicationStopGate、InspectorLockHandoff、ConfigurationGroupResolver | 割込gateはあるがclock読取を挟まない | 同causeのclock後取り逃しなし、各既存全PT回帰 |
| RunReferenceRepository、InspectionSummaryRepository | 割込gate前後はJDBCでclockなし | 同cause非該当、既存JDBC資源/割込PT全回帰 |
| MaintenanceRunFiles、DurableRecordFiles、InspectorEnvironmentReader/Files/Publisher | 保持inode操作境界に割込gate、LongSupplier/nanoTime読取なし | 同cause非該当、各既存IO/割込/並行PT全回帰 |
| 他全Production getAsLong | OptionalLongからIDを取り出す値操作（InboxResultReference/JdbcInboxCoordinator/InboxRequest/ResponseSnapshotIdentity/LogoutInboxService/AdminCommandAuthenticator） | 時間portではない。値/NULL/境界の既存全PTを維持 |

検索条件: rgで全srcのmain Javaへ isInterrupted/getAsLong/LongSupplier/nanoTime、TWR/SafeCloseを検索。単なる検索のみで完了せず全該当修正＋負例＋非該当根拠と正式回帰を記録する。

## 2. 独立file/IO oracleと資源所有

038の実装前public literal: 3file26/35/32bytes、合計93/設定67、MANIFEST964bytes/SHA256 bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370。actual返却size/hashをBAT194でliteral比較後、target/backup-artifact-traces/PT-BAT-194-digest.txtへ保存。expectedをProduction encode/hashで作らない。fixture自身も020の別固定literalで照合。

独立call mapは4file一bufferずつ、設計上の保持/再保持順から実走前に算出:

| 操作 | 回数／根拠 |
|---|---|
| attributes/ACL/readonly | 各17 = 親2 + 子3 + 4file×3 snapshot |
| openNames/iterator/closeNames | 各2、4件集合を2回確認 |
| hasNext/next | 10/8、各集合4要素と終端 |
| digest/openChannel/closeChannel | 各4 |
| size/read | 各8、各file前後size・本体1readとEOF1read |
| openDirectory/closeDirectory | 各2、子保持と親から再binding |
| openEntry/closeEntry | 各8、4file初回と最終再保持 |
| fallible位置 | 合計123、全位置発火/資源0/file不変 |
| euid/clock | 2/207、上の123には重複算入しない |
| 1byte partial read | 964+26+35+32+EOF4 = 1061、進捗0readは拒否 |

本体とchannel/list/entry/childのcloseを重ね、既知IOExceptionは固定StorageIoException（raw cause/suppressedなし）へ変換。未知Runtime/NPE/Errorは同一primaryを保持し、そのsuppressedには既知cleanupの固定診断だけ。NPEをcatchして正常化しない。borrowed rootは消費しない。返却後/失敗後に全read bufferゼロ化、channel/list/native資源0、root使用可を確認する。

4fileそれぞれ実rename差替え/同内容書換え/mtime/permissionと同device/ino/ctime最終照合、親/子差替え、集合欠落/追加/重複/NULL、全metadata型/欠落/ACL/RW/euid境界、全size/EOF/hash/canonical byte境界をBAT194..209で検証。native公開SPIのmutation操作はfail-fastとし、実0700/0600設定をfixtureで作成後、実byte/mode/ino/mtime/ctime不変を独立に比較（atime読取変化は対象外）。root UID/GID admissionのみ非特権合成port、実Linux FDと実byte操作を使用。本番root/NASはIT必須。

## 3. coverage/標準生成部分

探索4で新実装4class/23method/198line/114branchのmissed0、LogCleanupService/StepCleanupService/InspectionRunExecutorの追加割込分岐もmissed0。正式clean verifyをまだ代替しない。プロジェクト除外を追加しない。Io/Digestsのabstract署名は実行bytecodeなし。private FileClaim recordの4単純accessorと生成equals/hashCode/toStringは既存JaCoCo標準filter（037の一次資料参照）であり、業務処理・明示constructor・全snapshot/分岐は測定対象。4fieldはBAT194正系/197所有・size/201hash負例で実使用の意味を検証。内部recordは外部公開されず、生成toStringをloggingへ使わない。

020 collectorは28 Batch test class=19 Program+9 OPS、279=209+70 PTを独立照合する。019の33件＋017の1件=34負canary、15collector/38scopeは変更なし。新16methodの全欠落/重複/未知/失敗/error/skip/flaky、実digest traceの全byte改変/欠落/余分ファイルを拒否。正式認定時は同一source/実run/全scopeのhashを要求する。

## 4. 探索履歴（非正式）

- compile1: /tmp/pgpt-artifact-compile1.log、07:00:30 JST/4.130秒/exit1、BUG184。PT未実行。
- compile2: /tmp/pgpt-artifact-compile2.log、新fixture追加後のSpotless不一致、非PASS。Production障害の追加ではなく整形前check、後続formatで整形。
- explore1: /tmp/pgpt-artifact-explore1.log、07:09:15 JST終了/exit0、先行8件＋Storage8。残り8未実行で正式加算0。
- explore2: /tmp/pgpt-artifact-explore2.log、07:20:16 JST/7.479秒/exit1、BUG185でBatch testCompile失敗。
- explore3: /tmp/pgpt-artifact-explore3.log、07:21:07 JST/9.981秒/exit1、新16中15成功/1failure BUG186、成功扱い禁止。
- explore4: /tmp/pgpt-artifact-explore4.log、07:24:27 JST終了/1分13秒/exit0、Protocol4/Storage8/API8/Batch36成功。新16＋既存Log12/Step8/Inspection8を含む。選択実行の混在targetは正式source証跡として使用しない。
- 019証跡canary33件は新固定16method/実trace拒否を含みexit0。017別canary、全module static・全reactor再試験は別途記録。

環境421（Java25.0.4/Maven3.9.12/PG18.6/Flyway13.4.0/Ubuntu26.04.1）。branch dev-foundation、探索は親cc6639f1上の未commit変更。正式targetCommit/run/日時/OS/tool/command/exit/coverage/関連BUG/SSC/input/actual/hashは039と017/evidence/manifest.jsonへ確定するまで、BUG184..186/YKT145..146は未完了。
