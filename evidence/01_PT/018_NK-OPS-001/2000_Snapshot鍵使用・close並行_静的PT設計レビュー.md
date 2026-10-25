# Snapshot鍵使用・close並行・静的PT設計レビュー

2026-10-26、文書レビュー群2256/WBS-P006-01、開始.25/1/3pp cap10。元群2254の1/3/8ppと費用/sourceを保持。HEAD8c2af892704b355fc5ae83be273756fcaf73a62a、Production/Main-Test source21d7c30425e7aa9ce435e808035a94fa4d75c93b。**STATIC_PT_DESIGN_REVIEW_COMPLETE。KEYLIFE001/002は未実装・未実行HOLD、BUG1775は仮説のまま未実証。同期修正/新Test/fixture/ハーネス/formatter/lint/preflight/compile/JUnit/JCE/並行実行/coverageは行っていない。**

## 指令と保存状態

継続的な停止時静的切替方針、およびPMO/hourly-monitor/static-pt-design-snapshot-key-close-20261026.txt（sha37cd5ea1170e7ec1719acb35e20ce2ec830b68d86b9dd5ad309b502ecbe79a31）に従う。failed turn01a1737c-d6fd-75d0-932b-49fe6a09b029、最後の可視failed operationはformatter/pyflakes/pg9892 witnessの一括command。PMOはturnのsecurity flagを確認、どのsuboperationが拒否されたかは未特定。当方に見える準備assertion終了1を拒否箇所や製品PT失敗と断定しない。元witnessの有効な動的結果は未確認、再現済みとも正常終了とも認定しない。

一括command/同検証/言換え・分割・別経路の再試行0。未検証WIP tools/quality/architecture/SnapshotKeyCloseWitness.java と tools/quality/pg9892_snapshot_key_close_witness.py は保全し、修正・再読取による原因探索・再実行・削除・配備を行っていない。Production sourceの差分0。外部job/VM/processは未観測HOLD、再付着/起動/停止0。

## 上位契約・静的事実

SS324§6（127～129行）はJDK Deflater level3、api-inbox-response-aes、Message/layout/version/owner AADと最大平文を規定。SS352§11.2（173～189行）はNKENC1構造、32byte key/12byte nonce、current write/current-previous read、unknown版拒否を規定する。

**SS343 701行のS3 assembly追補は、callback帰還前にconsumer等を停止してからcodec/root/DBをcloseする所有順を既に要求する。** 978行の検査process契約はprocess終了までcurrent/previousを保持し、途中close/rotationを禁止する。したがってkey-idと構成keyの一致が必要であることと、ownerがin-flightの途中にcloseしてもCodec自身が待つという追加規則は同一ではない。1999/PG-D675のread/write lease方針は未実装の提案であり、上位の停止順を置換する承認ではない。実callerが停止/終了を保証できているかは本レビュー外・実経路HOLDであり、保証済みともしない。

Main sourceの読取では、constructorがkeyをclone（56～69行）、encryptがensureOpen後にcurrentKeyを使い（70～120行）、decryptがcurrent/previousをselectKeyで選ぶ（122～200行）、closeが配列消去/closed設定を行う（261～267行）、ensureOpenがclosedを検査する（269～273行）ことを確認した。これらの対象範囲に使用leaseの同期機構は記述されていない。この構造だけで実callerの禁止順序違反や、実JCAが特定の結果を返したという事実を認定しない。BUG1775はSTATIC_CANDIDATE_NOT_CONFIRMED、五codec横展開YKT1526も未実施のまま。

## 予定Test ID・既存assertion・不足証拠

