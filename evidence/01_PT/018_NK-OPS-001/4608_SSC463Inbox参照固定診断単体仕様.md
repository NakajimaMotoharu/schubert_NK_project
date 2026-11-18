# SSC463 Inbox参照の固定診断単体仕様

WBS-P018-10.03 CATALOG-013、NK-MSG-002、UI242、SS324/351、SSC463、BUG-3241／YKT-2686。toStringはInboxResultReference[<redacted>]の定数を返す。type、numericId、uuid、固定数値範囲、閉じたenum、DB/JMS／再送の既形式、許可された構造化種別は既契約。

原Reference値のPT-IDEM-REFERENCE001～003を全件使う。独立な84cell許容表で、公開種別・各合法値・診断固定・不正型等を検査する。明示値の所有、null、範囲、enum全定義、配列防御は原試験のまま。InboxModelTest／NonAuthenticationInboxInspectorTestの同文言を同期し、当runには含めない。

Java25、厳格NullAway、Checkstyle、SpotBugs Max/Low、全policy PMD、同source単exec・独立XML/CRC、生counter、公開ABI。実DB・実認証・資格・実ログ操作は発行しない。全受入は別。
