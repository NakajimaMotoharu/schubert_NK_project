# 1547 AlertThresholds 単体テスト仕様書

2026-10-23、NK-OPS-001/P018-09、C07共有参照、PG-D520。SS351§7/10・UI252§6・RD MON005～009/013の承認済12条件を純粋入力からNORMAL/WARNING/CRITICALへ判定する。着手見積1.5/4/8pp、上限10pp、共有使用7/残93/reset1793306748（元開始0）。元計画製造の不足補完、C07監査費/元受入の二重計上0。

PT_DEFAULT：数値/Duration/booleanだけ。実metric collector/Queue/DB/service/VM/Root/Backup/鍵へ接続しない。入力値の真正性・source/owner・観測連続期間はcallerが保証し、このpure判定から保証しない。共通型は1545のSeverityだけを使い、実制御/通知/起動抑止は別未完。warning/critical双方を満たすとcritical優先。時限付きはcallerから二つの連続超過Durationを受け、非負かつcritical側<=warning側を不変条件にする。counterとpercentageはそれぞれ承認条件のOR、byte単位はSI decimal GB。async比率はBigIntegerによる整数交差積でoverflow/丸めなし。入力不正を正常へ補正しない。

ExpectedはSS351表のliteralと独立手計算の分数、threshold前後1byte/1件/1ns、doubleのMath.nextDown/nextUpで作る。Productionの評価器をexpected生成に呼ばない。既mode7/catalog6/state14の27は同package必要回帰、新threshold14は追加分。元4222/common44再演/旧counter合算0。

| Test ID / method | 入力と独立期待値 |
|---|---|
|PT-OPS-THRESH-001 / threshold001|FS80%5min=warning/90%1min=critical。割合直前/到達、期間1ns前/到達、warning/critical優先、0/100 |
|002 / threshold002|Transfer3.5GB又は5000warning、4.5GB又は9000critical。byte/件数前後と両OR片側成立 |
|003 / threshold003|Async5000件又は70%、9000件又は90%。countのみ/ratioのみ、699/1000・700/1000・899/1000・900/1000、Long.MAX値の交差積overflowなし |
|004 / threshold004|Web log5000件又は最古5分warning、9000又は30分critical。0/直前/到達とOR両側 |
|005 / threshold005|DLQ0normal、1warning、非空で増加又は未調査critical。全boolean4組合せ、空を誤警報しない |
|006 / threshold006|Expiry999normal/1000warning/4999warning/5000critical |
|007 / threshold007|DB pool80%5分warning、pending又はtimeout>=1critical。期間/割合前後と各count片側 |
|008 / threshold008|heap75%10分warning、90%又はOOMcritical。割合/期間直前/到達とOOM片側 |
|009 / threshold009|sync p95 >2.0s5分warning、>2.5s5分critical。厳密超過、double直後/直前、期間1ns前/到達 |
|010 / threshold010|Backup05run後当日成功なしwarning、連続失敗2critical。予定前/後・成功有無・失敗0/1/2 |
|011 / threshold011|10分内restart0normal/1warning/4warning/5critical |
|012 / threshold012|integrity/config0normal/1critical、自動復旧/closeは実行しない |
|013 / threshold013|全domain負値/NaN/±Inf/割合>100、capacity0、全Duration null/負/順序逆を拒否。診断固定・入力原値なし |
|014 / threshold014|64並行callerが12条件を同じ独立literalで評価、元不変値、全Future成功/全executor終端、sleepなし |

同package41件/5suite、全12実行class＋metadata1を当sourceの通常verify/四100・CRC/単一session・XML/静的解析へ接続する。新code/設定/hashを旧source成功へ転用しない。実行command/source/exit/coverage/static/hashは後続1548と新onlymanifest。実観測、性能、status/collector配布、NATIVE/IT/STは未受入のまま、F03 Root11/actual/拒否操作HOLD不変更。
