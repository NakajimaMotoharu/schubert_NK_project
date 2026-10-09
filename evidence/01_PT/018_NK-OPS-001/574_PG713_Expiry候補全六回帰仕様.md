# PG713 Expiry候補のfresh全6回帰

NK全6/SS311～355/451、PG-D404/573。trigger=Production CleanupExpiryExecution変更1outer＋2inner/新11PTと先行同byte新2PTがまとまったため、当sourceを固定し全6moduleをfresh clean/compile/test/static/XML/JARへ一回実行する。管理文書だけでの不要再全回帰ではなく変更群の必要検査K01、P017-08/N15へ二重実行費0。

command `python3 -B tools/quality/vm/050_s1/pg713_full.py`、全source/tools/pomのhashguard・HEAD/clean前後固定、JDK25.0.4/Maven3.9.12/PG18.6/Artemis2.56/Node24.19/Spotbugs4.10.4/JaCoCo.8.15。W/pg713-expiry-six-host-v1新onlyに実start/end/exit/XML/exec/静的/JARをコピーする。終了0、F/E/S/flaky/not-run0、全suite/testcase各一意、静的6zero、当source/main1614/変更1outer追加2innerを独立collectorが照合して初めて群合格。事前予測3502PT/517suiteは期待集計確認用で、実完走するまで認定しない。

Coverage100は後続同source実native/残異常matrixを含む別gate。旧9bd/PG680/native9は保全、candidateへ旧変更classbyteをNoMatchで合算0。私有raw XML/log/exec/credentialはGit0、sanitized summary/manifest/hashのみ公開。source/commit・実結果/coverage後記。formal24/1964/53不変更、IT/ST合格宣言0。
