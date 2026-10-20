# 1310 SS316 B2：管理bind/start・内側owner・ordinary配線

WBS-P018-05主/P005-03/F03参照0、BUG1547/1548/1553/1556/YKT1307、SS321342343354/SSC316/PG-D466。1490群開始1/4/10pp固定、前残.5/3/7内数・原v3v4不変更。S3b前半6170限定25/13/6172独立資格が終了後に四Mainと三Testを実装し、同sourceを固定する。工数/実N/T/専有費null、追加件数を完成率にしない。

API管理はbindでowner捕捉し、startを同stopLockで直列化・一回のみ試行する。実server.start完了前にはready/promote不可。stop要求が先行すれば再startせず、既close期限/実executor joinを維持。ApiProcessMainはbroker/管理/consumerの各取得前にResourceScope release/actionを用意し、固定RetainingUnknownを選択する。管理はbind後・保護action内でstart。最内側consumerからの逆順停止・全完了marker位置を維持し、API ready単独を親全体完了にしない。

ApiApplicationPreparationはnative entryに限りcodec→transfer→asset→Outboxの各未知releaseでそのframeを保持する。normal entryの既TWR/例外順位、借用graphの31handler/SQL/credential/時刻/Outbox未start状態を維持し、業務graphを一箇所のassembleへ抽出する。Web ordinaryは返却前factoryの固定保持entryだけ接続、返却済みphase/実行/停止契約は不変更。実Root/admission/Main成功をcomponentで偽造しない。

独立oracle：ApiManagementBindTest.bind316001..005（新5@Test）=bindだけではrelease0/DOWN、実start/一回promote/health、未start closeと実socket再bind、setup三位置×RTE/Errorの元例外/owner回収・二度start不可、start-stop実競合と実executor終端、自己所有二childでstart失敗＋stop UNKNOWN/外側markerなし。ApiPreparationOwnerTest.prep316010..012（新3@Test）=nullは取得0/factory例外identity、同Outbox未start借用・復帰前close、正常/IO/RTE/Errorのreleaseとnormal例外順位・nativeIO固定redaction。fixtureのloop/childをJUnit件数へ加算しない。

着手前PT_DEFAULT：所有ローカルephemeral HTTP/未start Outbox/自前有限child、外部通信/DB接続/JMS実送信/原本/鍵/実VM/cohort/intent/permit操作0。先行6174は全六format/compile型null/Test-Werror/SpotBugsだけでJUnit/XML/exec0を要求、851Java/1667Main・コード四/Test三のexact差分。定義/生成/pyflakesを確認しnew-only一回、source/run/command/日時/終了/hashを結果へ保存。次に同sourceの関連API/Web＋必要全体をまとめて実施し、部分未測定を100へ補完しない。拒否依存の実経路はHOLDのまま、PTALT代替0・正式/QA051不変更。
