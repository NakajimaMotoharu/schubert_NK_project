# Context補助件数二件・是正仕様と結果

TOOL-CONTEXT-CARDINALITY001/BUG1958/YKT1707/PG-D734。開始savef60feaf1dda04b5789be1e235837aeb210e28fd1/push33227真正0、実行中source d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec。二対象の履歴sourceは4b5f6faa0とd8a2b7952で分離し、成功PT/coverageを合算・移植しない。主F03の追加工具是正費・着手前0.5/1/2週次pp cap10、原七Map1/2/4とv3/v4/v5旧見積は不変更。fresh共有58残42/reset1793599188/短期非提供ordinaryAllowedtrue/券0、N/T専有費/工数null。

PG12201-audit-metric-context-v1/hash12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2はsource4b5f6faa0/rawRetained3/sourceContexts5、review5 ID（04748/04749/07954/07955/07956）と元12198 static5に対し誤った3を保存した。PG12231-check-health-context-v1/hash2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86はsourced8a2b7952/rawRetained3/sourceContexts2、review2 ID（00994/00995）と元12228 static2に対し同じ3を残した。意図したsubsetという宣言/ID根拠はないので5/2が正値。元byte/hash/元終了0は保持し、補助metadataの誤りを製品試験失敗へ変更しない。

予定12272の追補では、元static manifest/reporthash・context manifest/reviewhash/sourceを認証し、原10690とactual XMLをjoinしてselected ID集合がreviewと一致することを確認する。rawRetainedはSELECTED_REVIEWED_RETAINED_FINDING_IDSの件数としてIDから導出、全static rawとのscope差を別記する。宣言fieldの3だけで結果を数えず、過去原本を変更せず正値と訂正対象field/hash/理由を保存する。別12274は同じproduction/helper methodでexpectedを生成せずXMLと固定IDから再算出、誤3・別source/ID・重複/欠落・subset混同・実PT水増し等metadataを拒否する。

直系family七（12111 authz三、12141 Batch一、12175 audit三/全static五の正しいsubset、12201 Metric五、12231 checksum二、12246 Main四、12260 Bundle七）を件数/ID/scopeで横展開する。修正対象二以外は具体ID・分母と非該当根拠を残し、Main subsetの全current rawが未測定ならnullにする。消費側12203/12233 post、12206/12236 completion、12202/12232 trace、12210/12240 setと凍結済み2307/2310について、誤fieldを使った件数か、正しいrows/static値を使ったかを確認し、補助field検査不足と製品結果への影響を分ける。

原Product19/8・実static5/2・counter/CRC/XML・現raw8597/累計820/追加8/refs3114/pending660・正式1964-53/個別17-190・QA051finalと451条件は不変更。新build/JUnit/PMD/normal/VM/job/Root/Backup/署名/配置/permit/鍵操作0、既成功/失敗/Current/原本全保全。凍結済みspec/result/completionは編集せず本追補へ参照を結ぶ。実結果/command/hash/独立post/YKT消費側/保存commitは以下へ追記し、完了前に成功扱いしない。

## 実結果・追補受入

実commandはrepo cwdで `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg12272_context_cardinality_supplement.py` と同12274_context_cardinality_post.py。両lint/body終了0。追補manifest `evidence/provisional/PG12272-context-cardinality-supplement-v1/manifest.json` SHA256 `d2dbc3890af82f6a5dade993e3ee4e18198f303f35951f105d40b22a8c3a9373`、独立post `evidence/provisional/PG12274-context-cardinality-post-v1/manifest.json` SHA256 `8da37464e00bf938e289cde878df65bd016b418ea140b38bfd74469343911544`。独立postは固定IDと元XMLから5/2を確認し、2domain各19＋全体11＝49異常metadataを拒否、原manifest全hash不変。

family七は12111三/12141一/12175三（全static五の明示subset）/12201五/12231二/12246四/12260七。誤二件のみ追補し、他五件は選択ID集合と分母の一致で非該当。Main subset二件のwhole raw未測定はnull。直接消費側八entryは12203/12233/12206/12236/12202/12232/12210/12240で、AST上rawRetainedの読取なし、元review/static集合を使用する値を原manifest/hashで確認した。generic bindもsource/hash/終了を照合するのみ。当調査は八直接entryに限定し、全世界のtransitive consumerが無影響とは主張しない。凍結済み2307/2310と元postの補助field検査不足は履歴として維持する。

WBS追補は12276-context-cardinality-trace-v1 SHA256 `7b9374e4efec869b9fd8116f9662583800987687fa85d99ea5b1dc048f80418a`、独立12278-context-cardinality-trace-post-v1 SHA256 `fdbc6c572ac7dfacd90d2828ef2bde0acc1e8ca015c1b095a64dfe10ba47ccc4`、checked entry各終了0。485二sectionへ訂正参照を追加し、486はinventorySHAのみ更新。原artifact/requirements/983sourceRows/owner-cost/予算/受入は不変更、全WBS監査は前後同じHOLD終了1であり合格へ変換しない。411へ集合由来の件数・一意selector・immutable追補規則を反映した。

BUG1958/YKT1707は補助件数二件と直接family/消費側の限定是正・再発防止確認完了、保存commit待ち。製品PT0/新source是正0/正式受入0、raw8597/累計820/refs3114/pending660/正式1964-53・17-190・工数nullは不変。実行source D8は補助工具の実行地点であり、4bの製品成功をD8へ転用しない。
