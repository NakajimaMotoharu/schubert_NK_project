# 1190 Protocol残重複fixture一括・全module通常PT結果

2026-10-27 04:00 JST、1189仕様/event2469。host source `5cc74a2e437d19b22b07eb9a57c8d04414109e9b`、Main logical source `21d7c30425e7aa9ce435e808035a94fa4d75c93b` 不変。BUG1869/YKT1620、主責F03/P00103/P00201/P00301参照費追加0、開始2/5/9pp cap10固定。元見積り/v3残予測、正式1964PT/53scope・個別17/190・工数nullは変更しない。

当scopeでは11Test fileに意味名のprivate固定String59を導入し、元494参照を同値置換した。Production/他input・golden TSV/独立expected/否定assertを不変にし、独立逆展開で確認。原Protocol107指摘＝既Semantic十＋不変97、不変97＝本duplicate59＋他rule38。実アプリ挙動の障害発見とTest保守規約の是正を分離する。

| 証拠 | 真正結果 / manifest SHA256 |
|---|---|
| PG10773 formatter後plan | 59/494/11、`08aa28e9d97072c21bd14b3181605165349b6be04dfe8f577fb1c5883ff39751` |
| PG10774 独立逆展開 | actual0・33反例、`b2e54df0e380e0afbd37e2bcfeba1cd752940ccf1d869cef60c322ef5271f5f4` |
| PG10778 六正常 | actual0・PT0、`f0b3a2df7892710085ec00739c49c8d0a6d0a7da8d3dc9d4ccee8d75b6214462` |
| PG10780 PT_DEFAULT preflight | actual0・102method/22Test class/23source固定、`13470c5ac83be631a73f3e7caf506ce88dfe29b3d5ecd5695a7af8c53e20a97f` |
| PG10782 元JUnit | actual0・102件/22suite、`c4b328b524e3ebb362d4398e9b430df5ea7890474ea169ce94deda4aab16ca5d` |
| PG10784 全Protocol静的 | raw1・PMD38/CS0/処理0、`cf78f966e0e8d185dc00049a52172c45d01c8c3bbd362017291551ce5473c2e1` |
| PG10786 独立post | actual0・完全176/CRC/session、`e2977b3ce5d49057733b753925f3b678a59b72fb53fbfabeb659cf169912d6fd` |
| PG10788 trace / PG10790独立 | actual0、`8d3395bd2abe8826e6eb5ad085aeaddb803c10aa57e644bdb265f8f78ab2d416` / `61d23f9bb2a56f24a07672a55b7e7ab9105cd8f781e76e9cb9145dc19a03fbcd` |

PG10772は整形前の同値変換成果として歴史保持、整形後sourceへ流用せず10773へ別固定。10772初回generatorはJava固有escapeを全てJSON decodeした工具誤りでpatch発行前1/OUT0、BUG1870/YKT1621を先行登録し完全target token一致へ修正。失敗SHA `b4360154e79f43c121fbb3e729c6a95356431aa57eaf56ed603086ea35753136`。10774初回の反例生成はassertEqualsがないTestで未変化guard1/OUT前、BUG1871/YKT1622先行、失敗SHA `e2210173eccf76a85dd9706858a41a885797714ecd1118798b0f7db138e0da88`。全Testに存在する@Testのmetadata-only改変へ訂正し、実Testのdisable0/三反例×11拒否を確認した。工具手戻りを製品試験失敗や元計画の新規消化へ計上しない。

通常PTは変更11Testと関連するProtocol module回帰/完全counterのため実施した102methodであり、確認だけの原巨大回帰再演ではない。PT-PRO-FIX-001～102は10780 cases.jsonでclass/method/path/source SHAへ一意対応。独立golden TSV/offset literal/JCA digest/JDK時刻、295 named field/69型/79optional/四空型の独立public API binding、境界/異常/null・例外identity・byte tamper・有限並行を元Testのassertで検証した。全scopeのoracle最終認定を102成功だけで代替しない。

preflightに固定したProtocol-only jar/Test/JUnit/jspecifyの閉じたclasspath、公開固定resourceの読取、ByteArrayと自作有限stream、固定enum serialization、Protocol public constructor/getter反映、八own threadのtry-with-resourceだけを使用。実DB/JMS/HTTP/VM/Root/実file/鍵/credentialなし。最大48MBのメモリfixtureを含み、専用JVM -Xmx768m/ja-JP一回、outer own timeout、parallel/autodetect extensions無効。保留Graph9等の抽出/別経路試験ではない。F/E/S/aborted/container failures0、flaky/retry0。OS Linux/JDK25.0.4/Maven3.9.12/JUnit5.13.4・Platform1.13.4/JaCoCo0.8.15、branch dev-foundation。日時/実command/環境/own PID親/exit/XML/input/expected・actual対応/exec hashはPG10778/80/82元manifestとSLOT `work/pgpt-runs/PG379/pg10782-protocol-fixture-batch-host-v1` に保存。

| 完全Protocol artifact・当source一exec | covered / total | missed |
|---|---:|---:|
| line | 3480 / 3480 | 0 |
| method | 743 / 743 | 0 |
| class | 159 / 159 | 0 |
| branch | 1014 / 1014 | 0 |

完全物理Main176＝JaCoCo解析169＋無実行memberのpackage-info七。七はflags5632/SourceFile/field0/method0と五negativeで確認した注釈metadata、実行code除外0。解析169の標準counter0/0 classもJSONへ保持。全Main1843byte不変・変化Test classは当11source由来だけ/他byte不変を確認。session PG10782-PROTOCOL-JP一・CRC mismatch0・禁止域classload/probe0、旧exec/二Locale/旧sourceの合成0。これはProtocol artifactの四counter100%実測であり、他module・全Java・native・451/全Programの受入宣言ではない。

全Protocol Main/Test静的は重複59消滅、他38を保持、CS0/processing0、rule/抑制変更0。未分類を適用違反0とも合格ともしていない。次の同module品質対応で文脈非該当と要是正を分ける。traceは11SHAだけ更新/他972全field・原主責費/UNKNOWN二/全旧runtime保持、今回102実行/完全counter100を別資格へ。八metadata反例/所定audit前後1同HOLD。全G13/G01/F03/451、QA051final、元安全HOLD、未読保証不明1847を不変更とする。

共有used17→17/残83/reset1793599188/短期非提供ordinaryAllowedtrue/券0、丸め0pp≠専有0、実token N/T・専有費null。usage cursor `46033a5c42091b99fc01b6b8095194beb8b1e8854839983011a9df5b7ad87cc7`、期間内explicit usage未提供を推測0埋めしない。own compile/JUnit/reader全真正終端、外部所有UNOBSERVED_HOLD。通常小受入/commitで停止せず、残38の具体source/rule/contextと必要PG/PTへ継続する。
