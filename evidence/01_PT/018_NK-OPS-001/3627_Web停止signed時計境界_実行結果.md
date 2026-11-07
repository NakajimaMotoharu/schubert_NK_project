# Web停止時計境界の実行結果

BUG2409修正Mainは54d5c19da0117db49edff7b5ae46207fdee59acc、試験の独立expected定数整理は4c719e2aeb1dffaa6e7d0de6c451574cd896f192。正常Main入力1036件を全照合し、Test source変更後もMain全byteが一致することを独立確認した。Gitの異なるcommitを同じrunと呼ばず、Main source/試験sourceを分けて保持する。

| run | 真正結果 | 位置づけ |
|---|---|---|
| PG22008 / 元normal21922 | exit1、006一件/error1、IOException「Web stop unconfirmed」 | BUG2409赤再現、PASS0。元raw/旧checker、metadata-only回収を保持。再実行なし |
| PG22012 | Main-only六module正常build exit0、1036 input/1845 physical | 全POM保持/NullAway設定不変、変更WebRuntimeStop一class・他1844同byte |
| PG22014 | 六module SpotBugs exit0、bug/error/missing各0 | 同normal Jar不変、Product PTではない |
| PG22018 | 全6件exit0/F/E/S0、四counter100 | Main是正後の最初の成功。後の試験source整理後の結果と別run、unique二重加算なし |
| PG22016 | PMD raw exit4/2件、Checkstyle0 | Main既catch1と試験literal重複1。namespace回収不備は元XML保持でmetadata-only是正、空findingsを静的合格にしない |
| PG22022 | PMD raw exit4/1件、Checkstyle0 | 試験重複修正済。Main catchは元20154の同class/method/rule/column/message/roleと一致し、fatal保持→固定失敗・後続非進行の契約で個別非該当。抑制設定無し |
| PG22024 | 全6件exit0/F/E/S0 | 最終Test source全体の必要再資格、新規1/既5。line16/16、method3/3、class1/1、branch4/4、全missed0 |
| PG22026 | 独立post exit0 | 元XML/source/run/normal全入力/CRC/session/全physical2・六静的0・原赤と原rawを照合 |
| PG22028 | Main/Test二source format exit0 | google-java-format1.36.1、設定変更なし |

最終unit manifest SHA-256: `4c00f5957b5549994a2a270332c4fd85e48e51d8d95d37467037f1c9ac6ef3e3`。
独立post manifest SHA-256: `dcb4a48da9389653ef8b8e4232d4961ce259e29c86604c04223765b8c6011ad2`。
正常build manifest SHA-256: `e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640`。
静的manifest SHA-256: `b2e2d9695ba4734698d2378d51be117cbdfd9368fbbabc6cd8b42ead5d387360`。

各runのbegin/exit/raw stdout/stderr/XML/coverage/manifestに実行日時・OS/JDK・command・実input・期待/actualが対応する。最終sessionはPG22024-web-stop-clock-six-unit-v2-WEBSTOP、WebRuntimeStop CRC5b3d3b93ffa681c7・全12probe hit。abstract Stepは全physicalに含むが実行code/counter無し、手動除外0/旧exec合算0。依存SessionStoreExceptionやTest自身の部分coverageを対象source全counterへ加えない。四held型の初期化0、外部VM/DB/JMS/Web/Root操作0。

当sourceは固定seedですでにFOUR100だったWebRuntimeStopの変更後再資格。whole-source実績88は増やさず、新Testは006の一件だけでunique387→388（Java283→284、HTML97/CSS7不変）。原282/partial80の消化、新leaf、正式1964PT/53scope、工数率nullは不変。BUG2409/YKT2154と試験品質BUG2414/YKT2159を有限scopeで閉じ、実runtime/CHR/native/全451/QA051 finalやBUG2407動的六件のHOLDを解除しない。
