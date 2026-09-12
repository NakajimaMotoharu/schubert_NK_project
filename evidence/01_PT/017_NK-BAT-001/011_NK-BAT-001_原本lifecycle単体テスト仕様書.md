# NK-BAT-001 原本lifecycleの単体テスト仕様書

BUG159/YKT124（先行12446fed）: BAT059のactive再利用は同byteのanchor/begin/active各forceと各directory sync（doneありは4件）を必須にする。BAT060/061/062は元anchor再同期、既beginも再同期してからactive確定。BAT064/065/077はanchor/begin/activeを再同期後done確定、active不存在でもdir syncを要求する。最初のsync failure→可視record/不存在から再開し、再同期force/syncを再度失敗させても成功しない独立負例を加える。byte/元inode/mtime不変を併記し、可視性をdurability oracleにしない。正式20260913-01には含まれない新発見として追跡する。

PG-D-158/SSC055先行36b5f85b、OPS-009/UI251/SS311/341/343 §6.15。MaintenanceRunFiles/Session・immutable再開状態・共通durable ancestor policy。実装前仕様。実file/native NOFOLLOWと合成root属性を使用、秘密実体なし。既存literal72/109/140・141byteを独立oracleとしProduction encodeからexpectedを生成しない。

| Test ID | 予定method | 入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-058 | newRunPublication | 空rootへ固定run/activation→anchor/begin/activeのliteral集合、固定値返却、停止等の外部command0 |
| PT-BAT-059 | resumeActive | 同run activeあり→同activation/cutoff、next IDを不使用、全file不変 |
| PT-BAT-060 | resumeOrphanAnchor | anchorのみ同run→begin/active追加、原本inode/byte不変 |
| PT-BAT-061 | resumePendingBegin | beginありactiveなし→同beginでactiveのみ追加、次ID不使用 |
| PT-BAT-062 | resumeCompletedHistory | 全完了run明示resume→新activation、旧done不変、新doneなし |
| PT-BAT-063 | completedActiveRecovery | active＋done→Optional completed返却、今回の実行成功へ変換せずactive保全 |
| PT-BAT-064 | completeSuccessAndWarning | 0/10両方、done公開後active退役、他履歴不変 |
| PT-BAT-065 | completionRetryAndMismatch | 同done冪等、異time/status/active拒否、done未確定でactiveなしも拒否 |
| PT-BAT-066 | noImplicitNewIdentity | 既run/使用済activation/new時pending・active、未知run resume、DB補完なし、run/cutoffを取り違えない |
| PT-BAT-067 | malformedGraphReferences | 孤立begin/done、名前ID・anchor/run/cutoff・done/activation・active不一致全分類、無変更拒否 |
| PT-BAT-068 | ambiguousPendingStates | 複数未完了/複数孤立anchor/他run pending/activeと他pending、全file保全 |
| PT-BAT-069 | inventoryUnknownAndPartial | root/runs/attempts全未知名・.part/GC marker・wrong suffix/aliasを省略せず拒否 |
| PT-BAT-070 | namespacePermissions | 6root各owner/mode/ACL/localRW・private同device、共有mount差の許容とprivate差拒否 |
| PT-BAT-071 | namespaceReplacement | fresh reopenと元6root比較、各root/name/inode差替え拒否、callback成功へしない |
| PT-BAT-072 | recordReplacementDuringScan | 各record読取/scan終端の交換・変更・途中消失/size変化、full snapshot一致 |
| PT-BAT-073 | listingAndIoFailures | DirectoryStream open/iterate/close/null/重複/別parent、各record IO全位置、owned資源0 |
| PT-BAT-074 | rootAcquisitionAndCloseFailures | 6root各open/closeとfresh reopen、callbackと複合close、取得途中も先行全close |
| PT-BAT-075 | startCrashBoundaries | anchor/begin/active公開の全途中故障、残集合と明示同run回復可能/part不明拒否を独立記録 |
| PT-BAT-076 | resumeCrashBoundaries | orphan/pending/completed各回復公開故障、原本不変・同activation/新activationの区別 |
| PT-BAT-077 | completionCrashBoundaries | done公開/active unlink/sync各故障、done前active保全・done後の再確認/冪等完了 |
| PT-BAT-078 | nullAndClosedContracts | 全constructor/操作/値/UUID supplier/callback/null result、scope後Session拒否、resource借用を漏らさない |
| PT-BAT-079 | interruptionAndRuntime | 初期/途中/最終割込保持・非root・未知runtime/NPE非正常、診断固定・副作用保全 |
| PT-BAT-080 | concurrentScopeOwnership | 同scopeの直列化、競合start1件だけ、使用中の終端待機と閉鎖後拒否、独立scopeにはOS lock前提を維持 |
| PT-BAT-081 | fixedFactoryAndReopen | 公開fixed/var factoryの実非root拒否、合成namespaceの再open再開・close後file残/独立state/redaction |

