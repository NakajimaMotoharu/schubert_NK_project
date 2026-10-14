# 817 Expiry実broker配送同期・再発防止

Program NK-OPS-001、ArtemisExpiryPurgeClient.observe/purgeObserved、Test.opsMq026RealBrokerRemovesOnlyActualExpiredMessage/PT-OPS-MQ-026、RD MQ009/OPS009・UI251・SS321§12/341§9、BUG1245/YKT1011。主担当WBS-P017-11、共通費二重計上0。event0706のP01803は誤った担当表記であり、後続eventでP01711へ訂正する（元event不変更）。

## 独立fixtureとoracle

固定2.56.0実Artemis、元production broker.xmlのsecurity/RBAC/Address/Queueと一時ディレクトリ、各秘密はメモリだけ。Test-only queue executor gateで送信後の非同期配送を遅延させる。旧expireReferences(null) expected1はiterator配送前に実0となる。PG2690v2で元assertionのAssertionFailedErrorを再現、合成Main改変0/agent0/PT・coverage加点0。v1 Spotless拒否はJUnit未実行で保存。

是正Testはgate期限10秒、entered/complete各5秒、gate解放finally、monotonic到着期限5秒/到着一件をassert、flushOnIntermediate latch5秒/flushExecutor成功をassertし、実Expiry移動件数1を維持。messageのLong.MAX_VALUE expirationは手動force-expiryを周期短TTLと競合させないfixture-only入力、Production TTL・再送・scan設定は不変更。受信先queueもflush後に一件/iterator/実broker _AMQ_ACTUAL_EXPIRYを観測。期待は独立SS七日から等しい境界保持0、+500µs選択1、+1ms選択/削除1・afterCount/Bytes0、maintenance session生存/不要management address0。Productionでexpectedを生成0。

元固定cutoff1789603200000のfake算術、null/malformed/count/byte drift/overflow/provider/unknown primary identity及び権限の既存oracleは不変更。v1是正はqueue flushのみで到着前count0になり失敗、別source/別namespaceに保持し合格へ補完0。v2は到着と中間配送の双方を期限内確認して旧障害の再発防止を同caseで実行。

## 実行・結果・後続

command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg2692_expiry_fixture_selected.py`。Source2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0、Production04207efc3（Maina79と同byte/資産新候補）、LAN固定JDK25.0.4/Maven3.9.12/Artemis2.56.0/JaCoCo0.8.15/SpotBugs4.10.4.0、source/root/envは工具に固定。

PG2692v2 actual0、05:54:23.711177Z～05:55:09.813698Z、11PT/三suite/FES-flaky-rerun0/Batch静的0。依存三moduleはcompile/test-jarだけ・PT加点0。Expiry class L65/M9/C1/B44、全missed0。独立全11case/三XML/hash一致。公開provisional/PG2692-expiry-selected/manifest.json、私有元XML/logはLAN同run保持・raw export0。

YKT全対象：期限入力setExpiration/expireReferencesはsrc Test全検索でこの一classのみ。ExpiryManagementAuthorizationTest一PTは空queueで権限判定、message生成/force-expiry0のため配送競合非該当、実再試験0。UnknownBoundaryTest四PTはproxyで型/例外identityを検証、実配送0のため非該当、実再試験0。ReadinessClientTestはqueue存在だけ・配送/expiry0。他JMS fixtureはconsumer receive/待機を使い、当force-expiry/iteratorの対は存在しない（全検索結果に基づく）。検索だけの完了0、当再発防止＋RBAC/unknownの実11と必要fresh全体で閉鎖する。

全2650は3666/541/F1/exit1・Batch静的未実行で保存。PG2694/2695はactual0/全3666-541-1643/static六0/FES-flaky-rerun0、05:58:07.745377Z～06:24:19.516336Z/1571.770959秒。当11caseをfresh全XMLへ独立join/hash照合しBUG1245/YKT1011当fixture対象閉鎖。full-qualified-manifestの全三XML/hashとqualification/source/archive/hashを参照。新candidate native/実Browser/global100/正式1964-53/全leaf/IT-STは別未完、旧回帰/旧nativeを新Test sourceへ加算0。
