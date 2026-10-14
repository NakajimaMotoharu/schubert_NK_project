# PG2604 permit DB readback両lock/schema境界

NK-OPS-001/MorningDatabaseSession.Session.inspectPermitDatabase、SS341/343/353/354/SSC129・451、WBS-P017-01.03主/N05-K01参照費0、group0686着手前0.5/1.5/4pp。PT-MDB2604-001：実隔離PG18でBackup失敗二row→Cleanup実advisory handoff→独立七terminal→Expiry RUNNING一row/実handoffまで進め、VALID/initial-heldfalse/final-heldfalse/schema SQLExceptionの四caseを確認。期待=両lock存在かつfresh schema時だけdata readback、他はIOException。Release factsは明示literal PUBLIC形のデータfixtureで、実署名/Root/permit発行資格ではない。OS gate、実runtime admissionの合格へ代用0。

全十rowのstep/attempt/status/byteをliteral期待に照合し、全11SQL値を前後比較、Connection/client/advisory0を確認。固定schema callback以前・以後のHELD投影だけを変異、実PGの所有操作/transactionを保持し、VM/Root/Backup/ADMIN/stop再発行0。全Maina79/全3657/現在native九同byte/CRCを要求、旧source/native輸入0。

command固定PYTHONPATHのpg2604_permit_database_selected_test.py→clean source固定→pg2604_permit_database_selected.py。工具二fixture/javac-Xlint-Werror0/限定1JUnit4case/FES-aborted-notrun0要求、実未発行。旧3657/正式1964-53へ件数加算0。Main変更無し、残技術794/156/9/551の対象を限定改善する。
