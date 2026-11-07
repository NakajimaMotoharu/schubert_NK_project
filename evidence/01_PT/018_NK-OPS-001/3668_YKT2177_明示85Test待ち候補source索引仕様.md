# YKT2177 明示85Testの待ち候補source索引

WBS-F03/REWORK、411/451、BUG2432/YKT2177。原.5/2/5pp cap6。21744で固定した明示85Test/helper path集合を使用し、現在hash（UserAudit/Question二修正を含む）へ束縛する。保護名はIO前に拒否。範囲外のTest/Root/工具/private raw/VM/DBを読まず、元Test compile/実行0。

JDK標準compiler APIのparse-only ASTを用い、get/join invocation・method reference、receiverの安全な構造名、引数個数、declared type/initializer種別、method/位置を索引する。文字列/認証情報/引数値は出力せず、Product classpath/annotation processing/analyze/generateを使わない。工具自体のcompileのみ許容する。

型がFutureと確認できないgetをFutureとも安全とも推定しない。未解決はUNKNOWN、既完了Futureやlatch等の意図もsource根拠を読むまでは未判定。明示deadline引数は記述の存在だけで実timeout/cleanup成功を保証しない。索引作成だけでYKTをCLOSEDにせず、全対象の修正/非該当根拠/再発防止と動的HOLDを後続へ残す。

独立照合は85path/hash/Git source・工具binary/原終端・各get/join名の実source位置/arity・metadata否定guardを検査する。原347/current346/分類283/未分類63、BUG2432 SOURCE_FIXED_STATIC_CHECKED_PT_NOT_RUN_HOLD、unique430/whole94/正式1964-53/工数null/全HOLD/451は不変更。新WBS受入0。
