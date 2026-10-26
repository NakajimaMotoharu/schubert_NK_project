# PT-DB-INBOX-125 UID期待値独立化・実行結果

2026-10-26、仕様074、BUG1794～1797/YKT1545～1548。branch dev-foundation、実行source d17f122d2026b804be626bf7a3b76912923bd240。Main変更なし。主G03.01/原P003-05関連追加費0、群2299、開始.5/1.5/4pp cap10。

## 結果と独立根拠

PG10132の単一method/単一suite、PT-DB-INBOX-125は実行終了0、成功1、failed/error/skipped/aborted0、新Test ID追加0。自己TempDirのJDK unix:uid→unsignedを独立expectedとしてdefault/三arch factoryの自己UIDと一致。OS/arch/symbol欠落・nullの既負例も同method内で保持。三archはhost上admissionでありARM機実証ではない。自己tmp後条件empty=true。

PG10135独立post実0：XML/exec/当source全四physical Main/CRC/session PG10132-UID-ORACLEを照合。LinuxInodeSecurity CRC9c747bb4a32c8770、LINE35/74・METHOD7/13・CLASS1/1・BRANCH6/32で全四100%未達。三no-Code interfaceは四0/0 N/Aで合格率へ換算しない。他八Test methodとaccessAcl/readAcl/requireNoFileCapabilities/readOnlyFilesystem/capability/failureの実行probeは各0。API/Web/Batch/Bootstrap禁止probe0、native資格取得0。

PG10136実0：正常六module compile/NullAway-Werror実0/PT0、全Main1843 byte不変、Test1931中当outerclass一件だけraw差/他1930同byte。既全source tokenは新oracle/throws/独立定数を逆変換した上で旧ddと一致。literal metadata三vectorは製品PTではない。旧ddの52PTを当source成功へ流用しない。

## 静的解析・工具失敗と是正

PG10126 rawPMD6/CS0/processing0/rawexit1：既四適用違反をBUG1795へ修正前起票しTest-local同値定数に集約。PG10127 rawPMD2/CS0/rawexit1はDoNotUseThreads二件（267/283）、standalone method所有executor/TWR/futureでJavaEE文脈非該当。raw1を0に偽装せず当source hashへ個別根拠を束縛。並行methodの動的検証は今回未実行。

PG10130初回はnumeric61のtoken展開誤りでpreflight1/JUnit前、BUG1796起票後に元工具/失敗をPG10129へ保全。既lexerで再token化し三vectorと全旧token guard保持、是正版preflight0の後、製品試験は初めて一回実行。

PG10134はJaCoCo不存在overload analyzeAll(byte[],String)で集計helper compile1、BUG1797/YKT1548起票後、元helper/script/receipt保持、別V2でanalyzeClassへ一行是正。PG10135は既存一回分のXML/execを読んだ集計だけで実0、試験再演なし。元compile1はPG10133へ回収。

## 証跡・再現

公開基点 `../018_NK-OPS-001/evidence/provisional/`。以下は各manifest.jsonのSHA256。

|段階|公開directory|SHA256|
|---|---|---|
|是正前static|PG10126-uid-oracle-precommit-static-v1|c3372346677df823f94b897de7408ba2c429daa146ec27d72b85f932b5d714c7|
|是正後static|PG10127-uid-oracle-precommit-static-v2|e41e9942ef8159c5e790e544ec151d08bc7c89c33b3cd74551529e2156378b32|
|正常compile|PG10128-uid-oracle-six-compile-v1|7738e9ba61b5166e1ca9ed2223f6c7ce494051c9837526df1b2f549a0b7a92be|
|token原失敗|PG10129-uid-preflight-guard-failure-v1|原manifest参照・元工具保持|
|preflight|PG10130-uid-oracle-preflight-v1|903994e5c0089cb146aa5beafc107ae6a990b76812866212420aa35f8402354e|
|JUnit|PG10132-uid-oracle-host-v1|433218f7037381741438e2c68b845c5758e2e5bb539a003d84542031907f7880|
|元集計失敗|PG10133-uid-failed-report-receipt-v1|986ea8e5bc0c22bcde57151b9f4a0b4f05d0627e8a7fdb2268fe9318ed2d1466|
|独立集計|PG10135-uid-oracle-post-v2|43685c265a5a73cc4a422ce75a7e52a795841282f2ff291dc16c1e7f70f2928d|
|source/static|PG10136-uid-source-quality-post-v1|f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29|

実command/開始終了日時/exit/stdout-stderr hash/固定input/expected/XML/JaCoCo依存は各manifest/公開receiptに記録。OS Linux amd64 7.0.0-38-generic、JDK25.0.4、Maven3.9.12、JUnit5.13.4/platform1.13.4、JaCoCo0.8.15/ASM9.10.1、PMD7.28/Checkstyle14.3。実行は固定source snapshotから `python3 -B tools/quality/pg10132_uid_oracle_host.py` が発行したmanifest内command。既成功の確認目的だけの再実行をしない。

raw UID/鍵/credential/秘密session/DB結果は保存しない。JVM計測sessionは非秘密測定ID。実VM/Root/cohort/ACL/外部process/DB/鍵/保留witness二fileは不操作。全451/全coverage/native/CHRは未受入、正式1964PT/53scope・個別17/190・工数null/QA051 finalを維持。
