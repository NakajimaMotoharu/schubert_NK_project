# PT-OPS-ROOTCTX-010 / PG2220

NK-OPS-001/RootStartupContext.NativeIo.serviceRootUid/read、SYS002004/OPS009/UI212251/SS342343SSC137/451。Mainsource3b7f（全1643/三semantic一debug物理四差の2125資格）、testSourcec7f08aae679997336699c51a706425025fdc5a31。

目的: PID1/非正/整数上限超の入力をproc読取前に拒否し、普通利用者の自己proc読取をserviceRootとして許可しない。fixture=LANordinarymini/JDK25.0.4固定、PID入力Long.MIN/0/1/MAX+1/Long.MAX及び実自己PID。独立期待=各IOException「startup context unavailable」、自己UIDは非0、Root権限付与や他process操作無し。期待値をproduction methodから生成しない。null契約=PIDはprimitive long、ioはconstructorinvariant。native正規Rootの正常処理は別実経路で確認し本negativeのみで100認定しない。

command=PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes runtime> python3 -B tools/quality/pg2220_root_uid_host_selected.py。current2124全6JAR/hostexecを2125hashへ照合し、既fixturebyteは前後不変。新test/launcherを別classesへjavac-Xlint:all-Werrorでcompile、固定JUnit一method・新JaCoCo単一hostexecで実行。Main再compile0/VM動作0/旧0fdnative合算0、全6jar Analyzer noMatch0。

actual0/1PT/FES-aborted-notrun0/javacWarnings0/CRC0、manifest55defb7a1ed2a5196dafb33579326bfb50d165f68a14d5cc2918d81ba4dbd572、payload31177d5fd057ce17c6af532fdc473366deb3eec30d64078795d820a1a79f8d43。sameMainhost-only残L3725/M624/C37/B952、旧currenthost基点3729/626/37/956からΔ4/2/0/4。kernel negativeの実行であり無意味assert/反射/到達不能/coverage除外0。全counter100・当latesttest統合full/静的・新native/CHR/451は未受入、正式1964/53/全leaf0。

LAN runs/PG2220-selected-v1/tests.xml/selected.exec/六coverageXML/manifest.safe.json、hostW/PG379/pg2220-root-uid-host-selected-v1安全manifest/私有logを保存。実時刻・commands・libs/bytehash・input・終了codeはmanifest参照。秘密情報/他procraw/実sessiontokenは公開しない。群着手専用計測が実装後となった欠測はevent0578に明記し、事後開始見積り・個別費推定0。原見積り/v3不変更。
