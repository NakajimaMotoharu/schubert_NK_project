# 2607 API八Main例外境界 PG追加発見・四site是正 静的確認仕様

実施時訂正（原計画を保持）：14202はphase CLIが既captureの引数なし契約と不一致で初body入口終了1/OUTなし、BUG2094。新14206の引数なしbeforeで原欠落を保存後に四siteを是正。14208 afterは旧before参照漏れで終了1/OUTなし、BUG2095。新14210 library/14212引数なしentryで真正before14206 hash固定参照しafterを確認、元before再演0・CLI/sys.argv書換え0。失敗を成功や製品PTへ算入しない。次の新source six compileはpackage/-DskipTests=trueで元PTを実行せず、format/null/型/WerrorとTest compileを確認する。原Source/元成功を保持し、source固定後の新SLOTへ出力する。静的製品チェック/追加tool手戻りは原48文脈分類から分離する。

2026-10-30 JST/PG-D870/event2994（原八Source48 raw選定・開始0.5/3/5cap10）/source0061。八Source全2920行を審査し、原generic-catch48の機械参照を行う前にBUG2092/2093の四欠落を発見・915/916へ修正前起票。原48の文脈分類は未実施/未受入で、追加発見のPGを代わりの元計画完成にしない。新依存四site PG/静的確認の追加事前見積0.25/1/2ppは原群見積と別、実費/工数率へ換算0。型名全application検索でSubmissionのexecute/executeCanonical二catchをmethod-local確認（原795行の全body認定ではない）、Commandは型分類0のeligibilityだけ確認。両者に追加修正なし、八全body外の委譲を推定しない。

|追加障害/是正site|期待・独立根拠/元実装|
|---|---|
|BUG2092 UserQuery.persist|SS312/324 SSC329、InboxExceptionはSQLException subtype。cause/next Errorを持ちsuppressed空でもMESSAGE_ID_REUSEへ分類前に元fatalを伝播。元はif(messageMismatch)へ直行。|
|BUG2092 LogQuery.persist|同じ後段欠落、前段inspectのguardでは後段の新例外を検査したことにならない。|
|BUG2092 QuestionQuery.persist|同じ後段欠落、元snapshot/role/owner判定/Inbox/audit/commit・replyの正常契約は変更しない。|
|BUG2093 QuestionQuery.complete Auth catch|AuthenticationContextExceptionは通常graphを保持するRuntime subtype。固定SESSION_INVALID/rejectを返す前に元fatalを伝播。元はrejectへ直行。|

PGは既共有TemporaryInfrastructureException.preserveFatalを四catch先頭へ各一回追加し、BUG/YKT/SS comment以外のbyteを不変にする。新module/依存/権限/SQL/認可/wire/DIF/例外graph書換え/再送/rollback/close回数を追加せず、非fatal時は元分岐をそのまま通す。全22 typed catch（Auth/Inbox、元八＋Submission）を独立manual role/receiver表で照合、既18のguardは重複追加しない。QuestionWorkerはInbox/Auth分類0、全fatal処理の受入ではない。

14202 beforeはGit0061/normal13832の同一Sourceとcurrent全入力を照合、code-only欠落四/guard18を観測する。exit0は観測処理の成功で静的conformance=false/gate1・Product PT未実行。14204 afterは同一immutable工具をphase引数とbefore hashで呼び、三Sourceの四guard＋comment以外のbyte差0、22先頭実行token/正しいreceiver、各四siteのremove/comment-only/string-only/wrong-receiver計16metadata反例を確認する。LEXは既public-source字句工具、一般Java Unicode/全意味parser認証でなく、固定Source/最小diffと後続の許可されたcompiler/static checkを分離する。期待は承認SSと手書四site/22role表・固定Source diffでProduction methodを呼んで生成しない。

禁止/保留：元UserQuery等Application whole PTは@BeforeAll実PostgreSQL/Flyway/一部実fileを含む。実DB/Root/VM/permit/停止/回収/元graph9やその新fixture/部分抽出/別model再試行をしない。新mock/Javaハーネス/実graphを作らず、当確認はPG強化レビュー・許可静的代替のみで、PTのPASS/実測coverageに算入0。dynamic conformance/coverageはnull、BUG再試験条件・451はHOLD/未受入のまま。source0061の400件/59suite/39program四100は歴史証拠として保持し、変更後sourceへ転用しない。修正後は必要なhost build/静的・Source固定の実施範囲を別に記録し、PGPT/IT/ST完了を宣言しない。

2608結果へ日時/OS/JDK/tool・branch/基点/候補Source/dirty/command/exit/原入力・静的期待実際/残PTリスク/BUG/YKT/path/hashを記録。全HOLD/二held工具metadata前除外・原本/Backup/鍵/native/Currentbaseline/stash7保持。利用枠44→22はreset同一でも比較不能、event2995へ原観測を保存し負の消費/自動reset/無料作業と推定しない。
