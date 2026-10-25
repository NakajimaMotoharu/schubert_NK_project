# API Outbox値型・集計overflow実行結果

2026-10-25 22:09 JST、群2218/API_OUTBOX_VALUE_OVERFLOW_V1、原owner/cost WBS-P006-02、仕様1971/PG-D672。修正source e598a81bb4200b4e4930278b31479ff927aa025f（Mainのlong cast一箇所＋新境界Test一source/三method）。開始1/3/8pp/cap10は不変更。

| 原証拠run | 実際の結果 | manifest SHA-256 |
|---|---|---|
| PG9746-outbox-overflow-witness-v1、旧fd3d04 | 0/MAX/MAX/2を受理しwitness exit1、既実装欠陥を再現。数学的和4294967296、PASSへ加算0 | a9806f2652adcb0785e0e51a35e033993dd63fd4cd21b338a0d539ded911d8a5 |
| PG9750-outbox-report-six-compile-v1、当source | 六Jar・Java25/NullAway/lint/format正常終了0、PT0/UNRUN | 7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96 |
| PG9752-outbox-value-preflight-v3 | 既10宣言＋新3のsource/compiled descriptor、4suite/全8Main凍結 | 086ec90be8f952f1fa252978634a14ed93ea969a5e9cdd998a0e39835795b625 |
| PG9754-outbox-value-host-v2 | 実13found/started/success・4suite、F/E/S/aborted/container failure0/exit0 | affbf2ef4c901e34206b99fa6610cf839c6c89037d7c4e6bc7b4e0a22ddc91e4 |
| PG9756-outbox-value-post-v3 | 元XML/source/session PG9754-API-OUTBOX-VALUE/CRC・全8unit/8class、L148/M50/C8/B79全miss0/四100 | ad294102220a887c95846df3ce33188d130bee2a3a89babe188e9d7d9e012600 |
| PG9758-outbox-api-static-v1 | API Main全class/当六Jar依存のSpotBugs、BugInstance/MissingClass/Error0/exit0 | 2c8439ae72535023ee5a22bc5311d90e46bd634bc4f1f7df50c889b791ada34f |
| PG9760-outbox-changed-source-static-v1 | 変更Main＋新TestのPMD/Checkstyleとも指摘/処理error0/exit0、抑制/除外なし | adc1062211e62be7464d1388a86e3f23c863b67b60db216cddd4d2c7e8bc8d26 |
| PG9762-outbox-quality-source-post-v1 | source差分2file/全1843Main中変更1・既1842同byte、既1912Test class不変＋新1、原結果/static/Web非該当/全scopeを独立照合 | 8b9963b22aac0b2d9dc1241c35cc07537980cd670a616854ca46a8c2cb0dc6c9 |

各公開path=evidence/provisional/<上記run>/manifest.json。9756v3に元4XML/summary/全8class counterを保存、source/input/独立固定vector/TestIDは1971＋新BoundaryTest＋cases.json。command/OS/JDK/実行日時/終了codeは各manifestのinvocation/begin/stage、元source/archiveとslotは /home/mini/codex/project1/work/pgpt-runs/PG379/pg9750-outbox-report-six-compile-v1・pg9754-outbox-value-host-v2。報告器の元exit0/CRCは保持し再実行しない。旧source native/PT/exec/coverageを新sourceへ合算0。

## PG/PT・横展開の実績と限界

- BUG1760は実装済みinvariantの不具合。修正e598a81のlong和は最大三intの数学的合計を表現でき、元0/MAX/MAX/2・1/MAX/MAX/3の各位置とMAX三内訳の周回を拒否。新OVF001～003は正常7/周回7/負値・不一致14の28独立vector、既10methodを合わせ当13件を実行。新試験ID増分は3だけ、反復runやvector数をTest件数へ重ねない。
- YKT1511のWeb同型は既long和＋claimed<=100・既MAX反例があり、現source/旧source一致hashと式を9762で確認して非該当。実DB/JMSを開くWebLogDispatcherTestは今回実行していない。API reportへ未承認の100上限を追加せず従来有効MAXを保持。業務wire/TX/JMS/retry/QA050保守間隔は不変更。
- BUG1761/YKT1512は新準備工具のmodule/package複製残留：v1 rows0、v2 API Jar対storage hashのguardで実1。元工具と診断を保持しv3でAPI PACKAGE/全13decl/byte/8Mainへ是正。既Storage9738の元storage指定は非該当。準備失敗中に製品jobを発行0。
- PG9754v1はnormal内の正規内部Jarを外部m2のみのguardが保留しslot/job未作成。v2で六正規Jarのhash/既bootstrap TestJarの正確pathを照合したうえで、値型に不要な内部classpathを除外し、当API/protocol Jarを明示。旧m2内部Jarやbootstrap Test suiteを実行しない。
- BUG1762/YKT1513は報告器でsuite3→4の数値置換がsession添字へ波及。v1 IndexError、v2 literal backslash-tのschema拒否を保持し、v3は実tabと四field decoder/正常一＋異常六vectorで是正。元report JVM終了0/stdout hash/当exec/CRCを回収しただけで製品JUnit/report JVM再起動0。既9742・Java launcher/helperは当該添字変更がなく非該当。五工具失敗のsource hash/観測exit1/理由を9762へ残し、実装・試験成功と分離する。

元witnessは終了1、六compile60140/host2236/APIstatic58576/post5432/PMD71919はそれぞれ元終端を確認、post v1/v2のPython終了1は成功へ変換せず独立v3だけ資格化。外部process/VM生存・鍵/原本DB/Backup/native所有は未照合HOLD、アクセス/操作0。新source全451・全API Outbox/実JMS/CHR/nativeは未受入、正式1964PT/53scope・既17/190・工数null・QA051final・現WBS監査HOLD/G07歴史4493を維持。旧Protocol102/Storage27の当時source成功は歴史参照であり新sourceの実行として計上0。

開始used11残89、終了fresh13:05:25UTC used12残88/reset1793513544。共有丸め差1ppであり専有実費は不明、N/T・PGPT/PMO配賦・工数率null。元見積/v3/v4/開始1/3/8は凍結、元計画内の集計是正＋追加発見BUG1760と新境界3、工具手戻り1761/1762とclasspath準備、source再認証を分離し費用を推測配賦しない。次は通常保存push後、現source追加Test一/変更Mainのtrace overlayを原owner/cost P00602で更新し、他の許可済みPG/PTへ継続する。
