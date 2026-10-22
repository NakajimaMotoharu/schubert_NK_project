# SystemdOwnedABI 原34結果

## PG補足：既設計参照v257との整合（原試験/期待値は変更0）

Mainの既Javadocが参照する[systemd v257公開sd-bus.h](https://raw.githubusercontent.com/systemd/systemd/v257/src/systemd/sd-bus.h)も追加のsource-only照合で確認した。公開header30597bytes/SHA17ecf87426e811161ddc225b7bc87a31886efa1ae3645d5939f976ae8d32f890の採用20symbolは、1476に手で固定したC ABI shapeと全件一致。残freeは元仕様の公開stdlib.h宣言でありsystemd header対象外。1476のv258.8参照はhost versionの更新/認定でなく公開ABIの補足で、v257と当採用宣言のshapeを変えていない。Production/全Test/原oracle/SS/実library0変更、追加PT0/library load0/native資格0。実配備libraryの世代・host ABI資格は従来どおり別未受入。

1476/PG-D501、P018-03、群1686開始低.2/標準.8/高2pp固定。Production Mainは01e41088cと全851/1667同一、Test込みsnapshot c45cd204ba1b049f39219ce58a1684ba9b07d9a6。新二Testを旧4184へ算術加算した全体合格とはしない。

元6740/session95205、UTC2026-10-22T01:02:05.849104～01:05:01.511241、175.662137秒、phase0,0,0/actualExit=mavenActualExit0、34/9/FESflaky0・sourceFixed/六SpotBugs0。archive659fb62c48f38c04cb75bd29fe5824c90940dcb040aba51c657ea6775ccb58c9、元manifest33683c2e0f451662f330959499e2691a0cbc41894bca6540b51b9d191fc32986。

原6742/session26481真正0、元source/run/archive/六Jar/XML・全851/1667を独立確認し、全1667物理byteが元01eの6724と同一、追加build/PT0。公開manifest5a7d26a79116236df9d0ca3598a3d41cb2bd97413d5e76070c8ca279a8192069、rawPMD1404/processing0/CS0・全旧診断identity不変。Nativeの原counterはL76/0・M6/0・C1/0・B26/0、四100。以前の非empty dispatcher M1未達は新独立正常21symbol二vectorで実行できた。通常JUnit新規二件であり42正常vector/21missingを個別件数へ水増ししない。

PGsource review cd183662の21CABI/lookup/失敗契約は正しくMain変更不要、全旧oracle/品質設定不変。fixture内全callは自己所有upcallに限り、失敗flag検査/無例外帰還/own Arena解放・symbol固有結果と引数順/bit/pointer、missing/unknown時stub0を確認。関連既loader bindは1476着手記録どおり未知symbolのみ、実bus/Unit/session0。実manager/native qualification/VM/Root/cohort/DB/鍵/permit/intentの所有成立は未確認のまま。

当snapshot全体回帰は未実施、global100/F03/CHR/正式未受入。次は1472の現原gapに限定したBackup request普通IO/metadata fixtureを追加し、同source必要全体をまとめる。正式1964/53・個別17/190・工数null・QA051final・PTALT代替0・全HOLD/原-v4は維持、通常区切り停止0。
