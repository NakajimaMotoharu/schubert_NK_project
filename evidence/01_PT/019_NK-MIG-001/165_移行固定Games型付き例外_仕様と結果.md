# 移行固定Games二行と資源・時刻

NK-MIG-001、WBS-F03/2-2-b、SS343 SSC403/SSC473、V004、PT-MIG-GAMES001～020。元明示SQL、独立固定二行、UTC instantと別offset、getIntとwasNull、例外同一性、ResultSet→Statementの一回closeを継承。四直呼出のSQLExceptionと有限Future/終了待ちのchecked型を明示。代理getIntではnull時の固定0をIntegerで返し、非nullの既型を保つ。元期待列・製品コード・Test IDは同じ。

PG42868、ad8edd7566、2026-11-23 JST。現JARの一物理とfixture三物理で通常20件全成功、F/E/S0。JDK25、Pacific/HonoluluでUTC即値を検査。行66、method10、class1、branch30、instruction213を単一JaCoCo runで全数到達。CRC 48a4a771276261de、61/61 probe。Checkstyle0、SpotBugs生1は故障注入用Throwable、PMD生9はSQL NULL一、worker五、代理classloader三。包括例外5・不要box1を是正し、BUG-3637／3638、YKT-2857の局所確認を完了。実DB・全製品の正式451は継続。[PG42868 manifest](evidence/PG42868-fixed-games-ordinary-v1/manifest.json)
