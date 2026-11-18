# SSC464 Outbox二値の固定診断単体仕様

WBS-P018-10.03 CATALOG-022/023、NK-MSG-002、UI241/242、SS321/324/351、SSC464、BUG-3243／YKT-2687。OutboxEntry/Requestの一般診断はそれぞれ型名と固定伏字。明示id、宛先、本文防御copy、lease、再送順序、DB/JMSおよび許可済み構造化欄は既契約。

OutboxDataValueContractTest全3とOutboxRetainedValueContractTest全2を用いる。既合成入力から独立に期待したid、版、時刻、宛先、lease、owner、null、境界、copy、DLQ、不正metadataを維持し、診断固定と明示取得を別assertで確認する。実送信、実情報、実ログ・DBは使用しない。群外の配信／所有境界は既保留を維持。

Java25、厳格NullAway、SpotBugs Max/Low、Checkstyle、全PMD policy、同exec／XML／class CRC、生counter、公開ABIを現sourceで照合。全451・全P018-10・実CHRの受入は別。
