# BUG-3257 Web JVM・System metric fixtureの有限終了結果

Core `29f3b433952ad19d4ad34c4e1a31ed310bebde6a`、固定試験source `9dcc19553d5c8f5732b2cfdb2eb6e25ed79b56b3`。PG39114のWEBJVM001〜014／WEBSYS001〜014全28初回成功。失敗・エラー・skip・未実行は各0。各並行試験で64の独立ownerと元期待256/128、finally終了10秒を確認。元期待値と製品Mainは保持した。

PG39118独立で物理8／正CRC3。PG39120の対象生counterはWebJvmMetrics 15L/4M/1C/8B/87I、WebSystemMetrics 15L/4M/1C/8B/79Iの各全到達。補助HttpMetricContractは一部未到達。Root static適用0、PMD生14の個別根拠は5101。PG39104以後に変わった当二試験sourceのCheckstyleはPG39110で各指摘0。

Linux amd64/JDK25.0.4/Maven3.9.12/dev-foundation。command、入力、各XML、単一exec、CRC、hashは[PG39120](evidence/PG39120-f03-web-jvm-system-finite-independent-v1/manifest.json)、SHA-256 `0fb8c113b430b6bd31cd0d67c4bbc3425ea5b52fcbbb91f08e2ccf9e0920afc6`。実Scrapeと全F03/451は未受入。
