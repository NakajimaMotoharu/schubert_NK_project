# NK-DAT-001 保持inode権限読取実行結果

探索2は2026-09-09 12:38:58 JST、12.155秒、exit0、dev-foundation/02949622後の未commit実装。Storage42件（新8＋旧34）すべてPASS、failed/error/skipped0、SpotBugs0。LinuxInodeSecurityはline64/method12/class1/branch28/instruction352全missed0、除外追加なし。正式root/証跡確定までは未完了。033/PT121～128、PG-D-133、SSC-049。

探索1は42件PASS/静的解析0だがbranch29/30で非合格。javapとJaCoCo line133を照合し、early-return用compiler生成Arena null guardを確認。BUG-097/YKT-088を修正前に02949622で起票し、Arena所有scopeの単一returnとprivate判定helperへ整理した。非null Arenaをnullにするtest改変や除外はなく、全native成功/故障/ERANGE/100並行を同じ期待値で再試験。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-storage -am test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inode-security-explore-2.log。実行環境Ubuntu26.04.1 x86_64/glibc2.43/setfacl2.3.2/JDK25.0.4、正式manifestでsource/branch/全tool/時刻/hashを固定する。

実ACLは独立44byte goldenへ一致、上限43byteはERANGEで拒否。file rename/置換後も保持inodeは旧ACLを読み、新openは新ACL、close後は失敗。実UIDと実FileStore flagを独立照合。READONLY true/falseと全errorはpublic call portからのliteral戻り値/flagで検証し、当機でRO credential mountを構築・起動したとは主張しない。Linux aarch64の許可ABI分岐は検証するが、実走行はx86_64のみ。実root-manager credential/IO reader/main/親gateは後続確認。
