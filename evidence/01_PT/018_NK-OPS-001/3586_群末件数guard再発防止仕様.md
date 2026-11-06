# 群末件数guard 再発防止仕様

NK-OPS-001/WBS-P018-04.03、487/Bug2331/YKT2076。Production Java/PTでなく純粋metadata工具。pmo_event_summaryは外部IOやresetを行わず、独立検証済み件数からcanonical ALLn_PASS_FOUR100_POST0文字列を生成し、summary中の唯一の件数と照合する。件数だけでPT/coverage/gateを合格にしない。

PT-META-SUM001..007: 固定期待文字列5ケース、invalid count6種（0/negative/null/bool/string/float）、unknown/曖昧/0/leading-zero label6種、元event4002の8対独立qualified13不一致、追記4004の13正規化、元Csrf4005/qualified9、直近全8GROUP_END/publicmanifestの実件数結合、actual13/9からの生成をunittest7methodで確認する。expectedは固定literal/独立資格manifest由来で、helper自身から作らない。元event/証拠/実費を変えず、元4002の誤記を消さない。

969群内の訂正4004/971とcurrent4005は保持、972/event4006原0.1/0.5/2cap3で共通工具と回帰を追加する。test command=env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/071_group_summary_count_guard_checks.py。コードinputはhash固定したworkingtreeで実行し、publish後Git byte一致を独立postで結合する。Metadata7をProduction件数/Java coverage/sourceproof/受入へ加算0、451/globalGは未受入。結果3587/PG20416へOS/Python/source/run/exit/shaを保存、fresh終端確認後のquotaを結合。VM/DB/Root/鍵/私有raw/元JUnit再演/held二読取を行わない。
