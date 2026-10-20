# 1267 Expiry監査readのowned JDBC複合故障

Program NK-BAT-001 / ExpiryAuditRepository.read・JdbcResourceFailures、DAT009/OPS009/UI251、SS331SSC200/332SSC063199/SSC310調査、BUG1530/YKT1290、PTPRE032。主費F03、群開始0.5/2/6共有pp固定（event1456）。正常DB/SQL/rowshape/借用transaction・successful usingJdbcのSSC304 TWRは不変更。正式/実VM/native/CHR/代替PTに加算0。

EXP310001: 固定run UUID12345678-9abc-def0-8123-456789abcdef/cutoff2026-09-12T15:00:00.123456Z、CLEAN_EXPIRY handle42/attempt1/started=cutoff+1秒。借用ConnectionはautoCommit=false/readOnly=false/READ_COMMITTED。参照queryは固定4Boolean（false,false,false,true）の1行を返す。audit queryのResultSet.nextで独立AssertionError primaryをthrowし、そのResultSet.closeは独立SQLException secondary、Statement.closeは成功。期待=SS332既優先表に従い同じprimary instanceを伝播、raw secondaryを保持せず新固定BatchRepositoryException一件をsuppressedへ追加、一度ずつclose、Connection変更0。ExpectedはProduction helperを呼ばず固定同一性/固定文字列・class/cause/suppressedで検査する。未知ErrorをSQL closeへ置換したBatchRepositoryExceptionは不合格。

初回は当Main不変更+新Testだけのsourceを固定、純proxy1＋全六module既guard12の計13/8suiteを通常offline host PTで一回実行する。fixtureはpublic固定markerだけ、実DB/原本/VM/権限操作無し。source/archive/日時/toolchain/全command/実exit/XML/実counterはWorkPG379の新only red manifestへ保存し、実行結果は別記する。未実行/終了欠測を合格へしない。

EXP310002（設計確定後）: test-only JdbcResourceCasesの独立68合成（2scope×SQL/IAE/ISE/NPE/Error primary-secondary・同一Throwable・成功body/close異常）を全検証。EXP310003（同）: 正常empty/監査snapshot、null resource/mandatory projection、不正値・provider unknown identity、body成功close故障・acquisition失敗・各一度close/借用Connection不変更。68はJUnit一件の内数、追加68PASSにしない。既Expiry/retained SUCCESS/callerの影響suiteとYKT対象も個別確認し、必要source全体・nativeは別終了依存に保持する。

coverage要求はline/method/class/branch100%。選択fixtureで届かない既program分岐は未達として表示し、redのcoverageや旧source成功をgreenへ輸入しない。実環境の全24DB/Root所有/原本Backupを本proxyから認定しない。SSC310は独立反例と現SS適用性の確認後に詳細確定・設計だけmainへ公開し、それまではoracle/正本変更0。

2026-10-20確定：独立反例1268を受け、SSC310はdesign-only e48bca17d/PR165→main615d40b1eefcc5f3a65a29e4556e803ca188ceb4へ通常merge/remote確認。EXP310002/003は上記独立期待で実装、初回3個のJUnit合計（68合成は内数）。既BAT287 readRuntimeの未知同一性期待補正はSS332/354明記後だけ実施、他固定拒否は維持。新source greenは148/16・既六guard＋実Expiry/保持監査/SSC304TWR/DB session/caller影響群、各case名は原source宣言と実XML一対一、原red/旧3976の算術加算0。全実counterと終了コード/静的・source/run整合を別結果へ記録する。
