# 残gap適用性・次ordinary候補（着手前）

2026-10-22候補照合訂正（計画条件の訂正、新PT/進捗加点0）：1477当source原6726全4184 coverageと実Testを確認した。Transferの`transfer3048002CalendarLowerUpperBoundaryAndYearZeroAreIndependent`は既に00000101/00010101/99991231を独立検証済みで、year0を未実施とする下表は旧候補の誤認。当line104はci8/mi0/cb3/mb1、未達は8ASCII桁から取り得ないyear>9999のtrue側だけ。year0試験を重複追加しない。他missはinspect/sameDirectory/enumerationの独立IO/metadata観点で、実原本やraceへ拡大しない。BackupWorkerRequestFilesの実残はline97/126の非MISSING再throw、102の二読不一致、138の前後request/dir identity不一致（各実counter保存）。1476元job実行中はsrc/Test変更0、後続着手時に予算/独立oracleを別固定する。

1471の元全体/原回収/同source品質/trace完了を先行し、実行中のMain/Testは変更しない。この文書は候補分解で、群開始・PG/PT・受入・見積減額ではない。通常小群完了だけで停止せず、次の独立候補を既存WBS内で進める。

基点は旧f16f/4170のcoverageXMLに残る箇所であり、新d48f/4184の実測ではない。新全体の実counterとSource byte一致を照合してから着手する。485実物でTransferCleanup.java主P017-09、BackupWorkerRequestFiles.java主P017-03（current943と歴史941に各一descriptor、費用を二重計上しない）。

|候補|残箇所の実内容|独立fixture/期待値|判定|
|---|---|---|---|
|TransferCleanup日付境界|yyyyMMdd形状・strict LocalDate後のyear0保全が旧未実行。上限year>9999は8 ASCII桁の四桁year不変条件との重複を要検証|新JUnit TempDir内に00000101/00010101/99991231/9桁等の明示literal directory、各独立残存/empty date削除/件数をSS333§12・341から固定。外側Guard/実保持FD/既mtime境界を維持し実Transfer原本へ触れない|PT_DEFAULT候補。重複述語を整理するなら、受理集合の同値証明・独立vector・判断記録を先行、coverage除外や入力不可能caseの反射注入はしない。証明不足ならそのPGを保留|
|BackupWorkerRequestFiles普通resumeの二読/異常理由|旧branch missはMISSING以外のread異常、二読の変更、directory identity差のfail-closed等|既BackupPublicationFixtureは入力IO/metadata injectorとしてだけ使い、公開synthetic request literal・新TempDir・公開UUID/時刻で、異常時publish/retire0・原byte/inode保持・全owned descriptor解放を明示期待値とする|PT_DEFAULT候補。実resume/Backup/DB/intent/permitの操作や失敗cohort回収ではなく、普通の自己所有fixtureだけ。source/command/副作用が変われば再判定|

その他のnative main/bindingやroot/UID/cgroup/Unit/既permit等の実状態が不可欠なgapは、その名前だけでなく実行権限・IOと依存先を確認してHOLDを維持する。実サービス/VM/原本DBBackup/鍵/失敗cohort/既native証拠にはアクセスしない。DirectoryIteratorException等を不安定な実環境raceで発生させず、未知/不可能を合格・100%へ補完しない。到達性だけでcoverageを除外しない。

着手時は新全体の真正source/counterに基づいて必要対象を確定し、現leaf開始予算をeventへ固定、仕様/独立oracle→必要PG/既全Test byte保存→限定関連群→原資格→必要まとめ全体の順とする。原/v4/既1674・1678は不変、実N/T・専有費・工数率null、現在受入17/190・正式1964/53・QA051final・拒否代替完了0は据置。
