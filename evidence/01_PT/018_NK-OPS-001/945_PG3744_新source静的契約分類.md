# 新sourceの原規則・契約に基づく技術分類

NK-OPS-001/F03、PT-F03-CONTRACT-3744、source7fff、SS311/324§3.1/342/343/354/451。固定PMD原raw1840は不変更、抑制/除外/規則変更/再実行0、適用違反の確定総数はnull、F03未受入を維持する。

PG3744 actual0：元3730 report/source全849 SHAと3734/3738実current source/独立XMLを照合、全1840のID/path/sourceSHA/座標を保存。旧sourceの239判定を単に貼替えず新sourceで原vendor定義/承認SS・POM/各statementを再認証した。

| 技術判定 | 件数 | 根拠 |
|---|---:|---|
| J2EE前提非該当 | 239 | DoNotUseThreads238＋UseProperClassLoader1。原規則はJ2EE管理serverを前提、SS311/342は直接Java service/shared lib。設定/POM/非managed配置不変 |
| validation label FP | 1 | 元label codeと独立JCE fixture/canary SHA不変、current全体でも固定nonce/圧縮/AAD golden実行 |
| STRICT EOF validation副作用 | 4 | RequestLogDetails/BrokerJournalEvidence/ReleaseInventory/SessionAttributeCodec。固定Gson STRICTのroot後peekはEOFか例外、独立trailing/malformed負系current XML成功。検証を削除/無意味な到達不能比較を追加しない |
| null wireの必須区別 | 2 | CanonicalFieldのnullable defensive copy/return、SS324 null lengthFFFFFFFFとempty0、独立null/empty/OpenSSL vector。empty置換は仕様違反 |
| 所有権transfer sentinel | 2 | LinuxSystemdQueryは確定closedだけpending解除、unknownは保全。InspectorAesCredentialは所有移譲後local参照解除でfinallyの二重wipeを防ぐ。境界/例外/aliasのcurrent独立Test |
| 未分類 | 1592 | 残るcatch/resource/synchronization/identity/serial field等。正当/障害を自動で決めない |

純classifier1は別source/未知module/managed環境/根拠欠落/別XML source/未審査行を拒否、各判定にqualityGatePass=false/rawWarningRemoved=falseを保持。実current XMLに結ぶnamed witness9、Production Test新規加点0。原vendor/全指摘を保持し、判定だけで品質PASSとしない。

manifest d85ddf48c5f680316c6f56bb3b54211e487b1f0823aac404ced5f7112a0157f2、全判定元 eb809ca4ad78f36e869c805f4407fb6e37596dea2aaeca82964c0c7269e70113、公開PG3750/classified-248-findings.json（全248source/座標/根拠/独立TestID/XML SHA）とtechnical-triage.json。正式/17受入/工数率/QA051finalに変更なし。
