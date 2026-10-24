# 計測sourceの追記訂正・横展開結果

2026-10-25/BUG1726/YKT1477、主P018-09/487。元PGPT-20261008-2069はsourceだけ旧fb5bde926で、1838・PG8950/8952の実sourceはfb9fce0f91de3d9fdfa634fe277592700f915e45。修正前915/916起票後、PG8974でhash/source/終了0を結合し、追記訂正event PGPT-20261008-2074を一度だけ追加した。元event全文は不変更、元新8/必要36/actual44・二Main四100はfb9へ関連付けるが、再加算/製品再演/費用再配分/旧source成功転用は0。

独立照合対象：2058→PG8858 source0f065c63f、2060→8872 source28befbf2c、2064→8914 source3359b1489、2066→8936 sourcefb5bde926は各一致し修正不要。2069のみ不一致→8950 manifest46b55585fd64cb659bfc0066327219c5b690bd9f7b47f07e8d931e9dd025fb3b /8952 manifest85aac967c065ccad21eb917a0787fa96fc5bcd8c581bb254738aadccc087e4a0でfb9へ追記訂正。対象五件を実照合し検索だけでcloseしていない。

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg8974_metric_source_correction.py` 終了0。新source_evidence_binding helperで実manifest hash/source/actualExitを確認、wrong-source/failed-exit/bool-exit/missing-source/wrong-hashの5 metadata反例を拒否、同一訂正がないことを前後検証。scan/job/source内容の変更0。411/477へ以後source転記でなく証拠結合を要求する再発防止を追記。manifest `evidence/provisional/PG8974-metric-source-correction-v1/manifest.json` SHA256 b7d5e1f4216601b0ac181c10263325395fd9be008802a05598ecbbb702ed0e40。製品PT/coverage/全体受入0。修正commitは本結果と同commit、限定CLOSED。過去費用・元見積・正式1964/53・技術653/34・全actualHOLDは不変更。
