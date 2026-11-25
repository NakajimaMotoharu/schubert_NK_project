# NK-WEB-002 管理フォームworker 単体結果

製品Core `cf08e414be9f877b851a387704350d5e7c980209`、対象 `c9426b589321874af323f590b1ad08f5482aa40c`。PT-UCREATE-DOM001～008、PT-UDETAIL-DOM001～008および試験補助三件は最終同じJUnit実行で全成功。失敗・エラー・スキップ各0。最終二画面の合成DOMは既期待値を照合。製品Javaの追加計測は0。

試験補助のみ同一exec L12/M3/C1全到達、branch命令0。正規Maven処理資源34のバイト一致、Spotless四入力、Checkstyleおよび最終SpotBugsは指摘0。SpotBugs初回は分析用class path書式不備で終了2。ソース固定で静的だけ再測定した。元二fixtureのPMD原指摘10は修正後2、補助・補助試験を含めた生19は個別適用性の判断待ち。

BUG-3846の局所再試験は完了。他Web画面の横展開はYKT-2997。実HTTP・DB・権限・六製品451と正式F03は別。 [PG45324](evidence/PG45324-current-admin-render-worker-fixtures/manifest.json)
