# 2124 F03現source差分index集約結果

2026-10-27 04:51 JST、2123/event2477、WBS-F03、開始0.5/1.5/4pp cap10固定。host sourcee73/Main21d不変更。PG10834-current-f03-derived-index-v1 `0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055` actual0、独立PG10836-current-f03-derived-index-post-v1 `6df85334f074141f4bfb9ce5d99df9992b89a780c1673104c66d94481e2e2a0a` actual0・九metadata反例。

| 集約項目 | 件数・意味 |
|---|---|
| 元全体scan | 1810Java/9409 finding、10688/10690の不変原証拠 |
| 元からsourceが変化 | Test17source、全件が次の再測定scope内 |
| 再測定済scope | Graph三＋Protocol188＝191source。その他1619sourceは元input SHA不変 |
| 入替え | 旧scope114 finding（Graph7/Protocol107）→現Protocol10。消滅ID104は実是正の部分測定結果 |
| 現source差分集約raw | 9305＝Main1512/Test7793、すべてPMD、CS0。全current解析の新runではない |
| 根拠join済 | 原ID2679、参照2681。Protocol THREAD二の重複参照を二重件数にしない |
| この集約に現資格の参照なし | 6626。未review又は真の障害と断定しない |

元Graph三/Protocol十は現hashの10716/10806実測、他1619sourceは元full scanの同inputで連結した。originalRowSha256/原IDと現input/attributes・measurementBindingを保存し、sourceが異なる旧rowを現測定へ貼替えない。104の消滅はこれまでのTest規約是正の追跡で、今回のmetadata作業で104を新規修正したという意味ではない。

分類参照はTHREAD2125（10822/24）、ClassLoader542（10828/30）、Protocol十（10810/14）、STRICT EOF四（10726/28）。元source全input/各原ID/現SHAが一致したものだけをjoin、THREAD二がProtocol十と重なるためunique2679。その他の歴史reviewが未joinである場合もあるため、6626を違反数や未review総数へ置き換えない。actualViolationCount=null、全F03未受入を保持する。

上位の未join件数はDuplicateLiterals2987、GenericException849、CloseResource679、Octal435、IfLiteral394、ConcurrentHashMap176、Assignment173、Synchronized150等。これは選定用indexであり、各ruleの妥当性/障害/PG量は対象source読取と既後続成果を照合して確定する。次の具体候補はWeb viewのLog/Scenario関連八Testに残るduplicate55。3424行のfixture/依存・既PTと実操作を確認し、普通memory/template PTで安全に閉じられる群へまとめる。現計画の単なる分類だけで終了しない。

10834初回unused copyはpyflakes1で本体未発行/OUT0、BUG1854/YKT1605同根追加、修正前SHA7bf985a3d8b273f53ff4fcd5c9d3221b93dc11c166538ae91d8f5e876db40f59を保持。不要削除→前置0後の初回本体/独立post0、製品実行0。九反例は原ID欠落/重複/未知・誤input/source/rule・偽context/PASS/全current scan偽装を拒否。原rawや保留を成功へ読み替えず、全解析/全回帰/既成功PTの確認再演0。

commandは`env PYTHONPATH=tools/quality python3 -B tools/quality/pg10834_current_f03_index.py`と10836、host Linux/Python3.14/branch dev-foundation。実時刻/exit/input/期待・実際partition/hashはmanifest/current-index.json/source-delta.jsonへ保存。source/code/ルール/抑制/新fixture/実PT/coverage/外部操作0、Protocol componentの102PT/四counter100/SpotBugs0は1192のまま保持。正式1964-53/17-190/工数null/QA051final/全安全HOLD・未読保証不明1847不変更。

共有used18→19/残81/reset1793599188/短期非提供ordinaryAllowedtrue/券0、共有丸め1ppは専有費ではなく実token N/T/専有費null。usage3af949b0c01ff21e328aa205070c9a0b4a4df866590d50233b9d7904d3798cfaを継承、原/残見積り・分類・再認証・実装是正の費用を混同しない。own jobなし/外部所有UNOBSERVED_HOLD。次は安全性の成立する前記PG/PTへ、通常小群/commit/PMO待ちで停止しない。
