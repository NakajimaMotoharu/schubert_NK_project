# API process Resource限定実行結果

2026-09-27 16:24:16 JST、PG288、exit0。PT-OPS-API-RES-001～006全成功。source SHA-256 `bc0646bae131d6c14d2e9ffc3eddf94ffb7f644f38eca3eab7b3d04eb7cebf64`。instruction187/187、line37/37、method11/11、class1/1、branch0（分岐命令なし、例外経路は001～005で独立確認）。初回testCompileの型推論/fixture hook不整合、および固定70byte helperを混合password/key bufferへ用いた試験側失敗は合格へ算入しない。混合buffer長を各取得arrayの実長で確認する既存ServiceCredentialSetTest helperを共用し、全zeroのoracleは不変。

同一選択runは21PT（Resources6、DBSource6、APIMain4、CredentialSet5）、failure/error/skipped0。019 collector負canary103/103。追加Test ID/ownerは009/022/019へ登録し、正式run後まで不整合を先送りしない。

API mainのnative経路は本Resource scopeへ結線したが、最後の未結線拒否callbackは実OS credentialを通過できていないため、現時点のmain coverageはinstruction7/line3/method1未網羅。088の旧main hash/100%結果は変更前の時点履歴であり、このsourceを正式合格としない。次は共用bootstrap境界、root/Ops gate、schema、実起動へ進む。全正式認定と全体進捗加点はなし。SSC084対応中、PGPT/IT/ST未完了。
