# NK-BAT-001 root manifest・資源解放横展開

PG169/170、SSC062/063、BUG195～197/YKT154～156。2026-09-13。正式PT-WEB-20260913-13、source820554603bca7e5ddd358139f33dee27c9ae87c3/dev-foundation、2026-09-13 09:48:33～10:04:44 JST、Maven16分10秒/exit0。全1415件（Protocol80/Storage66/API660/Web241/Batch327/CHR41）PASS、failed/error/skipped0。6 Java module全line/method/class/branch100%、Production5 module static未解決0、固定path3method限定レビュー・coverage除外なし。15collector/38scopeと41負canary PASS。PG169/170新24件を認定するがBUG195/YKT154の広域残候補は未完了。実NK CHR/IT/ST/親全体の完了ではない。 以下の探索記録は正式13前の履歴として維持する。

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

探索log SHA-256（原logは/tmp、再現条件/期待/実際を上表へsanitizeして保存）:

| log | SHA-256 |
|---|---|
| pgpt-bug195-red2.log | 102bd63c78257b39025bfe9b4434ceb3dd054bffb9d0151ce9830ce6c79e81d7 |
| pgpt-bug195-probe-red.log | 807fc62e65f3d8d6ab9fa1043ed9a6995a08b2da9c938942bd86a6ebd227e325 |
| pgpt-bug195-probe-green.log | bd7f1bc5b4f638ab0a8b8b8d00f73aa833df827c3b1aafe81322579c68ca2dac |
| pgpt-pg169-170-explore2.log | b9ce0d9684d2d62e8c0755ea043f9fd15b26853087b8d4f0e7d62233a1579e51 |
| pgpt-pg169-170-explore3.log | be9ebbac9893e7cbbafbdd7ca189666067c45c059f0d8f333d8b8f08ed2cea29 |

探索command（09:42:56の単一実行）: JAVA_HOME=work/toolchain/jdk-25.0.4、Maven ./mvnw -o -Dmaven.repo.local=work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=OwnedTransferDirectoryTest,LinuxFileLockTest,ResourceScopeTest,BackupManifestReaderTest,BackupArtifactVerifierTest,InspectorUnitProbeTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check。ここでworkは /home/mini/codex/project1/work、cwdは同配下pgpt-foundation。JDK25.0.4/Maven3.9.12/Ubuntu26.04.1/amd64、その他は421。Sourceは後続820554603bca7e5ddd358139f33dee27c9ae87c3へ確定して正式13で再試験する。

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

BUG196/YKT155: UNIT015追加compound loopにknown種別ごとのflag期待assert＋finally Thread.interruptedを追加。UNIT014全割込loopは既存finallyあり、ResourceScopeは割込注入なし。09:42:56のProbe8件と全compound通過後、正式13の全1415件/4coverage/staticでも成功。全対象確認により完了。

BUG197/YKT156: OpenCall4/LockCall3/CloseCall2を実interface・既存fakeと照合。新OpenCallのみ修正しmode0/flags/descriptorもassert。DirectoryCallsは実override。09:42:56のStorage32件compile/PT通過後、正式13のStorage全66件と全1415件/4coverage/staticでも成功。全対象確認により完了。

## 5. 正式認定・限界

正式13は上記の通り成功。run/source/commit/環境/command/exit/全4coverageを017/018各evidence/manifest.jsonと047/028へ登録、追加24PT/2部品を認定。BUG196/YKT155とBUG197/YKT156は全対象の正式再試験成功で完了、BUG195/YKT154は直接対象を認定し残候補があるため対応中。rootUIDの入場はsynthetic、実dump/tar/age/manifest生成/fsync/7世代/親OS継続保持・子終端・実NKCHR/IT/STは未完了。
