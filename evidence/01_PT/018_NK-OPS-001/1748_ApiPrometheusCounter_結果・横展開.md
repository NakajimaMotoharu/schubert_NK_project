# 1748 API四Counter 実SDK名是正・結果・横展開

NK-OPS-001/WBS-P018-09/C07/RD171 MON005010013/UI252/SS321323351、1747/1718/PG-D588・589。group1974開始1/3/6pp/cap10は不変更。

## 結論

新APICNT8＋必要既32の **40件/5suiteは修正source6246c954d6d0ac7171bf009663bb2e6539d8be32で全成功、F/E/S/aborted0**。四Counter/801sample、全Inbox64×12・operation8・queue6×3・MQstage7の固定label/増分・初期0・STANDARD登録0・二owner/64worker/1000供給を実Prometheus1.17.1/client1.7.0上で確認した。実業務Inbox/再送/認証/送受信・VM/DB/Root操作ではない。

当実6classは **line138/138、method19/19、class6/6、branch54/54**、CRC不一致0・一session・旧counter合算0。新対象PMD/Checkstyle/SpotBugs/processing/missing各0、二enum生成4methodも当typed契約と非初期化metadataで確認。正常六compile/NullAway/formatは終了0/PT0・UNRUNを維持する。

## 根因・PG是正と独立oracle

BUG1691：元e196のMqMessageMetricRecorderが固定名nk_mq_messages_totalへ内部baseUnit=messagesを加え、実SDKで **nk_mq_messages_total_messages_total** を生成。PG8206は40中33成功7失敗/終了1であり、旧Simple成功や33件を全合格へ読み替えない。PG8207の同SDK固定own診断で、元Producerの実TYPEとunit無しcontrolの正名を保存した。調査中の仮説を実測と区別し、診断を製品PTのPASSに数えない。

PG-D589で内部baseUnit指定一箇所だけを削除、旧MQEVENT001の内部metadata期待値をnullへ訂正。上位RD/UI/SSはその内部指定を規定しておらず、**SS351の外部name/type/label/一event一increment、新APICNT oracleは不変更**。1718は元状態を説明して現仕様へ訂正し、元1719/source/失敗40を保全。新sourceの本番用Java実装をsrc内で修正し、旧normal Jar/成功を流用せず再build/必要試験した。

YKT1442：全Production baseUnit三箇所を確認。Counterは当MQ一箇所のみ修正、他二DbQueryDuration/MqProcessingDurationはSummaryの_seconds名・seconds指定であり、同SDKの純命名結果は末尾不変。これはCounter_total重複の共通原因には非該当、実histogram/Timer backendや全アプリ合格を意味しない。四Counter全names/801固定sampleは修正後の新40で再試験・APICNT001/005を再発防止とする。実操作権限は付与しない。

## 一次証跡

|ID|真正結果|manifest SHA256|
|---|---|---|
|PG8206-api-prometheus-counter-host-v1|元40中7失敗/終了1、製品旧e196|e7ba3dd1435e89c39c55932c33574a9a33dbe99fb43373733485c596385e58f7|
|PG8207-counter-name-diagnosis-v1|固定TYPE差分・二seconds純命名、製品PT0|60bdfffe88b15efb41882febc66023f8b2e3879924a6205ac6756b6d56052ac7|
|PG8212-counter-name-six-compile-v1|新source正常六build0、PT0/UNRUN|db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6|
|PG8214-counter-name-host-v1|新source40/5全成功、終了0|e7c14378ecebe856fc3f09d06a32ea407135bf8f77d707c75b0553ac43875193|
|PG8216-counter-name-post-v1|当6四100/CRC0/一session・実静的0/7反例・生成4|d9796aebcd3d6b9e3a516d5367f02616c1508b6933748b69c5da911ad41e3fb8|
|PG8219-counter-name-six-trace-v2|全1799physical/変更1・元1669byte不変/五architecture0・全155source|671663c32905d4e15ca0462f02d59d4759842a9e27ab908ee623d9f9850734af|
|PG8220-physical-role-guard-v1|実三role・12prefix反例・測定部差0、製品/architecture再演0|70aff03906f9593e9007d31d765a92df0825953a178c1c93ca0a81c216cb427c|

各公開証跡は evidence/provisional/上記ID/manifest.json。元begin/process/exit/log/XML/exec/Jar/coverage/static/javapは /home/mini/codex/project1/work/pgpt-runs/PG379 の同小文字ID（8219はpg8219-counter-name-six-trace-v2）へ保存。全own job真正終端、Source/input/実command/環境/OS/JDK25.0.4/ツール/時刻/終了code/hashは各元manifest参照。SDK15Jar/annotation/JUnit/agent/current六Jarを全前後hash束縛、古い内部M2/test-classesを使わない。

共有runner/postは固定slot・fresh Testcompile・単一exec、最小env/own空prometheus config/最初classpath空resource・NoBinder。PMD7.28.0＋既record fix、CS14.3.0、SB4.10.4.0/Maven3.9.12、JaCoCo0.8.15/ASM9.10.1、formatter1.36.1。actual parserは実値だけを読む、期待値は1747/SS literal/固定整数。期間・root/runtime・本番BOM/endpointの証明ではない。

## 全byte・traceと工具障害

全六Jarの1799classを旧完全mapへ照合し、変更は当MqMessageMetricRecorder.class一個だけ。元1669/他1798のdebug byteを含め不変、新class追加/削除0。元147sourceのうちMain/Test二つを変更、以前に製造・schema検証したPrometheus/Grafana八dataを別履歴として加え155ownerを追跡。旧source counterを現在へ合算せず、当6/40だけを実行資格に結合した。全五architecture rule0は静的byte読取で、Root/F03受入や実class初期化ではない。正式受入には所定全回帰が別途必要。

BUG1692/YKT1443：初回8218は既role付きweb keyへweb:を重ねた工具不備でpreflight終了1。原byte a7b2b30ea・失敗記録を保全、ownslot/architecture child未作成。修正ca8c6f143で三prior domainはrole-qualifiedをそのまま要求し、新8219で真正全1799を完走。current componentだけapi:を一回付ける境界・original全1669を別扱いで確認。558b48448で純guardを抽出し、8220が旧測定部差0・実三role/二重prefix/裸/別role/空の全12反例を検証した。製品40/正常six/architecture成功の確認再演0、検索だけの横展開完了にしない。

BUG1691/YKT1442は修正6246c954d・新8212/14/16/19と全三baseUnit根拠、BUG1692/YKT1443はca8c6f143/558b48448・8219/8220に結合して当限定範囲CLOSED、完了日2026-10-24。実VM等や未知refusal関連の障害をcloseしない。

## 計測・残件

開始20→fresh21残79/reset1793382075、同窓共有差1ppはPGPT専有費ではない。実N/T・工数null、usagebd3e7d83/11:50:36JSTは明示0/完全性未証明。原-v4-v5/開始1/3/6を保持。元計画の新backend PT8、追加発見の製品修正1、失敗後必要再試験/新source再認証・工具修正を分離。二runの80件や失敗33を合算して成功数にしない。これまでの旧source三run112/新22caseは履歴、今回の新source40/新8caseを同source全体152/coverage100へ合成しない。

正式1964PT/53scope・原190新受入0・工数null・QA051final/PTALT0不変更。実VM/Root/cohort/native/DB/Backup/鍵/intent/permit/配備/サービス・拒否未特定操作HOLDを維持。実runtimeはUNKNOWN、当sourceはhost候補で配備済みではない。通常区切りで停止せず、次の安全な未実施PG/PTへ継続する。
