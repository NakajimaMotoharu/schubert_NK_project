# PublicPermitRecords原八・現source資格結果

2026-11-01/3268/PG-D1048、Source6b53/HEADb9abfb2d1c64ef34b083585b3ab47f8af7facf54・dev-foundation。JDK25.0.4/JaCoCo0.8.15/normal14216、source六module SpotBugs14224指摘0を既同sourceで照合（PMD全体/F03/451合格とは別）。Main/Test不変更。

| Test ID / 原method | 独立入力・期待根拠と結果 |
|---|---|
| PERMITREC001 literalRecords | 手書きNKEPOCH INVALID/ISSUED・NKPERMIT byte全体/順序/field、PASS |
| 002 syntaxFailures | 欠落/重複/順序/8193長/非ASCII/未知magic・固定IOException/cause無し、PASS |
| 003 identityAndHashFailures | zero/非正規UUID・broker ID長/大小文字/hash長/各field閉集合、PASS |
| 004 stateTransitions | INVALID/ISSUEDのdigest有無/二回値遷移を拒否、PASS |
| 005 issuedBinding | 手書きgoldenを独立JCA SHA256、boot/epoch/run/cutoff/activation不一致、provider失敗固定例外、PASS |
| 006 cutoffContract | 年0001/9999・microsecond境界/範囲外/非正規formatとrun UUID zero許容、PASS |
| 007 nullAndOwnership | 全境界/各record構成要素null・copy/元byte不変/返却byte変更独立/redaction、PASS |
| 008 concurrentSnapshots | 自己四thread・32call/全Future回収・同独立literal Permit値、PASS |

private data/秘密key/credential無し。valueのissued/verifyIssuedを実許可発行/署名/配備/原本認証/退役へ拡張しない。再送は純粋関数の同値照合であってJMS/運用retryではない。原whole全312Test/274Main/二dependency本文をfresh確認し同byte固定、ExpectedをProduction encodeから生成0、原八再演0。

| provisional配下/manifest.json | SHA256 | 真正結果 |
|---|---|---|
| PG16775-public-permit-records-fresh-review-binding-v1 | 4d07207f07d0fbd79308c42ee0ed62030aeaaff1fa66364d305a47b59ba3aed7 | 全review/sameSource固定・実行0 |
| PG16776-public-permit-records-original-eight-pt-v1 | a4c752dbdd39d0188790d6bca3a8f3972be2bf72579e215789fd99b71370189b | 8/1FES0、session79730終端3efae3 genuine0 |
| PG16778-public-permit-records-original-eight-post-v1 | 36dbe471c5a24e52443f79c739a4f16afc70a1f1a90d66f55f80287bc09488f8 | 17783終端84291b genuine0、単一exec/CRC0 |
| PG16780-public-permit-records-original-eight-independent-v1 | c573adf569f7e604fbe9ebefdc16732b6e1fadabf5d681dc3d0e762ba492f6bd | 98f72a genuine0、独立49/八oracle |

commandは各pg16776/78/80のchecked entry、actual argv/環境/fixture/Main/Test/XML/exec hashはmanifestへ。全一Source五physical=四Code＋一NoCode DigestFactory（flag1536/Code無し、除外でなく全closureへ保持）、line119/119・method25/25・class4/4・branch30/30、miss0。State単独branch0は自然非適用/理由付き、全Sourceのbranchは30/30で適用100。公式生成filter不変更・manual除外/exec合成/旧Source成功転用0。crypto/publicDigest/synthetic UUID=true、実key/permit発行公開退役/DBVMRoot/native/Service/network/file/認証0。四held六native無probe・RootFailed五/Cycle23/inactive五無record。正式1964/53/QA051final/工数null/451/全HOLD不変。
