# 当source全3635・正常runtime検証（限定結果）

対象NK-OPS-001、SS343/353/354/355・SSC284・451。Production3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8、PG2126、Java25.0.4/Maven3.9.12/PostgreSQL18、dev-foundation。正式1964/53不変更、IT/ST合格0。

| Test ID | command／source | 結果／独立根拠 |
|---|---|---|
| PT-OPS-PG2300-001 | python3 -B tools/quality/pg2300_jdbc_host_integration_full_six.py、snapshot9c7fec35955ce44bbb1128a361af8d5eb439ade5 | actual0、3635PT/540suite/1643Main/FES-flaky-notrun0、六静的0、1553.770349秒 |
| PT-OPS-PG2301-001 | python3 -B tools/quality/pg2301_jdbc_host_integration_qualified.py | actual0、XML/static/archive/Main SHA/四物理差を独立照合。archive9e67723985c6f1989912597e9c38098ccee9156958daf428f92dbcd1212812fe、servermanifest a323cb7249c005d2d01e75c79619368ce81ab68f2eeadda7e5142d191a9944db |
| PT-OPS-PG2352-001 | python3 -B tools/quality/pg2352_current_runtime_verification_dispatch.py verify-runtime、operator e39202411d5622c4522c3c40ae30a036eb5fb846 | actual0/sourceQualified、2026-10-13T18:38:07.162005Z～18:38:46.461010Z、正常M/A/DB/Ref帰還・追加reload/業務write0。旧complete.private二フラグ不備BUG1237を別記し操作証拠へ採用0 |
| PT-OPS-PG2356-001 | python3 -B tools/quality/pg2356_current_runtime_verification_post.py、operator e392+是正WIP | actual0、独立元24rows/187署名/状態18/kernel・宣言triple+CLOSED及び承認Morning二delta・同runtime inode/hash・client/advisory/FLOCK/bus0。独立oracleは既封緘2348/2274・固定literal・SQL全column、Productionから期待生成0 |

2356はnullable/未知scope/未帰還を成功化しない。工具1fixture＋全payload compile/static/boundaryは0（ProductionPT加点0）。2352原私有receipt/sourceは不変更、同job再実行なし。旧2318/2332の143/UNKNOWNは歴史保存しPASSへ補完0。新fresh resume/新native/全coverage/CHR/trace未受入。coverage100未達・全leaf認定0。

私有原本=WorkPG379のpg2300-server-six-v1、pg2301-jdbc-host-integration-qualified-v1、pg2352-verify-runtime-v1.safe.json、pg2356-current-runtime-verification-post-v1。公開manifest=evidence/current-runtime-verification/manifest.json。秘密/raw DB/session/credentialは公開しない。
