# 608 SSC242 完了原本INVALID配備・unused候補配置

2026-10-10。Program NK-OPS-001/pg863_stage_candidate_v6・pg866_unused_candidate_post、SS343/354/SSC242/QA047、BUG974～979/YKT743～748。production e016/PG857はfresh六3541PT・静的六0のHOST_ONLY資格済、正式/native未受入。管理検査をProduction PTへ加算0。

## 独立oracle・試験

STAGE863001: 同before全24/564・ten32設定・原本tree・runtime空、実生成validate_baselineをliteral fixtureで正常＋9拒否。STAGE863002: dev/ino/uid/gid/mode/nlink/size/mtime/ctime九属性を独立列挙し各変更拒否、atimeだけは対象外。STAGE863003: strict32の集合順・空ExecStop、欠落/重複/未知/異常dependency7拒否、空値はactualtyped DBus Array署名確認（expectedから補完0）。STAGE863005: actual generated tenRefをliteral十Unit順でLoad/Ref→全採取→逆順Unref/busclose、body失敗伝播を確認。実親起動/業務操作0。

実command: `python3 -B tools/quality/vm/050_s1/pg863_stage_candidate_v6.py preflight` 0、`python3 -B tools/quality/vm/050_s1/pg863_stage_candidate_v6.py` 0、`python3 -B tools/quality/vm/050_s1/pg866_unused_candidate_post.py` 0。v1～4は各1・v5は読取preflight1で不合格保持、成功へ混入0。host/VM Java25.0.4/Linux、既存toolchain記録維持。配置actual source5243bdd11d5977658e1df210be6382bf9b75aa11 / branch dev-foundation、2026-10-09T17:44:21.033719Z～17:44:25.895166Z、4.861447s。後条件独立866は17:45:44.701361Z/4.208719s。

## 実結果・証跡

unused `/opt/schubert-nk/releases/0.1.0-PG862` / sourcee01612fcd7f2752df5ae0836b78538fd5e87f120 / BOM20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe /187artifacts・28SQL/29historyを配置し、signature Ed25519検証0。current832/BOM8bcbと原本DONE37356f…・startup47/8bINVALID・全24-564・全32・Backup・runtime空・全十kernel停止は不変。start/reload/stop/DBwrite/DDL/承認公開0。

private W=`/home/mini/codex/project1/work/pgpt-runs/PG379`、旧partial/credential/raw byteはGitへ格納0。v6log SHA5e0353b2155018f32e56a79c7fdb9726c961371c13b2716bfd2020bc79046071、v6safe SHA2369323d0321bcf767585be8a2c499f781f10bf26f16a72ec86eb222011fcd8c。BUG979: v6safe.run literalがv1のままなので、旧safeを不変更保持し866が実slot/operator/logをjoinした補足で是正。866log SHA11b326e39f63c6cf478bd7c7f4fe807bc2f3222b6b0c070b8c7e4d2f8d131c3d。

## 未受入

SSC242正規code-onlyのnewINVALID有限出版・両RODB/同Session/tenRef/heldFD全scope、独立post、fresh noargs親真正DONE/ownedstop/当nativeは未実行。全Java四100/正式/CHR-L01最終は未完、QA051比較保留。初回newrunがALREADY分岐を使わなければ同JST日再runの直接検証を別に必要とする。設計only PR79/main56b7ba4b458ffbef1191d7befb7cc91309b993e0公開済で、製造受入ではない。
