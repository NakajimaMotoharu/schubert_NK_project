# Storage ResourceScopeの並行試験終了

RSCOPE001～008、IOFACT001～018、BUG-3279、YKT-2387/2202。元2733・3706の独立oracleを継承する。SS311/333/352/354、SSC063/308、OPS009/FIL001～009、UI237/251。F03/2-2、WBS-P003-08。

| 試験 | Fixtureと操作 | 独立期待値 |
| --- | --- | --- |
| ResourceScopeTest原8 | 合成close/actionと64仮想worker。各Futureを10秒以内に取得する | 返り値を入力の連番に42を加えた値と比較し、閉鎖64回と元の例外・null・自己抑制・重複順位を全件確認する |
| FactoryResourceScopeTest原18 | 元fixed 2worker二組、合成Token・callback・Latch。保有済みTokenの入れ子・並行handoff | 元の6操作順、別Token、二取得・ゼロ自動close、3×4例外優先表、nullableと全境界を維持する |
| 両原試験の終了 | 三組それぞれfinallyでshutdownNowし、10秒以内のworker終了を要求する | 終了しなければassertion失敗。Future待機期限、worker数、試験結果の期待値は元のとおり |

通常JDK、標準JUnit/JaCoCoにより、二class全26件を一度実行する。製品はResourceScopeと診断値の閉包。実IO、native、VM、Root、DB、broker、鍵、保留classのfixtureを含まない。試験改訂と製品Coreを固定し、Checkstyle、PMD、Java 25 lint、NullAway、SpotBugs、exit・JUnit・単一exec・物理CRCを照合する。生counterの未到達を残し、旧execを合算しない。コマンド・対象commit・結果・SHAはPG39426の公開証跡で記録する。
