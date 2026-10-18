# NK-MSG-002 snapshot scratch所有（BUG1453/YKT1217）

対象ResponseSnapshotCodec.compress/decompress、SnapshotScratchOwnershipTest、独立codec golden七、PG5540。関連RD永続冪等/既PT-IDEM007008・SS324§6/15/352、F03 raw二件、既1131/1132/PG5506。上位仕様/圧縮level3/暗号・AAD/例外優先を変更せず、Mainにtest専用portを追加しない。

## 独立期待値

|Test ID／JUnit method prefix|目的と入力／操作|独立期待値・fixture|
|---|---|---|
|PT-IDEM-SCRATCH001/scratch001|実compiled compressのbyte配列命令直前にsynthetic Errorを注入、固定1byte入力|scratch確保はnative ctorより先なのでnative取得0/end0、反射呼出のcauseは事前固定した同一Error|
|PT-IDEM-SCRATCH002/scratch002|実compiled decompressへ同じ注入|Inflater取得0/end0、固定Errorを正常化せずそのまま観測|
|PT-IDEM-SCRATCH003/scratch003|明示した旧型negative-control Deflater→array→try/finallyへ同じ注入|取得1/end0で未保護gapを検出。fixture finallyで保有nativeを実解放し後続へ漏らさない|
|PT-IDEM-SCRATCH004/scratch004|同negative-control Inflater版|取得1/end0。同上|

JDK25実ClassFile APIで**test-only別名のstatic target method copy**を生成し、対象methodの一意性/static/descriptor([B)[B・実NEWARRAY1/constructor1/end2という形を独立に検査する。元命令・helper参照・handlerを保持してctor成功後に取得、end成功後に解放を観測、元scratch命令直前にだけErrorを挿入する。Errorは実heap枯渇ではなく固定fixture、raw key/DB不要。別名copyは実Main CRCやcoverageへ混ぜず、agent除外設定変更0。Main他method/constructorは元goldenとfresh全体の対象のままで、fault copyはそれらの成功を主張しない。Mainのgoldenは元クラスに対して従来の独立JCE/圧縮値で行い、production methodからexpectedを生成しない。null/欠落/AAD/key/境界/暗号provider異常は元七caseを全件再実行、既期待値変更0。

## Red/Green／coverage

Main296を変更する前にfault四だけを新clean Test commitで実行し、scratch001/002のみFAIL、negative二PASSを確認する。harness/compile/別原因の失敗を再現成立としない。Redは合格数に算入0。その後scratchをnative取得より先へ移し同fixtureのgapを修正、四fault＋元七=11caseを固定別sourceで実行する。7他fixtureは全検索対象をcontrol-flow根拠付きで非該当又は修正し、必要full回帰で実利用側も試験する。

実行 `PYTHONPATH=tools/quality/vm/050_s1 python3 -B tools/quality/pg5540_snapshot_scratch_selected.py red|green --version v1`。新only private `pg5540-snapshot-scratch-<phase>-<version>` に固定Git archive/commands/start・各owner/PID/ticks/hash/log/真正終了/XML/coverage/static/source同一性を記録。Java25.0.4/Maven3.9.12・既toolchain repository、子umask0027。

全六formatをPT前に確認し、package（bootstrap test-jarも同sourceで生成）＋当selected11＋built四module SpotBugs/NullAway/Werror＋JaCoCo reportを実行する。未実行upstreamPTはselected成功へ数えず、全体coverage/全回帰/451合格は別。target四counter結果と物理Main差分は実行後002へ記録、全体100を当selectionで代用しない。当Source fresh全体は必要別工程で行い旧296 native/全体を新Sourceへ転用0。

FES/flaky/skipped/not-runを成功算入0、fixture/harness失敗は原因を保存し新version/sourceで必要部分だけ再試験、旧ログ上書き0。公開resultはallowlist/hashのみ、private rawXML properties/秘密をGitへ保存しない。群開始1278/補正1279・0.5/1.5/4ppは未較正固定、実費不明null、正式1964/53/QA051finalは保持。

## BUG1456/v2補足（上位仕様・品質非変更）

v1/65292は全六format0→protocolの既存failIfNoTests=trueで止まり対象0件、再現不成立として保存。v2は全四reactor moduleのguardを抑制せず、必要な依存契約としてPayloadGoldenVectorTest三（独立64layout/最大繰返し/並行byte）・ResourceScopeTest八（所有/例外優先/null/並行）・ApiNonSecretConfigTest七（既定/境界/非秘密テンプレート/決定性）を全source inventory付きで明示する。Redは**対象4＋依存18=22**、Greenは**対象4＋既codec7＋依存18=29**。fault再現成立は001/002の`native acquisition before scratch failure`で期待0・実1のAssertionだけとし、同じ2件の別理由失敗は認めない。依存試験を元296の成功へ加算せず当new Test sourceの選択結果とする。全体回帰/全scope成功を代用しない。YKT1220全四moduleのactual XMLまで確認する。

v2/73357は全22到達・依存18/negative二成功だが当Main二が全class copyの未使用constructor/型階層検証で失敗し、**予定Red不成立**。BUG1457/YKT1221でv3をstatic対象methodの厳密copyへ是正し、ClassFile.verifyと実ロードを無効化しない。constructorの試験範囲や元Main coverageは変更せず、copyだけでそれらの合格を宣言しない。元v2ログ/XML/物理Main779同byte差0は保持する。
