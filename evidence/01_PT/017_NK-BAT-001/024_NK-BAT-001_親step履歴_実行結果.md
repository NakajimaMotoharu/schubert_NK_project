# NK-BAT-001 親step履歴実行結果

探索static: 2026-09-13 04:55:22 JST終了/12.174秒/exit0、Storage/Batch compile＋com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check成功、未解決0。最初の短縮prefix spotbugs:checkはoffline plugin prefix未解決で未実行（04:54:49、/tmp/pgpt-step-static.log）、完全座標で再実行した。tool導入/版変更なし、未実行checkを成功にしない。再現commandは上記完全座標と421 JDK/M2指定、log /tmp/pgpt-step-static2.log。

PG163探索3: 2026-09-13 04:54:02 JST終了/12.140秒/exit0、BAT138～153/16件と値8/Storage8成功。独立SQL terminal10行、399 JDBC故障位置＋6複合close、履歴12列NULL/不正・99/100、borrowed所有/前後自己排他/rollback・同値replay、独立UTC/JST/歴史時刻、実rowlock/競合を確認。2実traceは020の独立literal一致、01927＋0171負canary成功。探索coverage全7class/31method/235line/160branch missed0。BUG176～178/YKT137～139は先行6a44bb8d→test是正、025の全対象/非該当根拠/追加testを参照。正式07/全scopeまでは未認定。raw /tmp/pgpt-step-explore1～3.log、環境421、JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、commandはoffline Maven batch -am -Dtest=BatchStepValuesTest,BatchRunRepositoryTest,LinuxFileLockTest test。以下は実装前履歴。

PG163/SSC055、PT-BAT-138～153。実装前仕様のみ、未実装・未実行・正式認定0。関連SS/PTは023、環境421、実行後にbranch/source/日時/command/exit/coverage/BUG/証跡hashを記録する。PG162の合格件数へ含めない。
