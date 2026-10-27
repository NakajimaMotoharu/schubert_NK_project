# 2208 三role GC Fake例外保全結果

NK-OPS-001 / WBS-F03 / source `495313cd8e724d5f1906fca64d9d9fd3516aae50`、仕様2207。製品Main・RD/UI/SS/POMは変更なし。修正commitはこのsource、保存commitはGit履歴を参照。2026-10-27、PG11446の元実行から回収し、再演していない。

## 結果と限定範囲

- 三role各八、計24 Fake取得の例外cleanup guard。Fake.closeは開始時false、callback正常帰還後のみtrue。元42 methodの全oracle/順序/identity/期限を逆token照合、metadata反例63。新gc015016は各role二、計六。成功確認後の重複close抑止、fresh/既成功後のRuntime/Error失敗未確認と明示retryを独立count・identityで確認。
- PG11444正常六module compile/package終了0（試験0）。PG11446は元42＋新六の48件/3 suite、F/E/skipped/abortedすべて0、単一 `PG11446-GCFAKE-JP` exec/session。全回帰・正式451ではない。
- PG11448の実静的結果は終了1、PMD44（CloseResource30/DoNotUseThreads6/AvoidDuplicateLiterals8）、Checkstyle0/processing0。旧38を保持し新gc015016のCloseResource六が追加。条件付きfinallyがPMDに認識されないため、動作是正を静的合格に変換しない。抑制・不要な二重closeは追加しない。
- 全1843 Main byte不変、Test物理六差/他1956不変、由来は当三SourceFileのみ。同一execから完全API467/Web358/Batch645を測定。三GC Mainだけ四counter miss0（API L18/M5/C1/B9、Web/Batch各L15/M5/C1/B6）。完全三artifactはすべて未達、旧exec合算0。
- 文脈36（thread6/保持実GC3/即close3/旧条件Fake18/新Fake6）、duplicate8未分類。全raw保持、実行免除/追加PT/coverage/正式受入への加算0。新六は `PMD-NEW-PG11448-001..006` として別登録し元10690 IDを捏造しない。

## エビデンス（provisional配下のmanifest.jsonとSHA256）

| Test ID | directory | SHA256 | 実終了 |
|---|---|---|---|
| F03-GCFAKE001 | PG11442-gc-fake-guard-source-post-v1 | ee7e93ea6dd4a8444f60778b1742d568e5f9767dae016bddd3604f9b065c8778 | 0 |
| F03-GCFAKE002 | PG11446-gc-fake-guard-host-v1 | c849836c6b0356430eaaf4426718bc8307bc1d8cd5581eb659cd776e8a529e74 | 0 |
| F03-GCFAKE003 | PG11444-gc-fake-guard-six-compile-v1 | 0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb | 0 |
| F03-GCFAKE004 | PG11448-gc-fake-guard-static-v1 | 4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185 | 1 |
| F03-GCFAKE-POST001 | PG11450-gc-fake-guard-post-v2 | 2e62cc35fc6c916cce3a6cce92d5e6bcc63ba1fc0779dca4fdfc69b6864342d7 | 0 |
| F03-GCFAKE-ID001/CONTEXT016 | PG11451-gc-fake-guard-context-v3 | 6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb | 0 |
| 同・独立post | PG11453-gc-fake-guard-context-post-v3 | ab7430e60bc819fbe2d938d077999ad886e274ee449787e28e73441d3b88d0e7 | 0 |
| 原担当trace | PG11452-gc-fake-guard-trace-v1 | 6948323785d9859c81bee7e449fb538158bb95c91f5715571205a79ef2eada42 | 0 |
| 原担当trace post | PG11454-gc-fake-guard-trace-post-v1 | 70c29cb6a5809e344409533071f398435b3100528d75d2594cb7eb7dec4d4711 | 0 |

command/実日時/OS/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15/branch/source/input・XML/exec/hashは各元manifestに保持。postだけを新PTとして数えない。追加metadata反例は同postの `additional-negative-vectors.json` SHA `6a744607d65d59c5af8b8223f0a9fe963b72b52295b74dd03a01f56b9d37eb34`（座標三/cleanup basis九）、元post反例12と分離する。

## 障害・残件

BUG1913/YKT1662は24guardと新六独立oracleの当scopeを検証。BUG1914/YKT1663は予測20のpost v1終了1を11449 receipt `63b427ef7e1549583eddca28a65438922ef38df4e33808114bf412922c03b5e3`へ保全し新v2で実44を照合。BUG1915/YKT1664はduplicate本文の座標だけを実LEX literal/count/first line照合後に正規化。BUG1916/YKT1665は016 callback解除付きfinallyを厳密に区別。失敗工具v1/v2はbyte保持、元v2終了は未回収null（OUTなし）で成功化しない。後続indexの新六追加照合まではYKT1663～1665 IN_PROGRESS。

工数率null、正式1964PT/53scope・個別17/190・QA051final HOLD不変。Main四100を全artifact/CHR/native/正式受入へ拡大しない。外部所有未観測HOLD、保留二工具/Graph9/deferred8/原本DB・Backup・鍵・stash・baseline保全。次は現在index8912に当新六だけを追加し8918を元ID集合で実証、その後独立した残PG/PTへ進む。
