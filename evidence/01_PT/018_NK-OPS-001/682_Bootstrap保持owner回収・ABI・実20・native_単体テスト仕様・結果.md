# 682 NK-OPS-001 Bootstrap保持owner回収・取得前ABI・実normal20（限定PT）

関連：RD OPS009／UI251／SS343・353・354／QA047、SSC276・277、BUG1156～1158、YKT924～926。主WBS-N15.01、P018-01/08は参照（費用二重計上0）。Productionは2741c4546afad6c1e8b6efbd53dfb58144edf7bb、署名current PG1638/BOM195e0668…、boot3d69。既存ADMIN・元Root真正DONEを維持し、Root/Backup/配備/VM起動の再演0。工具sourceは対応manifestのoperatorSource、Java25.0.4/PG18.6/Python3.14/JaCoCo0.8.15/pyflakes3.4.0、開発hostと専用LAN隔離VMで実施。

| Test ID／対象 | 独立期待値・fixture・操作 | 実結果 |
|---|---|---|
| PT-OPS-BOOT-1721-VERIFY／旧Pg1719.open・Expected | 現4桁labelを資格して全scope正常返却、業務起動0 | 旧3桁制約でDB取得後・Ref前retain。最終143/closeUNKNOWN、合格加算0。BUG1156、凍結111/ログ不変更 |
| PT-OPS-BOOT-1723-PROOF／全actor・原本読取 | 全99FD/argv/exe/Root/子0/soleM-A/OFD、全24DB/32設定/187署名/原本Backup/native18不変。DB期限後serverpeer/advisory0を正常closeへ換算しない | actual0/proof3b84d06a…。先行1722のlivepeer仮定拒否は別失敗/signals0 |
| PT-OPS-BOOT-1726-RECOVERY／fresh guard・pidfd・hostgate | 当31/90共有/run二時刻のみ合法進行、他97FD・全target/権限不変、fresh全像を耐久保存後・同像再検査から当Javaだけ一回TERM、15秒終端30秒reap。kernelgateは旧owner保持から新operatorへ引継ぎ | actual0/freshproof22cf32ce…。当383695のみ・DB/M-A0、forceunlock/他PID/DBterminate/SIGKILL0。1724旧29/32guard失敗は予約/TERM前、再送0、BUG1157 |
| PT-OPS-BOOT-1727-POST／独立全post | 別接続の全原値及び旧資源0/新Ref正常、旧before6b29aa3f…完全一致 | actual0、唯一ADMIN/674batch row、4namespace空/仮credential無し・全原値一致 |
| PT-OPS-BOOT-1729-ABI／Pg1728Expected・beforeOwnership | 3/4桁・suffix1/32・backend2/MAX、許可role/readOnly/advisory組合せ、null/空/桁不足超過/非numeric/全角/改行/過長/foreignrole-db・禁止組合せ。literal fixture、invalid時ownership callback0 | Werror0、argument8/input5/actualExpected60/監視fault307 check成功。期待値はproduction methodで生成しない。dummybackendは入力ABIだけ、実peerへ代用0 |
| PT-OPS-BOOT-1730-VERIFY／新版120閉包 | file/hash/import/署名187とactualconstructorをM-A/DB前に検査、同owner peerを監視、verifyはUnit/SQL業務書込0、全scope正常返却 | stage0/verify0（15.410497s）、旧120/111とは別namespace。旧失敗をhotpatch0 |
| PT-OPS-BOOT-1730-EXISTING／BootstrapAdminMain | 承認既存ADMINだけの専用Unit正常20、PID1の当世代DONE、30秒Unit期限・DB全24不変、仮credentialを同inode rename-no-replaceで私有退役、DB/Ref/M-A正常返却 | execute0（工具38.547168s）、実Unit1.759522s/Job120580、正常20。新ADMIN作成/元業務再演0 |
| PT-OPS-BOOT-1731-POST／独立normal20全post | captured normal20/PID1が前提、GCから過去成功を推論0。元全24/32/187・原本/Backup/既credential不変、認める差は専用Unit世代、仮credential親dir時刻・当native2fileだけ。現在全資源0 | actual0/afterSHA d44d02a87793a5fe611268dfd8a072a24c03293b51c1224f05a74dcce45e7488、全後条件/新Ref正常、仮credential2は私有のみ |
| PT-OPS-BOOT-1734-NATIVE／readonlymetadata9 | 読取atimeだけはobserver副作用、9field/hash/byte/ACL不変は必須。独立atime-only許可・他9field単独変化拒否 | actual0、21525B closing。同sessionのterminal pointは選定せず合算0。旧1732全stat拒否/1733入力なしは失敗保全、BUG1158 |
| PT-OPS-BOOT-1735-CRC／NativeSessions/NativeCoverage | 当普通8＋当Bootstrap closing1、各actualsession/window/hash、同Main全6JAR/class CRC0、資格済API5のexecを別join。旧4d6/別採取点のimport0 | actual0/9stream/CRC0/serverSHA4801fb7fd3c54a5af7494edd98ec35f624b68e5aed197d88b0df4b5530971458。残873/169/9/715、四100false |

実行command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes runtime> python3 -B tools/quality/<各上表pg番号の工具>.py`。1730のみ引数`stage`/`verify`/`execute`を各新slot一回。hostgate中に別guest診断を発行せず同job/logのみ、回収前の失敗phase静止のreadonly資格はSSC276と区別する。独立hostguard/kernelqueue試験5及び当FD/layout反例込み11成功、meta9 actual生成functionの独立10観点成功。工具check数をProduction PT数へ換算しない。

新Main coverage実測873 line/169 method/9 class/715 branch未網羅、直前900/171/9/716から27/2/0/1改善。資格済3596回帰のMain byteは同一だが、新Test追加後の全3597は未実行。既存API5の結果を全回帰へ加算しない。正式PT-WEB-20260925-24/1964PT/53scope/wholeleaf増分0、PGPT/ITST未完。raw credential/DB/native session識別情報・秘密keyはGitへ格納0。

証跡はWorkPG379の各固定slot/manifest/payloadとLAN PG1735-native-v1。公開682_manifest.jsonはsafe結果・hash・終了code・sourceだけ（raw私有0）。状態=当保持owner回収・新Bootstrap ABI/normal20/closing native限定確認済、fault/replay/Inspector/Resume/全四100/CHR/正式451/trace/引継ぎは残る。
