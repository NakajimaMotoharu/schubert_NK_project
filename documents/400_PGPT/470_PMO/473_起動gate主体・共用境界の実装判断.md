# 起動gate主体・共用境界の実装判断（SSC084）

2026-09-27。471の同一受入R1～R3を阻止する内部依存だけを対象とする。Astra/high補助1名の読取reviewを親がSS/code実物で照合。新しい受入分母や進捗加点は作らない。

1. SS321 §10/342 §4の管理readinessには専用Opsが必要だが、SS343/Unit/catalogはAPI/Web各5秘密だけ。普通serviceへmq-opsを加える方式は禁止。SS341のroot起動順controller内で独立管理sessionを所有する。
2. SS343のbackup0700/Artemis0700/staging0700は他主体の私有root。API/Webで6rootを開くことは不可能で、modeを緩和しない。既存StorageRootInspectionの型/SDS/dev/inoだけを全owner/mode/ACL保証へ読み替えない。root管理側で全配置を、app側で許可rootと保持能力だけを検査する。
3. WebLogApplicationRuntimeは内側DB/JMS probeより先にreply/replayを開始する。必須外側gateを完了してからruntimeへ入る。ServiceDatabaseAdmissionだけではschema/Flyway一致は保証されない。
4. Web parserのDB/MQ5key欠落はBUG261/YKT195で修正。共通sourceへ移さずweb.ymlの正規service設定として扱う。
5. API-localのcredential/JDBC部品をWebから参照/複製しない。共用bootstrap artifactの責務は厳格byte material/保持inode reader/固定role JDBC admissionに限定し、業務repository/HTTP/JMS認証modelを移さない。Storageのnative-only/no-JDBC制約は維持する。artifactとpackageの具体変更・全coverage/collector移行は着手時に追記する。

root→service gateの最小契約候補: 固定/run namespace root所有・app書込不可、bounded canonical regular/link1、NOFOLLOW保持inode/ACL前後検査。固定unitとfresh実Invocation/boot/release/config/root identities/Broker invocation/実Expiry outcomeに束縛し、再起動は毎回新規。時刻だけ・static OK・Inspector receiptの流用は禁止。親は既存maintenance排他とconfig/root/broker安定を観測→公開→子admissionまで保持、start不確定なら子の実終端を確認前に排他解除しない。子はgate欠落/古い/不一致/cleanup failureで非acceptingを維持し、独自singletonをshutdownまで保持する。本候補は未実装であり未認定。実runtime healthは別途継続する。

環境確認: host UID1000、systemd system/user running、sudo -nはinteractive認証が必要。unshare -Urは成功したが複数service UID/root所有配備を証明していない。host既存/etc/Unit/権限へ勝手な変更はしない。privileged隔離配備の最小手順を具体化した段階で、必要ならQAを先行起票して利用者へ支援を依頼する。現時点は独立実装・非特権の限定PTを継続できるため全体停止しない。
