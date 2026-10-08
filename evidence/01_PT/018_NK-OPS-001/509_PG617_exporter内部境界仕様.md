# PG617 exporter内部観測・実FD仕様

Program NK-OPS-001、NativeCoveragePrivateFile.export/write/Io/NativeIo。RD OPS009/TST004/SYS002004、UI212/251、SS342/343/354・SSC193/196、PG-D399、WBS P018-08.01（共通実装費 .67/1.67/3.67pp）、.02固有driverは別費を重複加算しない。正常既VMsource23b/PG600の8nativeとは別sourceのcomponent試験。正式受入/全工程完了ではない。

PT-OPS-NEXPORT617001：固定六directory/cgroup/phase/nameの独立literal。Root API/Webのterminal/before-exec、ordinary API/Web/Inspector/Bootstrapのterminalを実tmpfs新tree・実FD・実byteで出力。期待literal byte、物理0600/single-link/hostUID、sync一回、全owned FD正常close/残0、全観測再照合。Root UID/GIDはmodel metadataのみ、実Root権限/Unit成功と主張しない。
PT-OPS-NEXPORT617002：初期UID/env/cgroup/NSS/ordinary六条件、null依存/未知name/ordinary before-execを拒否。期待出力作成0/残FD0、sanitized例外。expectedをprofile/getter/subjectから生成しない。
PT-OPS-NEXPORT617003：祖先/targetのowner/mode/ACL/link/inode/device・filesystem/RO・欠落/symlink及びfile metadata/size異常。各拒否時の原値/部分出力隔離・FD0、既存出力を変更しない。
PT-OPS-NEXPORT617004：target close/reopen identity及びparent/service/run各再検査漂移。全close試行・owned FD解放後の非成功と元byte保持。
PT-OPS-NEXPORT617005：各scope/file/sync/observer例外。正常に解放されたFDとreported close failureを区別し、ResourceScope正常を捏造しない。異常は実close後にエラーを注入し、試行と残FD0を確認。
PT-OPS-NEXPORT617006：末尾env/cgroup/effectiveUID/NSS・ordinary全九field変化。全directory scope閉鎖後に拒否、出力はbyte一致で隔離保持。変更before/after値は独立literal。

実行予定：Java25/Maven offline bootstrap selected NativeCoveragePrivateFileTest/NativeCoverageExportTest/ChildStartupContextTest/FixedNativeCoverageCheckpointTest/FixedServiceIdentityTest、format/NullAway/Spotbugs、既exec保全→absent/newsession・XML/coverage/sourceguard/hash。全source固定後コマンド、実exit/日時・XML/FES・静的/coverage未達・BUG/YKT・証跡manifestを結果時追記。失敗済み実装仕様違反は修正前915、TDD未実装初期compile/testは未完として保持。全scope/regression/nativeは別sourceへ旧成功を流用しない。
