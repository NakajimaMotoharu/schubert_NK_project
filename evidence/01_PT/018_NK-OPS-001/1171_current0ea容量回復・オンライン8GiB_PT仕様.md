# current0ea 容量回復・オンライン8GiB PT仕様

QA052の既承認容量確保/専用LANを継承、業務仕様・451・12GiB基準の緩和0。群1313 WBS-N11（P018-04.03参照費0）着手前.5/1.5/4pp、追加発見の環境回復としてRoot群1311/原v4未較正597.25と分ける。専有費/実N-T/工数null。

5632元86686 actual1はpayload119の12GiB下限拒否、free11940941824（約11.12GiB）、Root予約/start無し。raw読取不合格は元namespace/manifest/payload/stderrを保全、下限を下げて成功化しない。5642元64127の旧freeze成功も今後変更後へ転用しない。

5654-v1元27382はactiveを含むchain四なのに旧count三を要求し拒否（BUG1467/YKT1230）。修正前登録→新v2元73811はhostQMP元0・四層path/容量/三backing実FD readonlyまで成功したがsudo提示付きPTY全体をJSONparseし拒否（BUG1468/YKT1231）。原log **87a6bcef7d2a38fdcca801d293947a44c11a44bf81cbb0c9cedcc982b178f8e9** を固定し、hostqueryを再発行せず`recover-v2`で一意完全JSON/固定提示だけ認証。元42445 actual0、未実施guestgeometryだけ読取。hostfree118308519936、active77309411328、node#block113、QEMU10.2.1/同4599ticks101242・hostbootc796/guestboot79a326。hostproofdb06deae/guestprooffaf39b9f。backing三pathはpg2200 active48GiB/pg1435 active48GiB/pg1431guest40GiB。

5656 before/afterは現0ea/PG5598/BOM1aa187・新5630after de765f0dへ全11/24/原本Backup/native94/十Ref/actor-client-advisory-flock0/設定inodeを独立照合し、privateにpartitiongeometryだけ追加保存。beforeは72GiB/root148670431sector/free12未満、afterは80GiB/root+16777216sector/free12GiB以上。root開始2324480・UUID/type/GPTid・他三partition完全不変、元growのpartition-afterとの一致を要求。

5658は同QEMU/boot/socketpeer/node/inode/argv/ticks＋旧三backingのreadonlyFD/metadataを認証。guestでmaintenance/startup-admission lockと全十Ref/Unitkernel無活動を保持してREADY→host単一`block_resize(node-name=#block113,size=85899345920)`→元0だけguestへconfirmed→単一growpart/vda1→単一resize2fs。no shrink/force/reboot/delete/copy/Rootstart、fsync済一回予約。途中失敗/応答欠落で再growしない。oldbacking/full11データを変更しない。

純粋12件: 手書き72→80/+8GiBgeometry正常・rootstart/UUID/他partition/delta/GPTid/不足拒否、active＋三の不足/余剰/逆順/異容量/異path、明示sudo/一意frame正常と未知prefix/複数/null/bool/非0拒否、grow元bool/非0拒否、全emitted static0・正確一回QMP/growpart/resize2fs/正常refs返却後出力、禁止操作0。actualcapacity/ProductionPTへ加点0。

元5654は回収済みで再演0。5656before actual0後、工具/台帳/仕様commit/push clean・freshquota>10→所定PYTHONPATH `python3 -B tools/quality/pg5658_capacity_online_grow.py`一回→元0→`python3 -B tools/quality/pg5656_capacity_current_post.py after`独立post。後だけ5632 freshreader v2/5642 qualificationv2を作り、新Rootを通常契約で一回開始する。旧Root/ADMIN/Backup/署名/3905成功の確認再演0。
