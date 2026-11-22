# Bootstrap純例外の通常試験と静的非生成

NK-OPS-001、WBS-F03/2-2-b／P004-05参照、SS311/332、SSC-095/461、PG-D1179、451 §5、YKT-2863。旧PT-DB-ADMISSION-FAIL001はprivate constructor反射の履歴。現 `c313387dd2cf431b27eec7aaeef7447ce34519ae` では削除し、公開package操作の旧6件を同一本文のまま実行。対象JdbcAdmissionFailuresとJdbcFailureGraph、既StorageIoExceptionの限定4物理を現正規2 JARから個別認証。実JDBC、DB、サービス、外部環境、保留fixtureは起動0。

PG42918でPT-DB-ADMISSION-FAIL002～007六件成功。旧独立の優先20セル、null、同一例外、Throwableのcause/suppressed/SQL next、異なる所有を確認。PT-DB-ADMISSION-STATIC001ではjava25のclassfileでfinal、private no-arg constructor一件、static method二件を確認した。通常試験へ足さない。Checkstyle指摘0。生coverageは当一型の行11/13、method2/3、class1/1、branch16/16、命令45/52。未測定はprivate constructor。旧7の反射実行や未測定は加算しない。

現実行の仕様・対象source、実行command、元JAR hash、JUnit、独立原exec CRCと残欠落は公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42918-bootstrap-admission-without-private-reflection-v1/manifest.json` SHA-256 `1afd4c994d153a4fe0f1371b99a4e59d315adf8108dcb932114d2cb000a7f921`。YKT-2863／全451は継続。
