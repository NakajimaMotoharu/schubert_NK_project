# 正規issuer接続 単体テスト仕様書

ISSROOT004（PG397・BUG377/378）：固定NSS literal/host6rootの全metadataを独立getent/lstat/listxattr/findmntで確認し同原本INVALID5keyと6SS行からhashを計算。Production methodをoracle生成に使わない。actual native capture/recheckは別に同source parent.exec＋全actualclass一致0とMain帰還181/capture24line/recheck4line完了で確認。Productionがnative roots canonical hashを未出力の間はhash一致/許可成功を宣言しない。未知name/欠落/交換/ACL/RO等は既存ISSROOT001～003と併用、独立fixture誤名/labelの初回拒否は合格へ混入しない。spec/実actualmetadata/Source/command/coverage/hashはnative manifestで追跡する。

ISSGATE003 / MMAIN010（SSC128/BUG376/YKT296）：実Expiry正常0→独立再読transaction内のbroker.recheckが別DB transactionへ再帰しない。同Root/親PID/期限/原本/INVALID、生Brokerは毎境界で検査、DB原本/HELDはtransaction外前後と所有Session内で検査する。6bind境界の既知停止は固定IOException、Morning既知停止は30、未知Runtime/NPE/Errorは同一throwableを保持。独立oracleはPG396旧53行保持＋新10SKIP全14列、真正fresh Broker/Expiry0、permit0/INVALID、次修正nativeは同原本から6root収集/再確認の実return-line到達。親exit30だけを到達証明にしない。HostはMain typed停止/未知同一性、MutationGuard実PG timeout/rollback、Session全negativeを再試験。Native同source4exec＋actualclassesでclass mismatch0、root返値のline到達を別採取する。未実行/失敗は合格へ加算しない。

NK-OPS-001/NK-BAT-001、RD SYS004/OPS009/MQ/DAT、UI251/253、SS311/321/341/342/343§6.17・SSC108/126。PG394実Broker/Expiry後、同ownerの正規発行→Root/APIWebへ進む一接続変更群。部分parser/PT成功をissuer完成にしない。

| Test ID | 対象/目的・fixture入力/操作 | 独立期待値と根拠 |
|---|---|---|
| ISSCFG001 | 既存ApiNonSecretConfigTest/WebNonSecretConfigTestをsharedへ移管、default/common/service・正常/境界/未知/null/parallel | 既存の手書きsorted scalar vector/独立SHA256を無変更。6Queue値はSS321固定literalと1対1一致、hash/例外/role別拒否は従来と同じ |
| ISSCFG002 | Root actual保持common/role YAML→shared parser・current signed inventoryとの関連、漂移/unknown/private close | raw YAML hashだけでeffective hashを代用しない。同actualのcanonical SHA一致、secret入力/環境fallback/業務module依存を追加しない |
| ISSROOT001 | 同M/A/原本/INVALID下の6実root identity/policy→NKROOTS1、前後再確認 | SS343固定6行/全10field/5共通key、独立手書きASCIIgolden。owner/mode/ACL/FS/重複/並行交換拒否 |
| ISSROOT002 | Root collectorのhost/private保持前後・同名再保持・固定profile/6path・close故障 | host localRW、privateのみROを許容。同全metadata/FS、dev+ino重複無し、uid/gid/mode一致。size/time/nlinkの保守変化は次最終identity照合で許容するが各IO内の漂移は拒否。null/未知例外は正常化せず、秘密・許可・runtime repair能力0 |
| ISSROOT003 | 隔離VMの固定2account/3root初期配置、既存3root/原本/INVALID保全 | 実M/A/全8停止/署名current完全BOMに基づくnew-only。systemd-sysusers固定名、NSS private before-image、実ACL/hostRW/metadata確認、既存root/devino/current/原本不変。空ASSETはmaster移行未認定。部分配置は未完了保全し自動repair不可 |
| ISSSTEP001 | 実10step最新全列・SKIP元監査参照・真正producer receipt→NKPRESTART1 | SS343§6.17の順序/完全handle/元reference、未試行placeholder・旧receipt・不確定/signal/timeoutはencode/issue不可 |
| ISSSTEP002 | MorningExpirySessionTestの実PG当回SUCCESS→通常再開SKIP→親ExpiryObservation、同owner readback | 手書きauditはcutoff-7日/before3/after1/target2/success2/bytes200。今回SUCCESS handle/終了を保持し、再開の別row/attempt2はSKIPPED全0/ended=started/ALREADY_SUCCESSFUL、元audit/handleを別Priorに保持、receiptは当回EXPIRY0。異なるowner/row/receipt/元値変更は拒否し書換0 |
| ISSSTEP003 | CleanupTerminalRepositoryTestの実PG最新7slot＋別元SUCCESS全列、親receipt保持 | 手書き7step順・元row1000～1006/count1・新row2000～2006/attempt2/all0/ended=started。元不足/別run/同attempt/未来end/diagnostic不整合は拒否、元は更新0、success時とBACKUP_UNAVAILABLEに不要参照を付けない |
| ISSGATE001 | 実POSTGRES/RELEASE_BOM/STOP_SET/BROKER_OPS/BACKUP_RETENTION | codec具体key順をSSへ先行確定、実固定query/inventory/保持readbackを独立照合、任意digest受理なし |
| ISSBROKERSTOP001 | BUG375/SSC127、既知通常143＋真正全cgroup空＋同Invocation停止journal→fresh Broker、旧fullsnapshot/summary保持 | 手書きdaemon inactive/failed143/別code/signal/foreign target/PID/時刻vector、手書きvendor停止JSONと独立SHA256。journal無し143はstart0・reset0、startup3eventで停止を代用しない。native旧failed143の正規resume→真正fresh/Ops→Expiry/6rootを同未完了runで確認する |
| ISSGATE002 | A後のMaintenanceUnitTermination.quiescentObservation→MorningUnitTerminals.capture→Control/Stage/Main | 既存手書き12field/5～6固定kernel identity、固定8順/別Unit/欠落/busy/null/前後漂移拒否。真正取得SnapshotとMorning actorを保持、immutableで旧stop観測流用0。clean journal/全gateは別未実行 |
| ISSPUBLISH001 | 同owner全根拠再照合→StartupPermitFiles.issue→current/permit原byte独立再読→再照合 | 実INVALID同generationだけISSUED、失敗part/旧permit保存・秘密0。API/Web readyをprestartへ混ぜない |
| ISSNATIVE001 | 外部Morningから真正producer10step→正規issuer→Root/APIWeb経路 | 同Source/classbyte実exec、実current/permit・boot/run/activation/roots/steps/実live一致。原本doneは業務ready実完了後だけ |

command・JDK/OS/tool/branch/commit/実時刻/FES/coverage/BUG/SSC/path/hashは296と新manifestへ採取する。source/expectedで同production encoderを共有しない。line/branch/method/class100%・全native/未解決重大0・秘密/trace・正式gate未達は未完了として管理する。
