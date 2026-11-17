# NK-WEB-002 Rangeパーサ whole5仕様

P00904、RD FUN005～007/PER004～006・UI223237・SS333§10/354、PG-D1175/BUG3178/YKT2647。詳細は018_NK-OPS-001/4495。元HttpByteRangeParserTest4 source・固定区間/record/hash/enum/並行oracleは保持。新HttpByteRangeNamespaceContractTest1はprivate utilityの非構築とfinallyでのアクセス状態復元、復元後の拒否を独立に確認する。単にObjectを生成してcoverageを上げるものではない。

元4のPT-MED-001～004はfirst range/1MiB cap/空・未知・null・桁溢れ/例外/Full-Partial/各全generated/hash固定34603007/enumコピー・valueOf/有限100並行を持つ。追加record/enumの重複caseは作らない。既存PG27002保存execの現在Java/Test/byte同一の範囲を解析してprivate ctorだけ1L1M3I未達と37532で確認後、修正前に台帳登録しMain一bodyをguard化した。

Java25/原POMNullAway/限定Main2source6physical、strictTest、全6SB/PMDCSformat、五ABI・物理/debug差分、単一exec全181CRC/init・独立raw/XMLを確認。原186の確認再演/oldexec合算/除外なし。自然Selection NoCode0/0は保持する。実HTTP/配信/FS/認証/DB/JMS/Root/native/VM/key/権限/四held classfile操作なし。全case/command/OS/branch/sourceは37550.begin/37552.caseIdsとファイルhashへ一意対応。
