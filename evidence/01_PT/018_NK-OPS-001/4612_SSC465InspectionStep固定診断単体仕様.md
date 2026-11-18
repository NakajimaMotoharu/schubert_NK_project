# SSC465 InspectionStep固定診断の単体仕様

P018-10.03 CATALOG-017、NK-OPS-001、SS351/354、SSC465、BUG3244／YKT2688。InspectionStep.toStringはInspectionStep[<redacted>]の定数。各outcomeとcursor、終了判定、合法状態、値比較、既構造化結果は従来の契約。

元InspectionRunStepValueContractTestの全4で、固定独立入力のRun、ID/時刻、DELETED/PROTECTED/ENDの公開値、cursor関係、不正／null、同値・enum語彙を保持し、三outcomeの一般診断固定を追加確認する。実Inspector・実ログ、鍵、DB、native、Rootは起動しない。

Java25、厳格NullAway、formatter／Checkstyle／SpotBugs Max/Low／全PMD policy、単exec、元XML、未フィルタ、現sourceと公開ABIを独立照合。既35診断のsource一覧に結果を結び、外部58、実経路、全451／P018-10受入は保持。
