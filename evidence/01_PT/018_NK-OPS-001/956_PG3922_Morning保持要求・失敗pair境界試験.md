# PG3922/3926 Morning保持要求・失敗pair境界試験

NK-BAT-001 / SS331・332・343/SSC124・451 / WBS-P017-01。Main7fff/PG3748不変更、独立fixtureのPostgreSQL18だけ使用。配備DB/VM/Root/Backup再演0。Test追加2件を既存全体へ算術加算せず、必要なPG3928/3930真正結果を待つ。

| Test ID / method | 事前条件・入力・独立期待値 | 結果 |
|---|---|---|
| PT-MDB-3920-001 / mdb3920001RetainedRequestTimeBoundariesPreserveActualRowsAndOwnedLock | cutoff2059-04-09T15:00Zの旧Backupを作り、1µs後に同runをrecover。cutoff直前/現startと同値/直後/別UUIDを拒否、旧start=cutoffは受理。各前後の全行JSON同値・別接続のadvisory取得拒否、終了後4行のstep/attempt/status/error/start/endを独立literalで検査、client/advisory0 | PG3922 actual0、全64件/FESAbortedNotRun0。Test source7c193f7d5、Main再compile0、元fixture/依存/全六jar前後hash同一 |
| PT-MDB-3924-001 / mdb3924001DifferentFailureMetricsCannotMintCanonicalFailedPairSnapshot | DB/configのFAILED件数1/2を左右入替2vector。正規失敗projectionはSS343/SSC124のFAILED,1,0,1,0のみ。異なるcommitted metricsは監査行として残るがsnapshot/observe両能力を発行しない。固定例外/原因null、全行不変/lock維持・終了後SQL各件数と資源0 | PG3926 actual0、全65件/FESAbortedNotRun0。Test source746ca85f8。選択単独Session branch327covered/58miss、全体nativeとの合算未実施 |
| PT-SELECTED-LAUNCHER-3922 | coverage libraryにlauncher無し、旧成功固定hash有りなら実行依存だけ追加。旧proof欠落/違うhash/別versionは拒否、source集合不変 | pure3、実compile lintWerror0/64・65件成功。BUG1328/YKT1094 |

初回PG3920はlauncher依存欠落でcompile11error、試験未開始、BUG1328修正前起票2586cf8a6。是正7c193f7d5でJUnit-platform-launcher1.13.4の独立旧成功hash0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564を明示固定。元3892はnative資格だけでJUnit起動しないので依存追加不要、元3734はSurefire別起動/元成功保持、旧3256は元固定launcherを持ち非該当。新3922/3926の実compilerと全件で横展開consumerを確認、検索だけ完了0。

初回PG3924の新Testは非canonical行をobserveで受理できると誤って期待し1件失敗。SS343/SSC124の固定projectionを根拠に期待値を訂正、Production変更0。TDDの新oracle誤りで既実装の仕様違反ではない。初回XML/log/selected.execと不合格を保全、65件成功へ読み替えない。

再現commandは完全PYTHONPATHで `python3 -B tools/quality/pg3922_current_abandoned_boundary.py` / `pg3926_current_failed_pair_boundary.py`。各new-only工具は既runへ再発行しない。Linux/JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/PG18、実command/時刻/依存hashは公開3934 manifest内。manifest SHA **a4634ff257547018216739da4a4ee5f32921d6aa2a7f90be0755d26216df0fbe**、元64/65 XML・session hash化した選択単独coverageを同梱。counter/line/method意味はredact前後不変、raw session/DB/鍵/native公開0。

PG3928 wholeは固定cb55caf0ce2b330880f63d717ba31270588847ff/全六source、元exec89619、期待3716/545/1643で実行中。元beginの説明だけ旧Root/hygiene群を継承した不備はBUG1329/YKT1095先行、元begin/工具/sourceを不変保存し、公開3936の外部訂正receipt（e6272243b606e18cc3dbd4d68f67569c23d04810feeade843d6c9b438e745a3e）を束縛。正しいtriggerは旧3714保持＋上記Session独立2件/一Test変更、Main/settings/resources変更0。実数/結果は3930で独立照合前に認定しない。

正式1964/53・既17/190・工数null・QA051final保留・F03未受入を維持。管理pure/同一64→65再実行を追加PTへ二重加算0、全counter100/PGPT/ITST完了0。
