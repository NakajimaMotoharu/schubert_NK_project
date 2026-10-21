# SSC329 borrowed green / authentication JDBC boundaries

元6552/25460はsourceca6268514608106a76314d5167632bde91805f69、2026-10-21T15:18:06.579935Z～15:21:02.439180Z、archivec0384cc98fb89e316c13ee173792b4d6b1d42610ff1ad3b2bb34f72c1c428e9d、23/9/phase0,0,0/六gate0/F/E/S/flaky0/sourceFixed/真正0。6554/74675原資格6346bd42cd80f2d742d49b4f7de907b71a0e5f6d1c13b95c1e52c2e76072fbdaで851Main/1667physical/六Jar/XMLを結合、五outerだけ変更/残1662同byte/PMD raw1365/CS0。元red二Test bytes固定。各borrowed9のmode・資源後条件とcoreboundary2を確認、選択coverageは各class/global未100。旧4073/他source結果へ加算0、再演不要。

## 次の認証三境界（実装前）

PT_DEFAULT。BUG1592/YKT1345/SSC329、SS312/314/324/332/354、NK-AUT-001、UI226/234。群1625/.5/1.5/4を継承し、SQLCATCH074～076の適用性を確認する。通常業務/SQL/認証許可/session上限/再送間隔/権限は不変更。

新`AuthenticationJdbcBoundary329Test` PT-AUTH-BOUNDARY329001 lockForAttempt、002 recordFailure/recordSuccess（共通record）、003 authenticateのcritical audit。自己所有JDBC interface proxy/有限SQL・固定UTC/typed rowsだけを用いる。3mode=SQL primary＋statement.close Error、SQL.next.causeだけError、非fatalSQL-next cycle。前二modeは元Error、最後はliteral `authentication storage is unavailable`・cause null/suppressed0。各methodのprepare/execute/Statement close、借用Connection commit/rollback/close0を独立counterで確認する。

lockは最初のSELECT失敗なのでStatement1/ResultSet0、recordはaccount無/IP emptyからIP UPDATEで失敗してStatement1/ResultSet0、success/failure双方を別fixtureで検査。auditはuser不在ResultSet→IP作成→IP emptyのResultSet→IP失敗counter更新→audit SQL失敗、Statement5/ResultSet2各close1。時刻・行数を固定literalで供給、provider password照合は自己所有BiPredicate falseで1回、session発行0。入力char配列はError/非fatalとも全ゼロへwipeする期待を独立配列で確認する。

audit constructorの既AuthContextCodecは公開既知の全ゼロ32byte fixtureのみ、実credential/key/session/hash/ネットワーク/署名/認証回避を使用しない。codec所有はtry-close、暗号化/復号/session発行は当経路で呼ばれない。既原本/VM/Root/HOLDのアクセスや拒否探索ではない。

当3method＋baseline12=15/8、赤で三失fatalを予測（API停止時9/5、後続6not-run）。旧helperは328のsuppressed→cause→SQLnextを使い、新guardはLoginAttemptRepository二catch/AuthenticationService audit catchに接続する最小二Main。各元oracleを固定しgreen/原artifact→既domain・残mapper/必要当source全体に結合する。未実行値はnull、拒否代替/全113/正式の完了へ加算しない。
