# PG483 readiness短絡・配備物negative仕様

NK-OPS-001、ApiProcessMain.applicationReadiness/runtimeReadiness/main/startNative、ReleasePayloadVerification/StartupReleaseManifest.verifyCandidate。RD SYS002004/OPS009/TST004、UI212243251253、SS312342343352、SSC158161193、PG-D389。fixtureのauthorityを実VM admissionへ読み替えない。

|Test ID|入力・操作|独立期待値・算出根拠|
|---|---|---|
|PT-OPS-API-HEALTH001|management8通り/consumer4通りの手書きboolean table|managementはgroups=true/stopping=false/outbox=trueの一組のみtrue、consumerは両trueのみtrue。左から評価、拒否後のsupplier呼出し0|
|PT-OPS-API-HEALTH002|同supplierのgroups公開前後/outbox故障/stop・復旧遷移|呼出し時の値を毎回読み、factory時の成功cache0。admission/promote/資源所有は試験外|
|PT-OPS-API-HEALTH003|各supplierの同一IOException由来unchecked/fatal、null各依存|元Throwable同一伝播/後続呼出し0、nullはfactoryで拒否、正常化0|
|PT-OPS-FULLBOM011|独立literal ZIPの絶対path/backslash/..//nested JAR/空archive、manifest Class-Path空/未登録/実shared正常|悪性形は固定redacted release manifest unavailable/原因秘密非公開、全FD解放。正常形は手書きpayload全hash・共有class一致|
|PT-OPS-FULLBOM012|既Ioを使ったVERSION readのsize/position/zero/負EOF/oversized/offset故障、null/open IOException|受入拒否、元資源全close、再利用成功補完0。fixtureは実host所有FD/read channelを包むだけ|
|PT-OPS-FULLBOM013|列挙にnull/foreign parent/duplicate、全Root/treeは既literal fixture|仕様上単一宣言集合以外拒否、streamと全FD正常close・元file改変0|

fixture/publiccomponentの正常・境界・異常・null/欠落/未知・例外を同群で実行。再送はこのread-only検証には業務発行なし、並行は既FULLBOM007とAPI lifetime/regressionで確認、native別未受入。expectedは上記literal table/独立ZIP bytes/JDK channel契約/手書きrelease inventory、Productionのready/hash/codecで作らない。run command/environment/source/終了/独立assertion/static/coverage/BUG/path/hashは391結果へ、rawlog/exec/XML私有、秘密Git0。除外追加0、全coverage100未達を成功に加算0。
