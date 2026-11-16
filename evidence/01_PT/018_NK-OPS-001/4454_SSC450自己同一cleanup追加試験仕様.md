# SSC450 cleanup自己同一例外の追加PT仕様

BUG3136/YKT2607、SS366/450、Program NK-MIG-001・owner/cost P01903。既4453と原160Test本文・独立期待は不変更。旧PG36898の80成功はbranch2不足の限定履歴、正式/全品質未合格として保持する。

PT-MIG-ASSETSELF-001 / AssetStagingSelfSuppressionTest.assetSelf001SameBodyAndCloseObjectNeverSelfSuppressesInEitherOwnedScope。メモリ内java.sqlインタフェースProxyのみ、driver/DB/VM/native/file/Root操作なし。Statement scopeはprepareのsetQueryTimeout、ResultSet scopeはtransferの最初のaudio countのnextで独立に作ったSQL/RTE/Errorをthrowし、その所有closeでも全く同じオブジェクトをthrowする。二scope×三型を一JUnit定義とする。

期待値: 同一primary参照、suppressed.length0、getAutoCommit/createStatement/statement.closeは各1、ResultSet scopeだけquery/next/result.close各1・Statement scopeは各0。timeoutはliteral30、最初のSQLはliteral SELECT count(*) FROM schubert.audio_files。Connectionへのclose/commit/rollback/その他操作はfixtureが拒否する。期待をproduction methodから生成しない。独立same-object identityと資源counterで自己抑制の未成立二branchを検証し、catch NPEやprivate ctor呼出・除外でcoverageを上げない。

新1＋既160＝161を新sourceの同一JVM/execで実行する。全六source/追加NoCode9/必要全helperをphysical集合へ保持、当六sourceの未filter line/method/class/branchを100、全componentの未達は別に残す。既Column/Constraintと後三のself-suppression条件は全12siteの実counterで確認。旧80/既未実行Data80へ算術加算やexec合成をしない。metadata/Source/Core/Unit・全TestID・Rootflags/static/CRC-init/raw/資源後条件・command/exit/hashは確定profileと各manifestを正とする。追加予算/SV変更なし、現A1.2/cap4内の品質是正、原F03 C2.4不変。
