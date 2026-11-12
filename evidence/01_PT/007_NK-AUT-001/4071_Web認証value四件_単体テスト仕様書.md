# Web認証value四件：単体テスト仕様書

Program NK-AUT-001/NK-WEB-001、P00706追加品質・P015共通value参照。対象ClosedWebAuthentication.authenticated/principal、SessionPrincipal constructor/accessors/display、SessionStoreException constructor/preserveFatal、InvalidSessionRowException constructor。SS314 §7.2.1/7.2.6、SS331/354・SSC328、451。原実装・現Main629不変更。前提と根拠: [PG26784](../018_NK-OPS-001/evidence/PG26784-web-login-independent-v1/manifest.json)のhelper4実測line32/method4/class2/branch35miss。補完を事前.1/.3/.6ppで別群に凍結、元190受入/業務scope変更ではない。

| Test ID | ClosedAuthenticationValueTest method | 入力・独立期待値と根拠 |
|---|---|---|
| PT-WEB-CLOSEDVAL001 | principalUsesLiteralNfcUnicodeAndClosedNullBoundaries | literal NFD→é、U10FFFF16個=64UTF8byte、65byte/空/末尾space/改行/上下孤立surrogateを拒否。username/role/context/loginAt null契約、固定値/role/時刻/identity/redacted display。Unicode正規化・UTF8 scalarとSS閉schemaから決め、Productionでexpectedを作らない |
| PT-WEB-CLOSEDVAL002 | closedProjectionRequiresExactTokenAndLiteralRoleAuthority | null/匿名はempty、USER/ADMIN→literal ROLE_USER/ROLE_ADMIN、標準authenticated/同principal/no credentials/no details/権限一件だけ許可。派生型/未認証/別型principal/credential/details/権限0・2・不一致は固定SessionStoreException。合成memory Spring tokenのみ、配備先権限を発行しない |
| PT-WEB-CLOSEDVAL003 | fixedStoreFailureConstructorsHaveLiteralRedactedDiagnostics | 両exception constructorが固定message、causeなし/suppressed0。DB/値/原因を保持・表示しない閉診断契約をliteral比較 |
| PT-WEB-CLOSEDVAL004 | fatalGraphOrderUsesIndependentIdentitiesAndCyclesTerminate | 手組したcause/SQLnext/suppressed循環と同一参照重複は正常帰還。直接Error、cause優先Error、next内cause Errorは独立に保持した同一Error objectを返す。返却・探索結果をProductionでexpected生成しない。実DB/cohort回収は行わない |

fixtureは全一class4method、thread/Executor/DB/外部接続/鍵/実sessionなし。実DB fixtureからmethodを抽出しない。元Provider5/Probe3と必要Login154を保持して166一runで検証する。全197physicalを報告し、未網羅を除外せず4coverage100%を要求。失敗/未実行/途中/別sourceは合格にしない。新4定義と既162実行を重複なく区別する。

事前static: 初回26796compile0/26798raw16（適用literal重複1）は保全、BUG2677/YKT2357修正前PG26802起票後独立ROLE_USERラベル定数化。入力/期待値/元8断言不変更。fresh26808compile→26810raw15適用0/CS/format0→26812 preflight fb2cb3e8。Main197の再buildなし、原source/byte/静的証跡を厳密照合。抑制/品質緩和0。

実行予定: source固定commitの後、`PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1345_web_auth_helper_qualifier.py run <固定source>`、同runのみ1348独立postへ。環境Java25.0.4/JUnit1.13.4/JaCoCo0.8.15、各ツールhash/実command/branch/終了code/XML/CRC/coverageはmanifestへ保存。仕様書作成時点で166は未実行・未受入。旧162は成功だがhelper不足のまま保持し、合成しない。後続実HTTP/DB/CHR/451/元190は本純粋value試験だけでは閉じない。


実行後追記: source840・PG26816全166真正0/PG26818独立0、全197physicalの四coverage100。詳細は[4072実行結果](4072_Web認証value四件・現全一六六_実行結果.md)。上の「作成時点未実行」は仕様確定時の履歴を保持。
