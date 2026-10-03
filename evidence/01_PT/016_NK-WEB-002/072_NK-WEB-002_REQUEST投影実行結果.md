# REQUEST投影実行結果

保存時検査：REQ010-wire.expected/actual.bin はUI235の固定長2336byteと末尾X項目space paddingをそのまま保持する。`git diff --cached --check` の当該2file末尾空白警告は仕様上のデータであり、trimや除外による改変を行わない。src/tools/documentsおよび証跡md/json/xmlの同検査はexit0。wireのbyte一致とhashは上記selected-v7 manifestに記録する。

2026-10-03 13:56停止追補：Source e06916a6a5134be025790a5b2fa7446a4c470b28 commit/push、selected-v7 actual exit0/13:33:34/3:26、179PT/26suite/FES0/static6zero、新6class line266/method47/class6/branch90全miss0。safe `evidence/provisional/PG442-request-selected-v7/manifest.json` SHA d46724733e2f1c033f76e0368ebab3a52ef97d0f4bcefdece84781ac0d085c33。REQ010公開synthetic input/JSON expected+actual/手書き2336wire expected+実独立JCE復号actual5fileは既存checked collectorでexact inventory・独立offset・literal JSONを照合保全。

全6freshは利用者のOS停止準備依頼でBatch MaintenanceRunRetirementTest中に所有Mavenをpidfd TERM、actual exit143。完了XML2494/382suiteは全run合格に算入せず、未報告/未実行も合格0。safe `evidence/provisional/PG442-explicit-pause/manifest.json` SHA b48257fa682228706bc8c137ee33778bb93a84bcdd23dd7c517a30511578fc37。WorkPG379/pg442-six-full.log・停止json・pg442-interrupted-host（classes6/exec6/生成XML5）を保全、正式/native/full source acceptanceは未完了。BUG573～593/YKT414～418は修正sourceを固定した全回帰/native必要範囲が未達のため対応中を維持。停止/guest/保全/次再認証は456先頭参照。QA047～050の後続承認と最新main c47f1744cを適用するが、承認を実装/PT合格に置き換えない。

selected-v6はX9をN9と誤期待したBUG593でactual exit1/13:28:05/Web113-F1、safe `PG442-request-selected-v6-failed/manifest.json` SHA cad6f4cd7cc2492508e6c10398ecf3d9a42e0e9dd379033cce3f75c623e38147。Production/上位oracle型は変更せずUI235/SS322のX右space literalへ是正しv7で再試験。旧failed証跡を上書きしない。既存品質工具017/019は別に1/105 canary成功、Production PTへ加算0。最初のdiscoverは対象0/exit5で非合格、実file別実行結果はWorkPG379 pg442-evidence-canary-017/019.txt。

2026-10-03、SSC172173/PG-D354355。製造/独立3新suite＋既存producer→worker実broker/API SQLを実装中、まだ受入0/Source未固定。design-only PR3/source47f87e1/main0414f1e90の公開はProduction/PT/native受入ではない。PG441 Source de6 full3013・全6bytefreezeは別のUser入力成果であり本producer成功へ加算しない。正式run24/1964PT/53scope/48.3%不更新。

| Run | actual結果/対象 | 証跡 |
|---|---|---|
| compile-v1 | exit1/12:19:37/7.633秒、未参照scope TWR warning/BUG579、PT未実行 | 下記v1 manifestのcompileAttempts/raw log hash |
| compile-v2 | exit1/12:20:41/12.001秒、fixture public factory/非deprecated/switch誤りBUG580、PT未実行 | 同上 |
| compile-v3 | strict全6 compile exit0/12:22:00/8.190秒、PT未実行/合格PT0 | 同上 |
| selected-v1 | exit1/12:25:57/2:50、Protocol16/Storage8/Bootstrap7/API31/Web104/F11/E0/S0、Batch/staticWeb未到達、全run合格0。BUG581属性redaction1、BUG582 shared Logger fixture10 | evidence/provisional/PG442-request-selected-v1-failed/manifest.json SHA256 a0cf660b24c30f96d63e257fa25bd48491a55cfc388298a9d96a59519cd5fe7a |
| selected-v2 | exit1/12:34:04/2:35、16/8/7/31/Web107/F2/E0/S0、Batch/staticWeb未到達、全run合格0。BUG585 native charset後body1179 vs framing込み1191、BUG586旧固定UUID SQL | evidence/provisional/PG442-request-selected-v2-failed/manifest.json SHA256 12044d786313f992e18d592d3e72f93a110d93a5207ee1b46b704822e1ddd4b9 |
| selected-v3 | exit1/12:53:03/1:57、Web compile失敗/BUG588、Web/Batch PT未実行、合格run0 | WorkPG379/pg442-request-selected-v3.log、private原文はGit非格納 |
| selected-v4 | exit1/13:07:12/2:50、Web113/F1/E0/S0、BUG592 client reset oracle、全run合格0 | evidence/provisional/PG442-request-selected-v4-failed/manifest.json SHA256 01b8b9c9727580b2ae53706378f92ab771a497046c19093fa847289b641e322d |
| selected-v5 | exit0/13:23:21/3:38、179PT/26suite/FES0/static6zero。ただしproducer bytes-only overflowのbranch1が未実行、coverage/完成認定0。既存elapsed-only/両overflowに対しbytes-onlyの独立境界を追加する（未実装TDD/coverage不足であり新障害としない） | WorkPG379/pg442-request-selected-v5.log SHA256 67057d07b2a7e5db389b0108ffc28decf9ad9b6d63fe5c76c8f554e9a3a65fc5 |

selected-v6は同26suiteをfresh clean実行中。公開synthetic REQ010のliteral JSON/手書きUI235 offset2336byte/実独立JCE復号/SQL後条件を5fileへ出力、既存collectorへ独立offset照合・exact inventory/hash採取を加える。v5の結果を変更後sourceへ流用せず、source/toolsをactual終了まで固定する。

rawはWorkPG379/pg442-request-compile-v1～v3.log、pg442-request-selected-v1/v2.logをprivateのまま保持。安全manifestはcounts/class/method/type/time/hashのみ、failure原文/stack/stdout/private値を削除。実行HEAD e3183cfa8563345e0cf59cbb052b412b015b793f+dirtyで、起動時のdirty各file hashは未採取のため後sourceのhashを遡及して付けない。再試験/coverage/full/source固定/native/全Web/正式は未完了、F/skip/not-runを成功化しない。
