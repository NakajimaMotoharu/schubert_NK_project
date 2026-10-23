# 1573 Micrometer HTTP記録 単体テスト仕様書

## 試験用SDK内部表現の補完（2026-10-23、BUG1651/YKT1404）

下記1785はprimary業務Meter（Counter1750＋Timer35）の数を示す。実SimpleMeterRegistry1.17.1はnewTimer内でHistogramGauges.registerWithCommonFormatを呼び、九SLO×35route=315の内部Gaugeも保持するため、registry全物理数は2100。固定Jar primary bytecodeで同呼出/`.histogram`/`le`/base time unit変換を確認した。HTTPREC002/003/004ではprimary数を保ち、aux Gauge315・名前 `nk_http_request_duration_seconds.histogram`・service/route/le三tag・serviceWEB/独立35route各九le（秒 .05/.1/.25/.5/1/1.5/2/2.5/5）を別assertする。009のCounter conflict時partialは既Gauge1＋Timer1＋aux9=11、Timer conflict時は既Gauge1だけ。単に観測数へ期待を変更せず、SS九境界と固定providerの内部表現から導く。

これはcanonical producer metric追加ではなく試験用Simple providerの内部SLO表現。実Prometheusのexposition/命名変換/quantileは引き続き未受入で、内部 `.histogram` 名を新たな外部catalogへ承認しない。元v2の15件/F4は保全し、新sourceで全15を実行してから判定する。Main/SDK版/九SLO・1750/35の業務期待値は不変更。

2026-10-23、PG-D527/NK-OPS-001/P018-09/C07共有費0。着手1/3/7pp・上限10pp、共有11/残89/reset1793306748・元開始0。RD171 MON005～013/UI252/SS351§6・8・10。1570の閉型を実Micrometer core1.17.1へ接続するHttpMetricRecorder。既管理版coreをWeb compile依存へ正規追加し、元正規runtime Hdr2.2.2を含め依存除外0。契約・provider単体は実in-memory SimpleMeterRegistry/MockClockで検証し、実HTTP/DB/Root/VM/公開は行わない。

Registryはcallerが所有し、custom nk_ namespaceにラベルを追加/置換/拒否するfilter/commonTagを設定せず、寿命中その構成を変更しない。Recorderは借用だけでcloseせず、ctor失敗時のpartial registrationもcallerのregistry破棄で回収する。DEBUGは閉1750 request Counter/35 Timerを先行登録し、未知入力が新Meterを作らない。STANDARDはcustom登録0でminimum health等を変更しない。null/不正status/負elapsedは記録前に拒否し、unknown route/methodは1570どおり固定値へ。Callbackは一completionにつき一回、SDK Runtime/Errorは同一objectのままownerへ伝播、log/HTTPへformatしない。counter→timer途中のprovider故障は部分計測が残り得るため同completionの自動再実行を禁止する。HTTP owner側の固定terminal通知/既fatal graph分類・応答保持は未接続の後続条件。

二Meter IDはSS351 canonical名、labelsはservice/route/method/status_classとservice/routeだけ。Timer SLOは正規9Duration、実coreで登録/記録する。Prometheus側の命名変換、bucket exposition/quantile query、p95実測、Actuator/実exporter登録はこのcore単体で合格にしない。SDK timerの集計表現・長期負荷も製品/IT-ST確認を別に保ち、少量のPTから無制限の精度保証を導かない。

|Test ID/method|独立期待値|
|---|---|
|PT-OPS-HTTPREC001 / httpRec001|STANDARDはcustom Meter0/record後も0、borrowed registry未close |
|002 / httpRec002|DEBUG登録1785＝1750 Counter＋35 Timer、単一/login GET200・1秒でcounter1/timer count1/total1秒、正規9 SLO boundary |
|003 / httpRec003|独立35route×10method×5statusを各1秒、request各1/Timer各50・total50秒、ID/tag集合一致 |
|004 / httpRec004|1万異なる合成入力もunknown/OTHER counter10000/timer10000、meter1785のまま・禁止値なし |
|005 / httpRec005|null registry/mode/route/method、status99/600、elapsed-1は拒否・記録不変。100/599、0/Long.MAX_VALUE単一観測境界（別Timer） |
|006 / httpRec006|実registryに挿入した合成Counter/Timer Runtime・Errorを同一objectで伝播、再試行0、借用registry未close、部分counter結果を成功へ補正しない |
|007 / httpRec007|64並行record、同counter64/timer64/total64秒、自己所有executor終端 |
|008 / httpRec008|既外部fixture meterとregistry所有を変更しない。ctorのstrict mode・失敗はownerがclose、Recorderに寿命奪取APIなし |
|009 / httpRec009|既同ID wrong-type meterはSDKが拒否、未知name/tagへ逃げず、原source/contextを捏造0 |

新9＋既HTTPMETRIC6の必要同package回帰=15PT/2suiteを固定sourceから実行、実7class＋metadata1のCRC/単一session/四100、親Enforcer/lint/Werror/NullAway/SpotBugs/Checkstyle/PMD個別適用性を確認。ExpectedはSS name/label/bucket、独立35行golden・1750/35/50/10000/64・固定秒から作りProductionを呼んで生成0。Framework/SKD vendor sourceは当Production srcではなく、coverageを除外して我々の未試験codeを隠さない。既Batch73/原4222/common44の確認再演や異source union0。全体451/native/CHR/正式/QA051final・HOLDは不変更。実結果/command/source/版/hashは1574以降へ。
