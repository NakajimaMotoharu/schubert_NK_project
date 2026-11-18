# BUG-3237 Cleanup所有と固定SQLの補充仕様

WBS-F03、P017-07.02、NK-BAT-001、UI251、SS311／332／341、SSC063/175/437/461、YKT-2683。CleanupRepositoryの取得は固定messageの非正常NPE、CleanupStepRepositoryの取得は既SQL診断の契約を維持。それぞれのRepository内に行・文の型付き解放を置き、scope各一回の行→文、既known/unknown例外優先、借用Connectionの終了禁止を保持する。

既CleanupKindの九定数にある固定SQL識別子と固定SELECT・bind部でSQL文字列を作る。HTTP/DB値やfixture入力を識別子に用いない。原文のSQL九件が一字ずつ一致することを既CLNQUERY001と既bind/境界の表で照合する。CLNQUERY001～009とCLNPORT001～009はいずれも元独立Oracleのまま使う。

期待は各旧未フィルタ分岐が既実用条件を保持する単一判断へ移り、コンパイラのswitch mapが生成されなくなること。未到達は理由を証拠に保持する。Java25、厳格NullAway、SpotBugs Max/Low、PMD、Checkstyle、単exec／CRC／全XML、旧sourceとのpublic ABIを照合し、全WBSや実DBの受入へ加算しない。
