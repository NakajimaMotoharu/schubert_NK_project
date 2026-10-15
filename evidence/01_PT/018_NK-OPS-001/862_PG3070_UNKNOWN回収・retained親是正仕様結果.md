# 862 BUG1265のUNKNOWN正規回収と既存parent専用是正

NK-OPS-001/WBS-N14、PT-OPS-3070-001/3072-001/3074-001/3076-001/3078-001/3080-001/3082-001/3084-001/3086-001。SS343/353/SSC230259260274276277・451。0800の同群0.5/1.5/4ppを保持、失敗/回収を別実績として隠さず記録、全体正式/工数への加点なし。

3062 ABI六phase0/3064stage0でもreturned native_refs102のroot-only cold条件が残り、既存parentを拒否した。3064/exec55480は00:43:02.358211～00:50:39.731801Z、actual143/REFERENCE_SCOPE UNKNOWN/sourceQualifiedfalse/preparefalse/reloadfalse。Root/ADMIN/業務SQL開始0、SAVにはrefs logだけ（SHAe3f25b73a575626f9acbedc72d5ab9c18ba51e74325774f0377d7f75527aeb2d）。BUG1265/YKT1031は是正前に起票、元slot/失敗を成功化しない。

## 当時の実所有と回収

3070 actual0、host114601/t2519587/argvb5645b75・FD4/private gate66306:9337730をsole ownerとしてsingle queued読取。guest Java208849/t2423591/argv3ea1a485・親208847、101FD・子208880/4FD、runtime root＋元parent2entry・設定変更なしを捕捉。3072 actual0でchildt2423775/argv5424b435、samepeer backend208878を資格。JavaのM linked88/91/92・flock92、A linked/flock101/128・同OFD、/run祖先FD31/90を独立proc/kcmpと全metadataで照合する。

3074/exec51493 actual0・00:48:27.333242～35.801300Z、全24/署名187/原Backup/native16/Runtime元parent不変・DB同peer/advisory・二flock・101/4FD二読、proof f7eb7b8d72c3836f30e4d588b3718433b28e6ddcbcde0c434dddf6872bff96a7。純二試験で全scopeとonly-current-child→parent二回TERM/非再演/kill9やbackend terminate/reload無しを確認。

31648ad6c固定3076/exec58119 actual0・00:49:51.203187～00:50:39.923815Z。同接続でfresh全proof735b9243を再作成後だけpidfdでchild→Javaへ各一回TERM、両actor/backend/advisory/flock/bus消滅、元host gate自然解放→同inode queued承継0。強制unlock/daemon-reload/Root再実行0。旧3064 actual143は正常帰還と認定しない。

3078/exec18911別post actual0・00:50:55.295806～00:51:04.182608Z、payload1ce8e0c2。全24原値二読/187/Backup/native16安定、全十Unit/kernel/actor-client-advisory-flock0・原runtime退役後の全値不変を実証。元after92c953ea不変更、key/token/DBraw非公開。PG379/3070/3072/3074/3076/3078各私有manifestとguest保存域を参照。

## new-only是正と独立試験

3080/3082/3084/3086は別new-only。native_refs初期型をroot＋既存empty parentだけへ限定し、全metadata/ACL/shapeを照合して、元parent metadataを正常held-parent writerへ渡す。cold writer（rootからmkdir）を既実証済み通常writerへ戻し、parentのremove/rename/recreateは0。coarseCLOCK5予約/原base/pid1/八foreign deny等を維持。runtime_treeは全root値不変・parent identity0～5不変・有限mtime/ctime・独立file inode/Root0644/link1/byte長/SHAの強い型で照合する。

純三試験actual0: 修正前cold guardに既存parent反例を与えて拒否を再現、実Linux retained FDで既存parent inode不変のEXCL/byte/mode/force/二回目拒否・元byte保持、完成contractの正常/欠落/余分/unknown/hash拒否・全returned20source/dispatch/post namespaceを確認。3066の21metadata fault＋二shape反例も継承する。Production/Main/Current baseline/新3691のTest固定sourceは不変更。3082実六ABI→3084stage/一回prepare→3086別全postはこれからであり、BUG/YKTはその実証まで未完。

新RootはBrowser全case/既存有効専用credentialのfresh検証/明示HTTP-DOM-SQL差分oracleが揃うまで起動しない。既pg468 password-reset/初期ADMIN作成は再実行禁止、保全した有効credentialを使い検証するだけ。QA051finalは維持し、通常回収/commitだけで停止しない。
