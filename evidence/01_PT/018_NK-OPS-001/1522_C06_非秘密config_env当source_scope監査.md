# C06 非秘密config/env・当source scope監査

## 実結果

6954 reader exit0、公開 `evidence/provisional/PG6954-c06-public-config-current-v1/manifest.json` SHA256=5611a35e37534c2130d626545052ffd107aa324fed9b282816f00cdb250afe6c。全七source/当archive/git/485と正本一致、三env固定宣言・四YAMLのkey/type inventory、当元三caseを一意join。管理三/pyflakes0。設定/既Test/source変更0、再実行/実credential・鍵・配布先/Unit/VM/環境/権限操作0。scope根拠一つのみ、全contract/quality/実分離配布はfalseを維持し、実装/試験済みのRoot成功へ推定しない。

群1760、WBS-C06既枠.25/.6/1.5pp先行。SS352§11/SS342 SSC080/SS343§4～5を正に、Git上の非秘密七templateだけを読む。実credential/key・配布先・runtime・環境・権限にはアクセス/変更しない。PGはsource全値が固定URL/limit/period/path/version名/default等の非秘密宣言であることとenvの固定性を点検し、現在のartifactに変更は不要と判断した。暗号鍵実体の安全配布/分離をこれだけで認定しない。

## 対象と独立期待値

API/Web envは各固定一行SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk＋LFのみ（SS342 SSC080）。InspectorはDB URL/公開fingerprint version名の二行symbolic template、render後は既専用parserが検証する。ここで実port/database/key version値を配布しない。common/api/web/batch YAMLは既flat JSON-scalar部分集合の一意nk keyをinventory化し、タグ/object/list/nullを許容したYAML parserを追加しない。このinventory検査は全setting schema/value conformanceの代替ではない。

全七owned sourceと三既Test sourceをe7d64/PG6930 archive/git/current/485へ一致させ、origin/main8b919の正本352/342 hashへ関連付ける。全required inputはpublic Git fileで、credential file referenceと実体を混同しない。

|Test ID|当原method|既独立oracle|
|---|---|---|
|PT-OPS-API-CFG-006|ApiNonSecretConfigTest.opsApiCfg006ShippedTemplatesMatchApprovedDefaults|common/APIの既手書きGOLDENを独立JDK SHAへ計算しparser出力へ比較|
|PT-OPS-WEB-CFG-006|WebNonSecretConfigTest.opsWebCfg006ShippedTemplatesMatchApprovedDefaults|common/Webの既手書きGOLDEN・独立JDK SHA|
|PT-OPS-CFG-001|InspectorStaticEnvironmentTest.canonicalFixtures|symbolic renderの固定二行・未render拒否・port/version正常境界|

当全4222の原資格728682a9/cases692fcd4dへsource/method/XML hash/PASSを一意joinし、再実行しない。API/Web env二つは当readerの固定byte検査、batch.ymlはこのbounded三method集合に直接templateを読むcaseを未確認として残す。他の既存証拠の不存在とまでは断定しない。

## 残範囲・判定

local scope一criteriaのみ。全値/全roleの実使用、AES/HMAC/current/previous分離・rotation・配布/実owner/mode0600/ACL/nlink/private runtime/LoadCredentialは未確認で、C06 contract/quality未完。C02のLoadCredential sourceやC08等へ追加費0の参照が必要であっても、real配置/鍵へ自動進行しない。Source scalar/defaultの確認を実readinessや資格発行にしない。

予定command=full PYTHONPATH下 python3 -B tools/quality/pg6954_c06_public_config_scope.py、new-only PG6954-c06-public-config-current-v1。管理三/pyflakesを先行、結果/hashは後記。新JUnit/実測coverage/受入/正式/工数率/PTALTへの加点0、Current/実鍵/原本/全HOLDを保全する。
