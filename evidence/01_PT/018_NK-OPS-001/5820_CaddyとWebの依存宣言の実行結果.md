# CaddyとWebの依存宣言の実行結果

PG43734、WBS-C02-a、PT-OPS-UNIT-SUP006。JDK25.0.4、JUnit1.13.4、隔離した公開設定4資源。対象ソース、argv、XML、終了とSHAはmanifestに固定。コンパイル0、6件成功、失敗・error・skip各0。5件は元仕様の再資格、固有新規IDは1件。

起動用のService節は元bytesと一致。変更はUnit節の順序および依存に限定。停止・Web・Morningの既雛形は同じ。旧order28辺にWeb→Caddyを加え、循環0、合成逆辺は拒否。C02-bの実効設定、所有・起動／停止・実HTTPSは未確認。設定書式の試験であり、製品Javaのカバレッジは別。 [仕様](5819_CaddyとWebの依存宣言の単体テスト仕様.md) [再試験証跡](evidence/PG43734-caddy-web-order-current-readonly/manifest.json)
