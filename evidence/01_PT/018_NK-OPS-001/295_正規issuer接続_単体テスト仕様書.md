# 正規issuer接続 単体テスト仕様書

NK-OPS-001/NK-BAT-001、RD SYS004/OPS009/MQ/DAT、UI251/253、SS311/321/341/342/343§6.17・SSC108/126。PG394実Broker/Expiry後、同ownerの正規発行→Root/APIWebへ進む一接続変更群。部分parser/PT成功をissuer完成にしない。

| Test ID | 対象/目的・fixture入力/操作 | 独立期待値と根拠 |
|---|---|---|
| ISSCFG001 | 既存ApiNonSecretConfigTest/WebNonSecretConfigTestをsharedへ移管、default/common/service・正常/境界/未知/null/parallel | 既存の手書きsorted scalar vector/独立SHA256を無変更。6Queue値はSS321固定literalと1対1一致、hash/例外/role別拒否は従来と同じ |
| ISSCFG002 | Root actual保持common/role YAML→shared parser・current signed inventoryとの関連、漂移/unknown/private close | raw YAML hashだけでeffective hashを代用しない。同actualのcanonical SHA一致、secret入力/環境fallback/業務module依存を追加しない |
| ISSROOT001 | 同M/A/原本/INVALID下の6実root identity/policy→NKROOTS1、前後再確認 | SS343固定6行/全10field/5共通key、独立手書きASCIIgolden。owner/mode/ACL/FS/重複/並行交換拒否 |
| ISSSTEP001 | 実10step最新全列・SKIP元監査参照・真正producer receipt→NKPRESTART1 | SS343§6.17の順序/完全handle/元reference、未試行placeholder・旧receipt・不確定/signal/timeoutはencode/issue不可 |
| ISSSTEP002 | MorningExpirySessionTestの実PG当回SUCCESS→通常再開SKIP→親ExpiryObservation、同owner readback | 手書きauditはcutoff-7日/before3/after1/target2/success2/bytes200。今回SUCCESS handle/終了を保持し、再開の別row/attempt2はSKIPPED全0/ended=started/ALREADY_SUCCESSFUL、元audit/handleを別Priorに保持、receiptは当回EXPIRY0。異なるowner/row/receipt/元値変更は拒否し書換0 |
| ISSSTEP003 | CleanupTerminalRepositoryTestの実PG最新7slot＋別元SUCCESS全列、親receipt保持 | 手書き7step順・元row1000～1006/count1・新row2000～2006/attempt2/all0/ended=started。元不足/別run/同attempt/未来end/diagnostic不整合は拒否、元は更新0、success時とBACKUP_UNAVAILABLEに不要参照を付けない |
| ISSGATE001 | 実POSTGRES/RELEASE_BOM/STOP_SET/BROKER_OPS/BACKUP_RETENTION | codec具体key順をSSへ先行確定、実固定query/inventory/保持readbackを独立照合、任意digest受理なし |
| ISSGATE002 | A後のMaintenanceUnitTermination.quiescentObservation→MorningUnitTerminals.capture→Control/Stage/Main | 既存手書き12field/5～6固定kernel identity、固定8順/別Unit/欠落/busy/null/前後漂移拒否。真正取得SnapshotとMorning actorを保持、immutableで旧stop観測流用0。clean journal/全gateは別未実行 |
| ISSPUBLISH001 | 同owner全根拠再照合→StartupPermitFiles.issue→current/permit原byte独立再読→再照合 | 実INVALID同generationだけISSUED、失敗part/旧permit保存・秘密0。API/Web readyをprestartへ混ぜない |
| ISSNATIVE001 | 外部Morningから真正producer10step→正規issuer→Root/APIWeb経路 | 同Source/classbyte実exec、実current/permit・boot/run/activation/roots/steps/実live一致。原本doneは業務ready実完了後だけ |

command・JDK/OS/tool/branch/commit/実時刻/FES/coverage/BUG/SSC/path/hashは296と新manifestへ採取する。source/expectedで同production encoderを共有しない。line/branch/method/class100%・全native/未解決重大0・秘密/trace・正式gate未達は未完了として管理する。
