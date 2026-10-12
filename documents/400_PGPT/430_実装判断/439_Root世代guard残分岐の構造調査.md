# Root世代guard残分岐の構造調査（2026-10-13、未完判断）

対象Main2741／RootStartupContext、WBS-P018-03.02、SS343/SSC164。1741 literal4は異boot-init-service-pid-group、消失二読raceで9branchを追加検証。1743 literal8は親再照合後のUID/procfs/init executable/boot/PID1 drift、pid1/zero invocation/tick race、期限誤service、DEL127で更に10branchを検証。Main変更0、実owner付与0。現全Main残870/169/9/686、正式認定とは別。

残る構造的論点は次の二つ。これを到達不能扱い・除外・反射経由で合格化しない。

1. `serviceGenerationExited`は二読の後`require(!first || second)`で消失→再存在を拒否し、続く`return first && second`に第二値falseの分岐を再度持つ。後者のfirst=true/second=falseは直前guardで例外になるため、承認済みの正常/拒否入力から後続returnの当組合せへ到達できない。四literal真理値：false/false→false、false/true→false、true/false→拒否、true/true→true。`return first`への等価簡約は検討候補だが、現Sourceを変更/認定済みとしない。
2. private `NativeIo.serviceRootUid(pid)`はpid>=2/MAXを再検査するが、公開捕捉経路のPID検証が前置される。実/kernel IOを保持した内部testability又は型付き入力境界の設計を検討する。private反射や実別PIDを操作してcounterを作らない。

次の必要Production変更群で内部判断/関連SS分類を行い、完全真理値の独立testとfixedsource全回帰・新署名runtime/nativeを同sourceで閉じる。現在は修正案/残条件であり、coverage免除・期待値変更・QA承認要求ではない。新sourceへ旧2741 nativeを流用する承認もない。独立した他host/native残件は継続する。
