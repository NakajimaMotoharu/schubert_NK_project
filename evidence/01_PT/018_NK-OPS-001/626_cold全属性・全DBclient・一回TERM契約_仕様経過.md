# cold全属性・全DBclient・一回TERM契約

対象工具pg1026/1027、N11/SSC244、BUG1009/1010、YKT778/779。Production変更なし、VM接続/DB/Unit/TERM操作なし。正式PT-WEB-20260925-24/1964PT/53scopeを更新しない。

| Test ID | method | 独立入力・期待値 |
|---|---|---|
| PT-DEP-1026001 | actual_literal_inventory_and_normal_close | 実ABCD4byte・固定SHA e12e115acf4552b2568b55e93cbd39394c4ef81c82447fafc997882a02d23677、全属性二読一致/正常一回close/閉鎖後拒否 |
| PT-DEP-1026002 | actual_same_bytes_chmod_between_reads_rejected | 実600→400、内容同一でもmetadata差を拒否 |
| PT-DEP-1026003 | actual_inode_replace_and_xattr_rejected | 実同内容別inode/実user xattr変更を各拒否 |
| PT-DEP-1026004 | actual_unsigned_extra_missing_symlink_and_wrong_bytes_rejected | 実extra/missing/symlink/ABCE4byteを各拒否 |
| PT-DEP-1026005 | null_unknown_path_hash_owner_contract | null/空/boolean-owner/../絶対/非正規path/control入力を拒否 |
| PT-DEP-1026006 | actual_nested_inventory_extra_and_group_write_rejected | 実nested正常対照、extra directory/770祖先を拒否 |
| PT-DEP-1026007 | actual_reservation_durable_exclusive_and_symlink_refused | 実O_EXCL/NOFOLLOW・file/dir fsync・600固定・同名再予約/既symlink拒否、原fileABCD保持 |
| PT-DEP-1026008 | all_roles_sql_independent_literal_and_rows | 手書きSQL literal全一致、migration/未知roleを対象、observer自身/専用parentだけ除外する独立5行、backend境界拒否。実DB未接続 |
| PT-DEP-1026009 | once_term_order_and_post_reservation_recheck | verify→pidfd→verify→durable予約→verify→send一回→wait→close、予約後世代変動ならsend無し |
| PT-DEP-1026010 | unknown_send_timeout_and_close_never_retried | injected send/wait/close/複合故障は一回で停止、primary同一性・不明close追加note保持。実signal無し |

fixtureは実hostFS/0700私有一時領域（終了後test-ownedだけcleanup）。署名鍵/DB/raw/token未使用。APIの純pidfd callback試験は実handoff成功ではない。全DBclient SQLの実server観測・pin/signature/approvalとの結合・全task/FDlock/連続起動禁止・UNKNOWN Ref保持・新cold実受入は残る。

v1新TDD実1/F1E4はWorkPG379/pg1026-host-contract-v1へ不変更保存。repository祖先がgroup writableなのでtrusted fixtureとして不適切、fixtureを既secure home祖先下へ移動（Production側mode検査を弱めない）。非正規`.`の拒否を追加。新v2実行command=`python3 -B tools/quality/vm/050_s1/pg1027_cold_contract_capture.py`、新only/clean source固定・hash・実log/終了code・前後source一致を照合する。未実行段階の成功/coverage認定なし、工具10caseはProduction PT数に加算しない。
