# PG6316二反例再現・Outbox二MainPG・86仕様

元72488/PG6316/Test-only source `3bb2339f702c91b51476e17e22723da193638174` は02:28:46.310167Z～02:30:05.456587Z真正1/phase0,1/Maven1。実XML32/6/F2E0S0、宣言38/9との差6/3は未実行（API既定4/1とbatch2/2）。初期green工具の未実行guard仮値36/7を原結果32/6へ束縛し直しただけで、独立Test/oracle/期待値の変更0。原manifest `573c34705494563f7794b316798f020866bf1021db20142719eed636b60190b1`、二XMLは公開PG6316-outbox-graph-red-v1/manifest.json参照。API生成0/0 targetはpost-test coverage未実行のplaceholder、100扱い0。

001は最初のSQL.suppressed Errorでworker alive、002は同graphで期待Errorに対しthrow無しを確認。残graph/普通cycle後段は未到達のまま保持。BUG1572/YKT1328/SSC322/PG-D476に従い、二API Mainだけを修正し全Test/期待値/gates/Currentをbyte固定。send mark前とworker retry前の純粋identity-visited graph確認で同一Errorを伝播し、Error無しの正常失敗分類・lease/backoff/SQL/close/rollback/固定redaction/公開APIを維持する。新Main class/module/外部権限は増やさない。

次のPG6318新only選択は実宣言86/15、既12/default・API OutboxFailure6/Dispatcher20/Owned6・Web Request9/Log7/Dispatcher9/Replay9/Client8を列挙する。元red二Testと未到達matrix、既正常/境界/null/例外/DB・broker/重複・再送を同sourceで実施。38 redと84旧成功の算術加算ではなくactual XMLを確認する。

command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6318_outbox_graph_green.py`。全Main/Test/gates固定のclean commit/push後に一回実行、真正終端/原artifact回収前に変更しない。green未実行・compile/新counter未測定をPASSへ計上0。0後に6320で元XML/六Jar/全8511667/二physical差分/actualcounter/static rawを独立照合し、PG/JVM・必要同source品質と横展開を閉じる。実VM/current/Root/cohort/native/拒否PTの代用0。

正規JDK25.0.4/Maven3.9.12/既Spotlessで当二Mainだけformat、元44678結果はcheckpointへ保存。新green/qualifierのinventory/source/namespace/lint一工具定義0。共有残64/secondary不明、usageba93976b/N-T専有費工数null、群1537/原/v4固定、正式1964/53・17/190/QA051final/PTALT不明・全保全物/HOLD不変更。通常赤/PG/commitで停止せず同経路を継続する。
