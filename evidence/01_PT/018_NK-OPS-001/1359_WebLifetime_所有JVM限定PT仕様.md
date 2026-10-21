# WebProcessLifetime限定PT仕様・PG点検

対象NK-WEB-002/NK-OPS-001、SYS004/AUT002/MON003、UI212/243/253、SS313/342/352、PG-D369/377、WBS-P018-06（主費、参照P018-05追加費0）。元全4048/6332/source aed19c6dca368e9717309d6f744d7917c6b7b32cは終了済で再演しない。全851Main不変更・既存四LIFE Test/oracle不変更、一既存Testへ一method/fixtureのみ追加する。MainのPGレビューはowner保存・private stateLock・正常/割込の通知待機・shutdown中removeHook例外でもfinally通知・UNKNOWN非復帰がSSと整合、実装修正不要。コード差分と実行snapshotを後続manifestで固定する。

## 独立期待値と入力

NATIVE-LIFE004 `WebProcessLifetimeTest.life004OwnedJvmTermClosesWhileShutdownIsInProgress`: 新ProcessBuilderからWeb lifetimeだけの最小JVMを一回生成し、environment空、stdout/errは専用TempDir。固定文字列READY一行を最大5秒観測後、そのProcess handleだけdestroy（Linux TERM）、5秒内終了143、出力READY→CLOSED二行・stderr空・child不在を期待。CLOSEDはTWR closeの後のみ出力する。RootやWebMain、DB/JMS/network、鍵、service/VM/intent/permitは一切触れない。失敗時のみ当childを有限force cleanupし、137を143や真正Root成功へ変換しない。事前条件は同run JaCoCo agent/Java25/Linux、欠落時は失敗でありskipしない。

独立oracleは固定HTTP等ではなく明示JVMfixtureのstdout順序・実OS終了値・Process所有と期限。public JaCoCo RT/IAgent.dump(false)をclose後一回呼び、同run実probeだけを保存する。fixture-coverage-drain hookはagent先行終了を防ぐ測定用barrierで、Production hookの待機や借用providerの完了を実証しない。外国threadがowner通知まで戻らない点と割込復元は既存LIFE002の独立latch/原assertionで別確認。実shutdown中removeHook IllegalStateExceptionと非割込側が当試験の追加条件。private reflection、mock対象の実counter補完、人工branch除外なし。

既存LIFE001の正常/二重install/null/health不良/割込、LIFE002の並行通知・割込保持、LIFE003の健全待機→別stop、MONITOR004 privateLockに加え、WebUnknownRetentionTest一件（provider無し自己所有daemon fixture）がretainUnknownの正常sleep/割込後の非復帰/closed0を同source/runで確認する。再送・業務DB条件は本classに非該当、native assembly/Root/borrowed資源の受入は別未完。

## 実行・対象commit・証跡

新PG6348宣言18件/9suite（元baseline12/7＋当class5＋UNKNOWN1）、PG6350は元archive/XML/六Jar/851Main/1667physicalと静的だけを照合し追加PT0。新sourceはcommit後begin.safe.jsonで確定、全Mainはaedと同byteでも旧全4048/native成功を新sourceへ移植しない。実行command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6348_web_lifetime_selected.py`、真正0後だけ同環境`pg6350_web_lifetime_qualification.py`。対象Main/Test/gatesは元終端/資格完了まで固定する。

新実行結果・日時/OS/JDK/command/exit・入力/独立期待値・XML/counter/関連BUG・path/hashは新公開manifest/後続結果書へ保存する（現在未実行）。当class四counterは実XMLでのみ判定し、line/branchの既存miss1/1を推定で0にしない。全体coverage/native/CHR/451/正式は未完。新品質不一致を発見した場合は915/916へ修正前起票する。

## 計測・境界

event1545群開始.25/.75/2ppは凍結、原/v4不変更、実N/T/専有費/工数null。開始参照P018-03は実作業対象ではなく予備参照として記録されたため次eventで除外追記し、元eventは改変しない（費用追加0）。fresh used39/残61/reset1793082864/secondary不明。正式1964PT/53scope・17/190・QA051final/PTALT対象不明代替0・実環境HOLD・全保全物不変更。

前1358のmain状態未反映は歴史値。design-only PR185は06c32d69fcaf5deba1ce79dbe44a469cc5c82c2f→main ab43366ab800f86fb722dad14cadb8ab42a84fd7で通常merge/fetch済、914のSSC321/322/323局所完了六行だけ、未受入code/Test/tool/evidence混入0。artifact attachmentは100件上限一回失敗のみ・再送0。