全line/method/class/branch100%、NullAway/SpotBugs/format、全reactor・collector scope/負canaryを要求。未実行/failed/flaky/skippedは非合格。各操作の全native/IO occurrenceは実装後に独立回数表を確定し、全位置へ故障注入する。spec↔method↔Test ID対応、literal入力/実output、実行日時/OS/JDK/command/branch/commit/exit/coverage/BUG/hashは012とmanifestに保存する。actualをcollectorで再生成しない。

SSどおりOS flock/親終端/DB既存ID照合・backup/step・400日GC/DB参照は別の未完了実装であり、IT/STへ移して完了にしない。実root/systemd/rebootは後続Linux実環境確認。

## 実装後に確定した独立IO・境界表

探索209件（Storage58＋Batch151）を3回実行。初回の5 branch不足はBUG162/YKT126へ先行起票、2・3回目は全4指標100%/静的解析成功。正式全reactorとは区別する。

fixtureのabsolute var pathの名前数をdとする。下表は固定6rootの取得・fresh reopen回数とread/write順を手で数えた期待値であり、productionの計測値をexpectedに転記しない。全operation観測値との一致をassertしてから、root open/closeはBAT074、残り全IO位置はBAT075～077で一箇所ずつ失敗させる。

| 操作 | attrs/ACL/filesystem/readonly各 | 6root取得回数r | openEntry e | reader n | writer w | create/publish/write各 | sync | unlink | namesNext/HasNext |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| new | 171 | 13 | 42 | 9 | 3 | 3 | 3 | 0 | 7/13 |
| active resume | 201 | 13 | 60 | 12 | 3 | 0 | 3 | 0 | 10/16 |
| active complete | 239 | 16 | 72 | 15 | 4 | 1 | 5 | 1 | 10/16 |

openDirectory=r×(d+5)、close=r×(d+6)+e、read/readSize各2n、readerClose=n、writerClose/force各w、writeSize=2w、namesOpen/Close/Iterator各6。失敗結果は固定UNAVAILABLE（cause/suppressedなし）、全owned FD/reader/writer/listing残0、残存anchorは元literalのまま。null・未知runtime・割込は正常扱いしない。

最終guardは前段を通す独立fixtureを持つ。completed対象run＋他runのorphan（activeなし/完了activeあり）、6root正常でfileだけdevice不一致、operation終了直後/全scope close直後の2箇所の割込flag、first anchor差替えのscan終端検出、全record読取後の6root時刻変化、mutation中に別の正規完了履歴を追加した場合の全graph不一致を個別assertする。Session操作中にcallbackが返っても終端はその操作を待ち、close後は同Sessionを再利用できない。16並行startは新規1件のみ。

BAT058の実anchor/begin/active、BAT064の実done0/done10と実在する相対file名集合2件、計7fileをtarget/run-lifecycle-tracesから採取。020は独立ASCII literalとexact filename集合を照合しinput/run-lifecycle・output/run-lifecycleへ保存する。完了後の集合はattemptsの同activation.begin/.doneとrunsの同run.runだけ、activeはない。019は全7fileそれぞれの欠落/NUL追加/未知fileを拒否する負canary。実outputを再encodeしない。

MaintenanceRunFiles.createの固定/varだけ、DMI_HARDCODED_ABSOLUTE_FILENAMEをEXACTでreview（owner NK-BAT-001 PG、再reviewはPG gate/OS・path・SS変更、BAT081）。coverage/null/security除外はない。既存OPSの2 factoryと合計3件をmanifestへ個別記録する。name↔ID/canonical検査はPG157共通validator、全graphのanchor↔begin↔done一致はPG158で重複なく担保する。
