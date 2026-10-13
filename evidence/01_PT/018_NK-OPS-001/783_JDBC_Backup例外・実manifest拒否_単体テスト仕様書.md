# PG2482 JDBC Backup例外・実manifest拒否

NK-OPS-001／MorningDatabaseSession.Session.observeBackup/retainedBackupSuccessful/failBackup/requireAbandonedRequest。SS343/353/354、SSC129/133/134、RD OPS009/DAT009・UI251。WBS-P017-01、N05参照費0。events0642群開始予算1/3/7ppのsubset、0643の測定停滞是正で追加費配賦0。

PT-MDB2482-001／mdb2482001：実隔離DBでbegin、必要に応じてFAILED二行を正規commitする。対象operation開始後だけgetAutoCommitに一回SQLExceptionを注入し、OBSERVE/RETENTION/FAIL/ABANDON四経路の例外を検査。別caseはowner Guard期限切れを拒否させる。期待=IOException、faultは一回だけ消費、Connection閉鎖・owner/advisory0、別admin接続で二行のstatus/attempt/count/開始終了が固定SQL後条件と一致。初期fixture製造に例外を成功補完しない。

PT-MDB2482-002／mdb2482002：正規FAILED二行へ、database handle不一致、configuration handle不一致、正しい両handleだが実DBはFAILEDという三manifestを提示。期待=資格を拒否、実DB二行と全count/時刻/error不変更、Connection閉鎖・資源0。manifestは独立固定時刻・byte/countの手書きfixture、Production結果からexpectedを作成しない。

実command=`python3 -B tools/quality/pg2482_backup_refusal_selected.py`（固定PYTHONPATH）。clean source・fresh PG2482-selected-v1・JDK25.0.4/PG18・Werror・二JUnit XML/FES0、PG2404全1643Main/成功fixture/依存byte不変、PG2474最新九nativeとPG2478v4の選択execだけを資格照合。VM/業務start/stop/Backup/ADMIN/reload0。全体回帰/正式451/100%認定は別未完。実結果・source/run/time・残counter・証跡hashは取得後に記録する。
