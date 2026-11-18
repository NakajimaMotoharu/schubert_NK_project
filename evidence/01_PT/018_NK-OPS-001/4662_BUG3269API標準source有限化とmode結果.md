# BUG-3269 API標準監視sourceの結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `8800ed7277964b28bc3cdce2e7cffcd021e2e5e2`。PG39356のAPIHOST001〜016は全16初回成功、失敗・エラー・skip・未実行0。004は二つの合成modeをbind／scrapeで拒否し取得0、016は元のlatch・二worker・各10秒・結果を保持して、worker終了確認後だけowner.close。元期待の逆変換一致、製品差0。PMD生9は有限worker、局所割込、GC所有移管箇所、静的適用0。

事前styleの重複1（BUG3270）と先行証跡のGit未固定（BUG3271）は失敗証跡を保持し、理由定数化と元receipt収録で是正。二件とも製品試験起動前。PG39360独立は物理6・正CRC5、旧支援5点は同じbyte、試験再演0。PG39364で標準監視source本体の生46L/9M/1C/26B/231Iが全到達。GC等の同run生25箇所は未到達。全F03/451とYKT広域は継続。

Linux amd64、JDK25.0.4／Maven3.9.12／Micrometer1.17.1／Prometheus1.7.0、dev-foundation。[独立証跡](evidence/PG39364-f03-api-standard-source-finite-independent-v1/manifest.json) SHA-256 `9bc8ec6c7df4264886350de430c5aad18809f4e4e2b38fa6b28316c4ac813b46`。SDK11点実hash、command、XML、終端、CRC、静的、生coverageを参照可能。
