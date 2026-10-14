# 新boot署名候補unused配置・独立post

2026-10-15 JST。SS343/353/SSC247/249/264、PT-DEP-2832001、PT-OPS-2834/2836/2838/2840。Productionを変更せず、cold専用の一経路を接続した限定技術証跡。正式1964PT/53scope・WBS受入leaf差0・工数率nullは不変更。

## 固定入力・独立期待値

新guest boot `79a3260a-e16d-42bf-942a-b914ed144c28`。現配備Source `04207efc3ad78bca75942153a90c70985064c988`／PG2654／BOM `552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37`。候補Source `a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25`／PG2802／BOM `37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863`、署名SHA `93a6032cb7c3a15f010e521cea1da78ff6a975e2123462e70d808c59cfc10d11`。

834の真正有限prepareと別postを前提にする。全24表・32設定・Unit metadata・原本/Backup/credential実体の期待値は停止前に保持した独立read-only原値。今回のtmpfsは当bootで取得したprepare after `387f826c7603b7f2cdbaf39784a0996290ab0ae6b25832fe356dcbd24035bc9b` を期待値とし、旧bootのtmpfs・owner・permitを復元しない。候補は署名済みmanifestの全187 artifact/SQL28/schema028/history29、byte/size/名前/mode/UID/GID/ACL/新規signature0400/Ed25519を独立検査。Productionから期待値生成0。

## 試験・実行

| 段階 | command（正規PYTHONPATH付き） | 実終了 | 対象/根拠 |
|---|---|---:|---|
| 独立source契約 | `python3 -B tools/quality/pg2832_network_cold_unused_sources_test.py -v` | 0 | 三試験、current/candidate局所scope、欠落重複null/誤hash、権限変更禁止 |
| host frozen ABI | `python3 -B tools/quality/pg2834_network_cold_unused_compile.py` | 0 | current PG2654 JAR、Java25.0.4 `-Xlint:all -Werror`、独立Java引数/null/境界/mount/original golden |
| 完成graph | `python3 -B tools/quality/pg2838_network_cold_unused_test.py -v` | 0 | stage/place/post役割、当boot・Source・別post全namespace/static0 |
| 新規工具/input転送 | `python3 -B tools/quality/pg2836_network_cold_unused_stage.py` | 0 | 118file、worker/permission未発行 |
| 正規unused配置 | `python3 -B tools/quality/pg2838_network_cold_unused_place.py` | 0 | 一回freshM-A/readonlybatch/advisory/十Refs/保持FD/原本Session、全scope正常 |
| 独立full post | `python3 -B tools/quality/pg2840_network_cold_unused_post.py` | 0 | current全原値/24/32/187/原本Backup/oldDONE/12roles二読、candidate全187・署名、親/backend/advisory/FLOCK/Refs正常解放 |

全Python commandは `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime`。tools source `242b09f1089a84c0d2ccbdfc9af66b96cb7d1f00`、dispatcher/post source `bbb5274fb`。OSは既存専用隔離VM、JDK25.0.4。実行時刻は私有frozen manifest `2026-10-14T18:36:21.354026Z`～`18:36:27.171785Z`、他各actual/job証跡は下記保存。

## 証跡とhash

私有実体は `/home/mini/codex/project1/work/pgpt-runs/PG379/`、公開は本書のみ。secret、DB行実体、credential/key/raw token/native streamはGitへ格納0。

- frozen `pg2834-network-cold-unused-frozen-v1.safe.json`、immutable工具 `pg2832-network-cold-unused-tools-v1`。
- stage `pg2836-network-cold-unused-stage-v1/manifest.safe.json`、工具archive SHA `a01d7a41d4d52c6338d69f4e9574058de80b309abf4c36ff2d839c9e5ea2fdc0`。
- place `pg2838-network-cold-unused-owned-place-v1/manifest.safe.json`。payload `7ae2680a6030f278e0374f32746f848257bbae31d6cdaba008f65fd45fefd11f`、log `26335c3ccd637d44f27bd59f7edc3b68f5859e81f5f35c95989204ec784a9f24`、guest after `6f7367fd3fa5aa46aae17a65964c2f93d0b3c6e1e95448dbcbc090dc0e8a122a`。
- post `pg2840-network-cold-unused-independent-post-v1/manifest.safe.json`。payload `20025633efe43cbda25648045d2cdbc8c373cfcb7f0ae0608b8861cc9b4ab243`、after `c9aa34a32b6d2c411c23489016e1c365f12fc27653d16c7d5aa69028a7c6130a`。current/原値は2830 afterと完全同値。

作成途中のsourceガードでは一意marker・indent・bundle未注入・graph入力期待のTDD不合格を先に検出。actual転送/配置前に解消、これらを合格へ算入0。BUG1251/YKT1017 Mainの複合closeは別未完、工具ガード成功で閉鎖0。

## 未完と継続

候補unused配置のみ受入。current symlink/approval/startup epochは未変更、Root/Backup/ADMIN/起動/停止/reload/DB業務書込0。新source nativeやcoverageを旧Source042と合算0。次はcold candidateRO/独立post→有限正規公開/全phase別post→newa9 ordinary/真正terminal/24/全体seal/ownedstop/当native/実Browser/CHR/四counter100/451/trace/引継ぎ。QA051 final保留。
