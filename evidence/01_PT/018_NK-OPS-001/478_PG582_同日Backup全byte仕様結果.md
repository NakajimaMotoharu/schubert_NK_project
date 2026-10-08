# PG582 同日再実行Backup二step全byte独立検証

Program NK-OPS-001 / pg582_backup_oracle.validate / pg582_capture_backup.main、RD OPS009/UI251/SS331341353354/SSC200、Test PT-OPS-PG582-001～003。当Production969/schema028、通常run b62b6984とcutoff2026-10-08T07:36:21.802335Zだけ、旧PG577八SKIPと旧472全列保護は別封印scopeで維持。全十SUCCESS旧oracleを適用しない。

001: readonly当BackupdirectoryをPG579封印after/hash/九metadataに束縛し、SS341順序/canonicalJSON/独立SHA256/時刻/run/version/recipientと実MANIFEST、dump、config.tar、credentials.tar.ageの全byteを照合。二Backup全17column/id/attempt/成功件数1・2/失敗0/実sizeとbyte_count一致、旧row全列保護。dumpはpg_restore --list exit0、復元実行/ITST合格0。002: config八memberの名前・型・Root owner・modeと現在config全byteをNOFOLLOW/前後九metadataで比較。003: host私有age keyでmemory-only復号、固定十七credentialのRoot600/全bytehash/currentSourceを比較し、秘密の値/hash/catalogを公開せず、keyをVMへ転送0/平文保存0。

独立正常/境界/null/未知/誤hash/重複JSON/順序/canonicalbyte/時刻/row count/attempt負例は新2fixture＋既SS341literal3fixture、合計5成功。Productionをexpected生成に使用0、Pyflakes0。実command python3 -B tools/quality/vm/050_s1/pg582_capture_backup.py、Linux host/JDK25.0.4/guestUbuntu26.04/PostgreSQL18.6/age1.2.1、固定source commit/run/実日時/終了code/manifest/hashは実試験後追記。元Backup/DB/原本/全private保全、既service start/stop/退役を再発行0。

実行未実施、合格・coverageへ加算0、formal変更0。new-onlyhost PG379/pg582-current-backup-v1、私有VM/private/pg582-current-backup-v1.private.tar（dump/config/cipher、Git禁止）。全source/regressionの代替ではない。新作業経路は既PG573 groupの二Backup後条件のみ、着手前1.03/2.5/5.67pp群見積り内、親子/共通費を重複加算しない。
