# Web MediaDecoderの静的検査と通常試験

NK-MED-001、WBS-F03/2-2-b、UI237、SS333/354、451 §5、YKT-2863。PG42926、2026-11-23 JST、試験 `b1aa1bbbb1c6760fb7bef7eee36b2c73917d8124`。現Webの明示10 Main（既PG38162と同じ型集合）と現Protocol・Jakarta JMS APIで局所compile。元の二試験は固定JDK内callbackだけを使う。provider・外部接続・実認証・FileStoreなし。旧MediaDecoderNamespaceContractTestは履歴を保持して現通常PTから撤去。

PG38170の非反射条件15件を採用。旧PG38154の9件と後続のcontext所有6件を重複させず、一つの現execで全15成功、F/E/S・対象未実行0。固定独立descriptor／wire値、並行、null・不整合・借用値保持とcontextの例外・消去境界を検査。初期preflightでは旧fixtureとの差を検出しcompile／JUnit前に停止した。d53bb9c2e8で例外宣言と合成fault型分岐を明示した現fixtureを照合してから検証した。NullAway指摘0。

PT-MED-STATIC004はfinal、private constructor一件、他staticを固定classfileから確認し、通常試験に加えない。当owner五物理（四CRC、ContextOperationsは自然にCodeなし）。無フィルター行118/120、method19/20、class4/4、branch36/36、命令546/553。残りはprivate constructorのみ。反射再演・元coverage合算・実環境検証0。F03・451・YKT-2863は継続。

実行環境・対象source・コマンド・原XML／元exec SHA-256は公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42926-web-media-decoder-without-private-reflection-v1/manifest.json` SHA-256 `f83c9319baef88b4988b10f8efa76472e47305cb46dccd3e7eebc0207c3a07b7`。
