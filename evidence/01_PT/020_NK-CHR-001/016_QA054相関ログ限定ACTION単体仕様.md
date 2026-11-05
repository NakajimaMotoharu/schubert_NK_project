# QA054 相関ログ限定ACTION 単体仕様

NK-CHR-001 / CorrelatedLogEvidenceValidator、Main pom JSpecify1.0.1既存dependencyを明示、@NullMarked validate/versionOneはnullable入力を固定failure/falseへ分類する。RD FUN008/MON003/TST004、UI264/235、SS351355、QA054/UIC011/SSC336/main f6df0102f。

新CorrelatedMenuActionContractTest全7（PT-CHR-QA054001..007）＋変更Mainの既CorrelatedLogEvidenceValidatorTest全9=選択全16。①初回正常menu/logsearchの独立literal expected/observed、Input不変、②MENU local/outbox必須・欠落/重複、③MENU GET/root200・HTTP欠落/不正とAPI LOG_SEARCHED witness拒否、④Current ACTION menu/log_searchのexact NK ACTION名称・category/大小文字/space/未知の非包括対応、⑤operation相関・DB欠落・replay二重保存拒否、⑥両expectedに2件を入れても初回成功数1を超えれば拒否。⑦任意responseBytesの0/N12上限と負値/超過/小数/text/nullを独立境界で確認。既9で全schema/数値型/null/未知/変更前行/未知field/REQUEST互換・欠落重複を回帰する。

期待は承認UI/SSからTest内のliteral JsonNodeで独立作成し、production methodでexpectedを生成しない。観測は合成入力であり実capture/DB/DOMを測定したとは扱わない。Current/NKの操作参照、after DB、検索response snapshotは異なる段階で、当検証はDB相関/投影だけ。DOM/native/realL01/保持原本/Currentbaseline等を読取/変更/実行しない。GateCli/promote/ArtifactSink/NativeCapture/Browser/PostgreSQL/鍵/VM/拒否操作・held graphも実行しない。

Main/source固定fresh normalChar build（test skipはPGだけ）、NullAway/PMD-CS/SpotBugs、normal JAR全physicalCRC、同一exec/sessionのline/method/class/branch100、全@Test/終端code/XML、null-negative/入力不変/異常test、TestID-method/command/OS-JDK/対象commit/BUG/path/hashを017結果・manifestへ記録。現状NOT_RUN、CoreMain1eaは別固定・既Char66再演/転用0、正式1964-53/工数null/第一V実測HOLD不変。

2026-11-06観点補完：原PG19588全15はFES0だがbranch225/226で全Source資格未達。line285の任意responseBytes有効値の分岐を独立仕様から追加し、Main/旧9test/normalJAR/SBは変更なしで新全16の一execを要求する。元15のexecやcounterを合算せず、newTest追加は未実装試験観点の補完でMain障害の修正ではない。
