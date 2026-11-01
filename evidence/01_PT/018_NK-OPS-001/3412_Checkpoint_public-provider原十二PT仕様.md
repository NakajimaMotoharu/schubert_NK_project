# 3412 Checkpoint public provider原十二PT仕様

NK-OPS-001/SYS002004/OPS009/TST004/UI212251/SS342343 SSC193/451・509、PG-D1098、Source6b53/normal14216/開始HEAD07a156ef10851c3d1bd350fffca303dc1ef2fcba、群PG17620/開始1.5-4-8共有pp cap10。原Test520行（SHA40d28e8f…）とMain253行（95d70220…）を全文読取、whole十二@Testを抽出/変更せず実行する。class名のNativeだけで拒否/許可を決めず、具体呼出しと副作用を確認。

## 呼出し・副作用・境界

Main FixedNativeCoverageCheckpoint/Point/PublicAgentと五抽象interfaceの全八physicalを分母に測定する。default fromCurrentJvm/fromCurrentTerminalJvmは現標準toolchain agentにreserved /opt profileがないことを原Testで確認→parse empty→open先頭returnでNativeCoveragePrivateFile.verifyPinnedAgent/export前に帰還。default PublicAgentは実JVMの非fixed CodeSourceをrequirePinnedSourceで拒否し、実RT.getAgent/実native exportへ進まない。残りは公開PublicFixture/metadata loader・fake Agent/Export、固定profile文字列のdata-only parseで、実profile発行/配備/権限/permit/原本/私有path/鍵/DB/VM/Root/Unit操作0。

public reflectionだけでprivate lookup/setAccessible/attach/resetなし。自己Test class resourceを四回読み、独立ClassLoaderでmetadata Classを四定義するだけ、CodeSourceが固定pathというfixtureを本物署名/hash/owner/OS権限にしない。自己executor一/四worker/32task・Future5s/TWRで一capture/一exportだけ勝つことを確認、実thread総数は未測定null。fake exportは公開7byteをMap等へコピーし実fileを作成しない。新fixture/held Testの部分抽出0。

## Test ID・独立期待

common922001: null role/phase等の固定IOException・causeなし/入力引数不変、未設定はOptional.empty。ncheck597005: 全terminal roleでもreserved agent不在ならempty/null role拒否。

ncheck597001: PUBLIC RT/IAgent四method順・fixture identity・version0.8.15/session固定literal/7byte {01 c0 c0 10 07 10 01}/reset=false/read1。002: constructor null三port・missing RT/IAgent/invalid型・class/source/reflective各故障を固定IOExceptionで拒否しprivate原因非表示。003: 三getter×null/Integer7/IllegalAccessを拒否。004: Object/no CodeSource/null location/foreign metadata pathは拒否、固定path metadataだけは受理（actual authority資格0）。

ncheck193001: 全service/phaseのdefault empty。002: fake四role/root前点・terminalの固定filename順と7byte/複製所有・ordinary argument literal・同point再利用拒否。003: version/session/変更途中/null/4byte/16MiB+1/header五箇所の12faultを拒否・export0/再試行data読取なし。004: null dependency/point・ordinary before-execは消費/出力0、terminalだけ一回。005: checked/unknown export identityを保ち再試行しない。006: 四worker32taskで勝者/agent読取/export各1、負けは固定IOException。expectedは手書きliteralとcallback countでproduction計算0。

## 実行と判定

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17620_checkpoint_public_provider_twelve_pt_v1.py。固定六normalJAR/SDK/JUnit1.13.4/Java25.0.4/180s・append=false新SLOT一回、既compile/static14224/reporter資格は参照し再演0。postで元XML/FESabort0・同session/CRC・全Source八分母/未実行Code・五NoCode、四held/六native/RootFailed/Cycle/既inactiveとNativeCoveragePrivateFileの不在を確認。未達は未達、実native/全451資格へ転用しない。結果/source/run/環境/command/exit/input/期待実値/coverage/hashは3413/3414、障害は修正前915/916へ。正式1964/53・工数null/QA051final/actual HOLDは維持する。
