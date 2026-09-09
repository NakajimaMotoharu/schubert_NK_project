# NK-DAT-001 検査process内部接続 単体テスト仕様書

## 1. 対象・独立oracle

InspectorProcess.execute、private鍵所有集合。RD DAT-009/OPS-009/MQ-008、UI212/241/251、SS324 §12/341 §7.3/343 §6.5、QA-046/UIC-006/SSC-049/PG-D-135。
既存公認sourceのcurrent/previous形式を独立ASCII/Base64で構築し、既存test fixtureの独立JCE保存wireと実PostgreSQLのSQL後条件を使用する。Production methodからexpectedを作らない。鍵値・raw context・DB dumpは保存しない。

| Test ID | method | 入力・操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-141 | currentOnlyAndEmptyScan | current2個/previous不在、空Inbox。0/END、DB進捗0/0/0、全material closed |
| PT-DB-INBOX-142 | previousKeysAndAtomicDeletion | current/previous4鍵、旧response世代の独立暗号Login error。1削除、progress1/1/0/END、旧鍵利用成功 |
| PT-DB-INBOX-143 | unverifiableRowsWarnWithoutMutation | 未知鍵/破損/Question未対応行。10、行を保持しprotected加算、業務表不変 |
| PT-DB-INBOX-144 | missingAndFaultedKeyLoads | current欠落と4各load失敗。DB未access、以前の全material close、previous不在だけ許可 |
| PT-DB-INBOX-145 | versionsAndPurposeSeparation | 同purpose version重複/全4cross-purpose鍵組合せ同値は拒否。purpose間同version名/別鍵は許可 |
| PT-DB-INBOX-146 | closedMaterialFailsBeforeDatabase | 各位置のclosed materialからcopy失敗。固定設定例外、DB0、所有済全close |
| PT-DB-INBOX-147 | timeoutsAndInterruptionCloseKeys | nano差分30分/割込前後、50/flag保持、全material close、未処理を成功化しない |
| PT-DB-INBOX-148 | databaseFailureAndResume | connection/close/commit成否不明。50とDB checkpointを照合、新service同run再開、二重削除なし |
| PT-DB-INBOX-149 | singleUseAndConcurrentContenders | 1objectへの100並行実行は1winner/99拒否、鍵4loadだけ。2回目別runも拒否 |
| PT-DB-INBOX-150 | constructorAndSnapshotContracts | null/空/未知/要素null・入力集合事後変更。constructor拒否または独立snapshot維持 |
| PT-DB-INBOX-151 | ownedCopiesAndMaterialLifetimes | DB処理時だけmaterial live、成功/想定外clock例外後全closed、source所有raw input不変、所有copy消去のfinally source review |
| PT-DB-INBOX-152 | publicLoaderFailureAndRedaction | 実public readerの権限不適合root、固定cause-free失敗/DB0、実JDK時計のpublic binding、borrowed rootの所有維持 |

## 2. 実行・境界・証跡

Java25/Maven/PG18は421、root clean verifyと018 collectorは451/458に従う。全line/method/class/branch100%、NullAway/Spotless/SpotBugs0。失敗/skipped/flaky/not-runは合格外。
構成例外はmainの70分類前の例外、0/10/50も内部結果のみ。Linux本番systemd起動、DB password配布、親backup/OS lock、Question7参照、IT/STは未検証。
実行command・日時・branch・対象commit・環境・終了code・coverage・Test ID・BUG/SSC・hashは038とevidence/inspector-process/manifest.jsonへ確定する。実装/実行前であり合格なし。
