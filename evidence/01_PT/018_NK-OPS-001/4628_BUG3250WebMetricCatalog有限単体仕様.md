# BUG-3250 Webのmetric catalog有限fixture

NK-OPS-001、WBS-F03/2-2／P018-09、RD MON005～013、UI252、SS351／352／354、YKT2387。対象はWebMetricCatalogTestの元WEBCAT001～014全件。Main二型および35routeのliteralは既[元仕様](2705_両Catalog単一exec全面測定56_単体テスト仕様書.md)を継承。API側の全試験、transport、配備、実サービスを起動しない。

WEBCAT014の事前条件は4worker、独立64task、各10秒のget。元七metric名と35route、HTTP1750、全39のゲージ／byteラベル、固定error・null・provider元例外・deepimmutableは元入力と独立期待を維持する。元実装のtry-withの暗黙終了待ちを明示shutdownNow・await10sの合否へ変更する。task失敗や所有終了不確認は合格に含めない。

対象MainをJava25のルート規約で当候補からcompile、承認済みSDKのhash、独立テキストfixture、静的解析、固定試験source、元全14と独立XML/CRC/生四を照合する。結果・hashは追記。従属のHttpMetricContract全経路やF03/451、実metric scrapeは別。
