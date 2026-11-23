# 原JUnit出力欄の文字型検証

Program NK-OPS-001、WBS-G09／G08・SS354・451。Surefire 3.5.4のschemaは標準出力・標準エラーを文字型として定義する。 [Apache Surefire 3.5.4 XML schema](https://raw.githubusercontent.com/apache/maven-surefire/surefire-3.5.4/maven-surefire-plugin/src/site/resources/xsd/surefire-test-report.xsd)

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-G09-JUNIT021 | 合成suite／testcaseの標準出力・標準エラーの四形に、文字欄以外の構造がある | 収録を拒否し、終端JSON未生成 |
| PT-OPS-G09-JUNIT022 | escape済み文字とCDATAの既存XML | 1件、原XMLのSHA-256一致。収録後も同じbytesを検証 |

PG43590、source `d5c25fb648a9dfee87051758eab42740c10ece8b`。局所の工具試験30件成功。失敗・error・skip・未実行0。修正前は独立合成の4形が受理された。保存したProtocol元39 XML／171件でも現読取工具で原hash一致。実行済みの元結果を参照しており、新製品PTは0。元証跡の構成やschema番号の変更なし。BUG-3715／YKT-2915、全451は未受入。

- manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG43590-junit-text-report-current-fix-v1/manifest.json`
- SHA-256 `4c7dee01ef02615c4e5f5d753e819ec0deae35ad823c0e7beb19cfd7c7f83647`
