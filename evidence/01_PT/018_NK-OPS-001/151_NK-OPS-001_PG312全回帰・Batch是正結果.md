# PG312 全回帰・Batch oracle是正結果

D02/04/05、SS331343/SSC095096。全回帰triggerはV023 security/DDLと共用JDBC資源処理。正式run24/source858713c/1964PT/53scopeの認定とは別。

| run/source | 結果・証拠 |
|---|---|
| 092ad15d5、Node PATH欠落、03:01:54 exit1 | Protocol80/Storage149/Bootstrap135/API742成功、Web555 error2、Batch未実行。BUG287/YKT220。次test前に5module264JUnit＋4coverage採取、provisional/PG312-regression-Node-RED/manifest.json |
| 092ad15d5、Node24.19.0指定、03:20:52 exit1 | 全2161実行、Protocol80/Storage149/Bootstrap135/API742/Web555成功・5module static0。Batch500のBAT153/214だけ旧SQL件数22期待でfailure2。BUG288/YKT221。次test前に6module323JUnit＋5coverage＝328file採取、provisional/PG312-regression-Batch-RED/manifest.json |
| b131c5a18eb8faebfa877d05a7fdaff96f3484b6、03:29:31 exit0 | test-only Batch2箇所current23へ是正、Storage149/Bootstrap135/Batch500全784 failure/error/skipped0、static0。98JUnit＋3coverage＋3static＝104file採取、provisional/BUG288-batch-GREEN/manifest.json |

修正前仕様は017023/BAT153・017041/BAT214。独立current oracleはV001～023 SQL23件、SCHEMA0は除く既定queryを維持、歴史target022と旧migration全hash/後条件は不変更。Productionは092→b131の全byte不変更。別runを同source全6合格へ合成しない。元4JDBC classは全counter missed0をfull Bootstrap135内で再確認。

whole coverage未達: Bootstrap native7line/3method、API/Web main各19line/3method/1branch、Batch native17line/13methodが残る。RootReader/MorningDB/Worker concreteclass byteはPG311/PG309 native証跡と一致するが、単独native合成で全scope/全業務起動/実NK CHRを認定しない。自動生成除外・未知到達不能扱い・期待値をproduction実測から作る変更なし。

manifestにOS/JDK25.0.4/Maven3.9.12/Node24.19.0、branch/source/command/日時/exit/loghash/全filehash/件数/coverage/BUGを格納。native exec/credential/password/token/session/key/DBdumpはGitへ格納しない。保存XMLは公開fixture/診断のみ、credential等固定pattern scan0。RED XMLの元provider診断末尾spaceはbytehash保全のため改変しない（通常source/doc diff checkとは区別）。R2業務process/R3実NK CHR未達、正式中心48.3%据置。次はPG313承認署名・全BOM・schema期待・親backup開始前接続。
