# Web停止owner private lock/待機表現・限定結果

2026-10-25/group2114/PG-D641、仕様1882。source64446a9f8901084a4ad7eba1f66ae975eb2bbdea未配備。private Object monitor→ReentrantLockの既install/close二箇所、IRQ catch一区間returnだけを変更し、外retainUnknown永久loop/例外範囲/既finished/installed/非interruptible reentrant排他/ownership/期限は保持。current sourceの新WLCLOSE004＋必要旧3=4/1、F/E/S/aborted/not-run0/CLI0。caller monitor保持中にも自己Executorのcloseが完了することを独立future/停止値で確認。実Hook/install/TERM/UNKNOWN interval/VM/Root/DB/nativeは未実行HOLD。

| 公開manifest（evidence/provisional配下） | 結果 | SHA256 |
|---|---|---|
| PG9246-web-life-lock-six-compile-v1 | normal六0/PT0/format-NullAway有効 | 989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46 |
| PG9248-web-life-lock-host-v1 | 普通4/1、session PG9248-WEB-LIFE-LOCK | e5908bd0113157f4002dcb38ef04e9530d4f6a9877b362ea87fc9b8a1186e977 |
| PG9249-web-life-lock-static-v1 | raw CLI1/PMD8-exit4・CS0/SB0、対象private synchronized/empty消失 | f3ab4a4d689eb0ec618eb1247d596c67aaae90dcd5ee4b1257ea82a78ee3b91f |
| PG9250-web-life-lock-measure-v1 | whole Web一Main L30/58 M7/10 C1/1 B6/14、四100=false | 54fc9529a931f5a7c73802ba7818a5946e3821d24aa9afafafcc202e33227667 |
| PG9252-web-life-lock-trace-v1 | 全1843/旧1842同byte・254canonical/五arch0/9metadata反例・raw8個別判定 | 70f008f4256751e5bf4ecc0baa9e398dc715643cbbff8eb1380927fbfb7d49b6 |

各実command/時刻/OS/JDK25.0.4/依存/source snapshot/XML/exec/CRC/終了codeは元begin/stages/hashへ結合。型/通常fixtureを実Main/nativeの証拠へ変換しない。PMD8は現Web.bootstrap ownerのThread7（vendor J2EE managed-component前提が当direct-Java WEB ownerに非該当）とexact owner identity1を、raw行/source/Unit/SS342 main8b/vendorへ個別結合したもの。raw CLI1/4は保持、ルール抑制0/PT免除0、qualityGate=false/全Program PT/四100/451未完。旧API7や別source coverageへ合算しない。

traceでsource差を宣言したprivate lock/finally release/IRQ returnと新004に限定し、旧3Test本文を完全保持。全物理差WebLife outer一だけ、他1842同byte、旧254canonical/cost/basisは完全保持。owner/costP018-06/groupchangeP018-06、参照P018-05追加費0・歴史配賦変更0。未知owner/欠測counter/old exec/省略class/別packaging/別Unit/owner identity変更を受け入れない。停止途中のUNKNOWN区間を実行したり正常化していない。

## 障害/横展開の限定状態

BUG1743とYKT1494の対象Web二lock/IRQ empty三行はsource64446a9f8で是正、normal六・普通4・CS/SB0/対象指摘0/最小source/全byte/traceまで確認。APIは既AtomicBooleanで同private monitor原因非該当、batch ProcessLifetimeなし。YKT1493追加IRQ対象のsource/静的再確認も終了。ただし実install/IRQ catch/UNKNOWN保持分岐PTはHOLDで未実行、これらの台帳状態はSTATIC_FIXED_PT_HOLDのまま、全横展開完了や障害CLOSEDへ読み替えない。再発防止は004と9metadata反例/当static・token保持、未実測分岐は後続条件を維持する。修正commit64446a9f8、関連原BUG1742/証跡1881は歴史保全。

開始.5/1/2pp cap2固定、fresh60→60（2026-10-25 01:24:34 UTCに観測＝10:24:34 JST）丸め共有0≠専有0、実token/N/T/工数null。usage2e2b0c048d1655bc5e61f8b3b462d93a5169b42d16b74e78d446229e9d822552の不完全欠測は0補填しない。元90捕捉下限85・不明2/正確累計null/80大型抑制・保全buffer2。技術一意879=856四100部品ID/42Main＋部分23（Life10/Main9/Web4）、formal1964PT/53scope/原190新受入0/QA051final/G078379・原/v4/v5/保全物は不変更。

通常保存後は元90予算内の短い許可品質工程/不足通常PTを継続し、実VM/Root/DB/鍵/配備/拒否対象未特定操作のHOLDを解除しない。過去group2113のquotaAfterObservedAtUTC=01:17:00は手動の分bucketでAPI由来の厳密時刻ではないため、厳密時刻はnull扱いに追記訂正する（fresh60残40/共有1という端点観測自体は保持、元eventを変更しない）。

## BUG1744/YKT1495・群終了の入力/出力分離

計測OUT-v1へquotaを先に保存したため元pg9254 scriptの新規専用guardがappend前に拒否。旧script SHAfc3681159c58d69c7812cac79e43f19b542fb1846384528612ee677ce4139109/元失敗/旧quota SHA2c3965ead318fe1b70359dbfaa241ce3d0cb60185b32c5b8e4f6ed73ee0fa71dを保持、製品4/normal/static/trace再演0。新V2 SHA0ac4aaf2636d5d2980ff84c8c89b9be060093e0d79cef65162ccfcec5059baf0は元quotaをread-only pinし、新OUT-v2だけにmanifestを生成、前後quota hash同一。PG9254-web-life-lock-metrics-v2/manifest.json SHA9562107a87f06d653ab57715d61a3c836d7b39fec7d686af84b8fa0587c63723、元group END不存在を確認後PGPT-20261008-2115一回だけ追記、前述時刻精度訂正も元eventを残して記録。

追加qualityはPython astでV2のgroupBoundary guard式だけを抽出/compileし、独立fixture四つ（events空=true、同group END=false、foreign END=true、同group START=true）へeval、4/4一致。工具main/追加appendを再実行せず、実eventsの当END件数=1/event2115を別読取確認。対象9204/9218/9226/9240は事前quotaを各metrics OUTへ作らず同原因非該当。新V2/旧quota/source/eventの整合と再発防止を確認してBUG1744/YKT1495工具scope CLOSED、完了日2026-10-25、修正commitは当1883保存commit。全Program PT/native/451には拡張しない。再現はPYTHONPATH=tools/quality:tools/quality/vm/050_s1のpython3 -Bで当V2のast.AssertからgroupBoundaryを含む一式だけを評価、tool呼出しによる二重event発行はしない。