|予定ID/状態|要求・独立期待値の出典|既存sourceで確認できるassertion|不足・依存|
|---|---|---|---|
|PT-IDEM-KEYLIFE001 / NOT_IMPLEMENTED_NOT_EXECUTED_HOLD|SS324/352の構成key/AAD認証、SS343の停止→codec close。1999のclose待機は追加提案であり、既停止順との前提差を要整理|ResponseSnapshotCodecTest#fixedNonceCiphertextMatchesIndependentCompressionAndAadVector（70～116行）は別JCE/独立AAD/圧縮とのbyte比較、caller key/input不変、返却copy独立性。#identitySnapshotKeyAndLifecycleContractsRejectNullAndInvalidValues（233～307行）は順次close/二重closeと、その後の両入口拒否|既assertionは並行close・in-flight排他の証拠ではない。通常のowner停止順を満たす試験前提/責任を整理し、拒否scopeの判断が必要。再現、競合順、実key使用、thread終端、提案lockの正しさは未確認|
|PT-IDEM-KEYLIFE002 / NOT_IMPLEMENTED_NOT_EXECUTED_HOLD|SS324/352の異Message/layout/owner AAD、nonce再利用禁止、各caller入力完全一致。独立JCE/別AAD packingは計画上のoracle|既TestのstoredCiphertext（370行～）/independentAad（388行～）は標準JCEとpurpose/table/入力identityを独立packingし、Productionのencrypt/decryptをexpected生成に使わない。NonceFailureTestのRNGSCOPE001/002（20/25行～）はprovider失敗後zero12/例外同一性/入力不変|予定32callerの並行Test sourceは未作成。既逐次/異常providerの9件を並行独立性・nonce一意性・close時のleaseへ転用不可。今回の拒否検証を別名の通常並行Testとして再開しない|

既存のindependentAadは入力identityのgetterを読むが、Productionのaad/暗号/圧縮methodから期待値を生成するものではない。これは既fixtureの独立組立の静的確認であり、予定Testの未実装assertionを実在するとみなさない。Test ID二件は将来仕様の識別子だけであり、今回実装/Test method数へ加算0。

## 読取hash

- Main ResponseSnapshotCodec.java：bde8b74bd7b18d33bfbcd52d0a83a015e2b8badfca4821d06c48587166abedb6。
- 既ResponseSnapshotCodecTest.java：e3599816867e51871714a40e24518f3d52d74fa81a09bf3ce9cb9713f81f0f70。
- 既ResponseSnapshotNonceFailureTest.java：b754c08d4b25039e22327fe56959a3eac7a080126f6b68dfbe02aa4cf7fe4434。
- 1999計画：7b988e567a9f28d7fca2c4db7472ac5b24908534328a71e51a59e9a77b403d6a（本レビュー追記前原文を指す）。

上位資料の当読取hashは付属manifestへ記録する。最初のSS343 path指定は存在しないdirectoryで、inventoryから正しい340_batch・基盤のfileを解決して読んだ。これは通常の資料位置解決で、拒否検証の別経路再実行ではない。Main/Testの読取範囲を越えて工具/実process/秘密実体を調べていない。

## 未完と別作業

当reviewはPT_EXECUTION_EXEMPT/ACCEPTED_WITH_USER_APPROVED_PT_ALTERNATIVEの承認ではない。元9/2/Codec L154-M14-C1-B70四100/PMDraw3・exit1/限定適用性は1994の別目的の証跡として不変、KEYLIFEへ転用0。正式1964PT/53scope、個別17/190、QA051final、工数null、Graph9/実環境/F03 Root11/全安全HOLDも不変。

同検証は必要な平台/人の具体scope判断までHOLD。元通知は既に現存しないとの利用者回答を保持し、再提示・再現を求めない。上位の停止順を確認しただけでHOLD解除/同期修正不要確定/実owner gate合格にもせず、仮説の不当な試験前提を記録して保留する。

独立した次候補はG07の既公開残metadataとenum等の公開symbol由来の限定候補選定。元key-close実行/JCE/並行/lease実装・Root回収とは対象/手段/所有が別で、当拒否を分割して追うものではない。着手前に新群の許可/依存/具体操作を確認し、未確定なら実行しない。通常文書完了やPMO返答待ちで全体停止せず、正当停止条件まで既存計画内の独立PG/PTを継続する。
