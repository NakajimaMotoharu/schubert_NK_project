# Revocation冗長条件 PG・PT・静的結果

2026-10-20、1189/BUG1481/YKT1242。source **7be1b02c471e6a5aa597d314b87e07050cab4b9e**、PG5742元53663 actual0/phase0,0、23:04:15.547759Z→23:06:21.518711Z、archive **1536f49cbffa5c19cb71419f644df535c6135bee258a8e81bd68572b1e269513**。

通常実行**15件/7suite・FES-flaky-rerun0/全XML一意/source固定**。RERUN003七件は当sourceの独立JCA/長さprefix/golden/AAD/未知版/鍵なし/片側null/provider/random故障/100並行/borrower-close/再起動previous読戻しを確認した。必要reactor八件は内訳を分け、新試験ID加算0。六module当1664Main compile/型null・SpotBugs各0。

PG5744元43256 actual0：全849Mainの差は一Source一条件だけ、全1664物理Mainの差は当RevocationPayloadCodec一classだけ（他1663完全同byte）。全field/公開・private method descriptorは不変。独立実対象四counter **LINE97/97・METHOD10/10・CLASS1/1・BRANCH40/40**、除外追加0。PMD7.28.0 exit4/raw**1598**/処理0、Checkstyle14.3.0 exit0/指摘0、当UnusedNullCheckInEquals消失。新schema2全1598診断一意、原rawの警告抑制0、全体F03未受入。

公開実PT `evidence/provisional/PG5746-revocation15/manifest.json` SHA256 **ccfa04e9939db3cf1ef4ea2c1fe673e24726408be08989095ecb5e2393f39dd3**。全TestID/XML/hash/環境/command/開始終了/exit/coverage hash・target counterを保存、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、dev-foundation。別静的 `evidence/provisional/PG5744-revocation-static-v1/manifest.json` **c85484fba88b1ae8ae84428de88c25eb283597872ead51a5bfc2b09005ab3ffb** とfindings.json。元snapshot/log/全safe metadataはwork/pgpt-runs/PG379各new-only run。

YKT1242：Production全体の`previousVersion != null && version.equals(previousVersion)`は当一箇所。他SessionPayloadCodec.selectKey/WebLogPayloadCodec.selectKey/ResponseSnapshotCodec.selectKeyはnullable previousVersionがequals receiverなのでnullguardが必要であり、削除しない。constructor対invariant/current先行/未知版拒否を保持し、当七PTのnull・旧版なし・別鍵・旧版ありを確認した。単純なnullguard一括除去ではない。BUG1481/YKT1242当scopeCLOSED/完了2026-10-20。

provider不在negativeの変更は自己所有test JVM内だけでfinally復元、実OS/provider設定・VM・鍵・DB・サービス・権限・回収操作0。拒否PT代替0、新全体/native/CHR/451正式/QA051finalは別保留。正式1964/53・工数null/原/v3/v4未較正597.25不変。続いて独立PG/PTへ進む。
