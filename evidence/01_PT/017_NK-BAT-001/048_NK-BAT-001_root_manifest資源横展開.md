# NK-BAT-001 root manifest・資源解放横展開

PG169/170、SSC062/063、BUG195～197/YKT154～156。2026-09-13。正式13前の実装・探索記録。工程/横展開全体の完了を意味しない。

## 1. 修正前再現と探索履歴

| 実行 | JST終了・秒・exit | 判定 |
|---|---|---|
| /tmp/pgpt-bug195-red.log | 先行format check拒否 | 行動試験未実行。障害再現には数えない |
| /tmp/pgpt-bug195-red2.log | 09:24:03・8.046・1 | Reader/Artifactの同一unknown body/closeで2件FAIL。期待IllegalState同一、実際TWR self-suppression IllegalArgumentException |
| /tmp/pgpt-bug195-probe-red.log | 09:37:47・14.506・1 | Probe UNIT015でも同じ反例FAIL。Storage ResourceScope8件PASS |
| /tmp/pgpt-bug195-probe-green.log | 09:38:48・11.991・1 | 新PT fixtureの割込flag漏れBUG196。Productionの割込保持を弱めず試験を分離 |
| /tmp/pgpt-pg169-170-explore2.log | 09:41:34・3.668・1 | 新FLOCK fixtureのOpenCall引数数BUG197、testCompile段階。未実行 |
| /tmp/pgpt-pg169-170-explore3.log | 09:42:56・21.666・0 | Storage32件＋Batch40件PASS、fail/error/skipped0、両module static未解決0 |
| collector負canary | 019=40、017=1 | 全41件PASS。欠落/重複/異class/method、不合格・flaky/skip、trace全byte改変を拒否 |

上表logは公開合成値だけの探索記録を要約したもの。正式証跡はsource commitを凍結した全reactor後にmanifestへ登録する。探索72件は全reactor件数へ重複加算しない。

## 2. 修正済み直接対象と独立確認

| 対象 | 実施・再発防止test | 探索結果 |
|---|---|---|
| Storage.ResourceScope | RSCOPE001～008。known全IO reason、unknown3型、同一/別cleanup、nullable所有契約、nested全close、64並行 | 8PASS、1class/1method/19line/8branch、全missed0 |
| OwnedTransferDirectory.open/openDate/withEntry・EntryHandle | 3scope×unknown3型/knownIO＋unknown cleanup=12反例。実FD live集合とclose回数、借用root保持、初期化/entry失敗をMED019で確認 | 既存16PASS。ResourceScopeへ集約後の二重IO正規化catchを撤去 |
| LinuxFileLock.OwnedDescriptor | FLOCK005でknown有無×unknown3型、native open flags0x80000/mode0・flock6・descriptor17、open→flock→body→close順と一度だけ解放 | 既存8PASS。実flock/fcntl/外部所有回帰も維持 |
| BackupManifestReader | BAT226～241。38 IO出現/63 clock、964byte golden、buffer消去・完全handle・root属性・保持inode/rebind | 16PASS、2class/18method/144line/102branch、全missed0 |
| BackupArtifactVerifier | BAT194～209。123 IO/207 clockの既存oracle不変更。child/rebound/channel/namesを明示scope、重複SafeClose classを廃止 | 16PASS、3class/25method/204line/114branch、全missed0 |
| InspectorUnitProbe | UNIT015: cleanup3×unknown3同一throwable、既存3×3既知close、既知IO/timeout/interrupted×unknown3の9複合。全取得stdio一回、出力消去、未取得資源0回。Interrupted primary＋unknown cleanup時もflag保持 | 既存8PASS、4class/21method/119line/30branch、全missed0 |

Reader/Artifact/Probeのprimaryを渡してexpectedを計算せず、例外same identity・固定secondary型/reason・positive注入回数を独立assertする。正常時のI/O順・境界・電文・DB・command・利用者結果を変更していない。

## 3. YKT154残対象（未完了）

検索条件: Productionのtry(resource)/implements AutoCloseable、SafeClose/SafeStream/EntryHandle/OwnedDescriptor、未知例外identity/非正常化/固定diagnosticのSS規約。Batch/Storageの所有構文59箇所を確認対象とし、API所有keyも確認する。検索ヒット数は完了数ではない。

| 対象 | 現在の根拠・残確認 |
|---|---|
| SystemctlStateSource stdio/process | TWR＋外側known固定化/finally TERMが残る。同一unknownとIO＋fatal、TERM複合の反例・契約別修正未実施。非該当にはしていない |
| ConfigurationGroupResolver stdio/process/reader executor | TWR/TERM/非同期readResultの既存固定diagnostic契約あり。Future一次失敗とcleanupの同一性/優先順位を分類してから反例・修正が必要 |
| DurableRecordFiles readFile/write/force | channel/writer TWRが残る。全3箇所をIO portで直接反例・buffer/part保持と合わせ再確認する必要あり |
| InspectorEnvironmentReader channel | TWR＋外側IO固定化が残る。同一unknown/IO＋unknown closeの反例と既存環境byte消去・借用root回帰が必要 |
| InspectorEnvironmentFiles/MaintenanceRunFiles/MaintenanceFileLock・namespace directory stream | root/child複合scopeを未解放資源/後続closeの優先順位まで確認する必要あり。基礎Entry修正だけで全caller完了とはしない |
| API InspectorProcess.OwnedKeys/AuthContextCodec/ResponseSnapshotCodec等 | OwnedKeysはoperation-local配列消去とfinal credential close。外部I/O close portのないin-memory資源候補。実close実装・constructor失敗・並行禁止の全根拠/既存回帰を揃えるまで最終分類を保留 |
| JDK Arena | 外部close fault portなし、同thread所有/descriptor lifetimeの既存Native PTを維持。今回のsame-provider throwable注入の直接対象外。全reactorで再確認予定 |
| 他JDBC/SessionLease/codec所有者 | JDBC primary保持はBUG193/YKT153で別原因処理済み。一般化して例外意味を上書きしない。契約と既存負例を追記してからYKT154最終判定 |

したがってBUG195は直接対象修正済み・全体対応中、YKT154未完了。未処理候補を「検索済み」のみで閉じない。次の小単位で上表を反例→必要なSSC→修正→全再試験へ進める。

## 4. PT自身の横展開

BUG196/YKT155: UNIT015追加compound loopにknown種別ごとのflag期待assert＋finally Thread.interruptedを追加。UNIT014全割込loopは既存finallyあり、ResourceScopeは割込注入なし。09:42:56のProbe8件と全compound通過、正式全reactor待ち。

BUG197/YKT156: OpenCall4/LockCall3/CloseCall2を実interface・既存fakeと照合。新OpenCallのみ修正しmode0/flags/descriptorもassert。DirectoryCallsは実override。09:42:56のStorage32件compile/PT通過、正式全reactor待ち。

## 5. 正式認定・限界

正式13は未実行。run/source/commit/環境/command/exit/全4coverageは017/018各evidence/manifest.jsonと047/028へ登録する。追加24PTは正式認定までは進捗加算0。rootUIDの入場はsynthetic、実dump/tar/age/manifest生成/fsync/7世代/親OS継続保持・子終端・実NKCHR/IT/STは未完了。
