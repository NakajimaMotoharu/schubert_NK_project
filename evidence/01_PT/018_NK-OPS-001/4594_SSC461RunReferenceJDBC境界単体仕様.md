# SSC461 RunReferenceRepositoryのJDBC例外所有と単体テスト仕様

F02-a／P004-03、NK-DAT-001／SYS-005、UI241/243、SS311/332、SSC448/461、BUG-3233・YKT-2680。借用ConnectionからRunReferencesを読む既存境界を対象とし、保守DBの実行条件・権限・SQL・引数・処理結果・想定失敗の固定診断を現設計から継承する。JDBC依存を持つBatchがBootstrap JDBC adapterを呼ぶ既存の有向境界に沿い、当該SQL例外1箇所の次辺を上位で保持する。

元独立仕様447とRunReferenceRepositoryPureJdbcTest全8を変えずに実行。独立Oracleは固定SQLと引数、固定Booleanと失敗診断、借用Connectionにはcommit/closeしないこと、行→文を一度ずつ解放、既知SQLに従属するErrorの元instance。各試験の正常、null、失敗と並行条件は元仕様へ一対一対応する。

Java25、同Coreからの固定source、厳格NullAway、全PMD policy、Checkstyle、SpotBugs Max/Low、元whole8、別後検証によるXML/CRCと未フィルタ対象値・公開ABI。未達と対象外の物理coverageを理由付きで記録する。実JDBC、実ファイル・Root・サービス・ネット操作は発行しない。単体の結果をF02全体又はP004-03の正式受入へ加算しない。
