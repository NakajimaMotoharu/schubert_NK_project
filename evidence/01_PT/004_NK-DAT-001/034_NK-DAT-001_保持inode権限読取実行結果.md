# NK-DAT-001 保持inode権限読取実行結果

最新正式再試験: PT-WEB-20260909-39/source2236df45、2026-09-09 19:02:57～19:09:57 JST、dev-foundation、exit0。全体1059件（Protocol80/Storage42/API626/Web241/Batch29/CHR41）、6 Java moduleのline/method/class/branch100%、Production5 moduleの静的解析PASS。対象Test ID・個別結果・coverageはevidence/inode-security/manifest.json、SHA-256 `9191314838f85a54b1ffc0dc6fd69001fbac554a97c1f82bd5d50e4b40d59985`。全34scope/11collectorの同run/source/branch/hash/参照、017の1件・019の10件負canary成功。Current baseline不変、秘密pattern scan0hit。更新3参照は045/046、DB credential/接続は047/048、外側resource寿命は049/050で合格、通常writer/replay・main/oneshot・親OS/実backup/実NK CHRは未完了。以下は個別試験・過去の探索履歴（旧件数/hashを現在値に用いない）。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、dev-foundation、2026-09-09 12:40:24～12:46:41 JST、exit0。全918件（Protocol80/Storage42/API514/Web241/CHR41）、failed/error/skipped0、5 Java moduleの4種coverage100%/静的解析0。新8 PTは全PASS、line64/method12/class1/branch28/instruction352全missed0。evidence/inode-security/manifest.json SHA-256 `19e5a449530065e970acfc24744d5a1a7341b0e0f3f3b88c18503e2a1cc00121`。8collector/23scopeのhash/trace/負canary、V001～013/Current baseline不変、秘密pattern scan0hit。BUG-097/YKT-088はsource6dd862d0・本正式runで再試験完了。file reader/実systemd/main/親gateは未完了。以下は探索履歴。

探索2は2026-09-09 12:38:58 JST、12.155秒、exit0、dev-foundation/02949622後の未commit実装。Storage42件（新8＋旧34）すべてPASS、failed/error/skipped0、SpotBugs0。LinuxInodeSecurityはline64/method12/class1/branch28/instruction352全missed0、除外追加なし。正式root/証跡確定までは未完了。033/PT121～128、PG-D-133、SSC-049。

探索1は42件PASS/静的解析0だがbranch29/30で非合格。javapとJaCoCo line133を照合し、early-return用compiler生成Arena null guardを確認。BUG-097/YKT-088を修正前に02949622で起票し、Arena所有scopeの単一returnとprivate判定helperへ整理した。非null Arenaをnullにするtest改変や除外はなく、全native成功/故障/ERANGE/100並行を同じ期待値で再試験。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-storage -am test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inode-security-explore-2.log。実行環境Ubuntu26.04.1 x86_64/glibc2.43/setfacl2.3.2/JDK25.0.4、正式manifestでsource/branch/全tool/時刻/hashを固定する。

実ACLは独立44byte goldenへ一致、上限43byteはERANGEで拒否。file rename/置換後も保持inodeは旧ACLを読み、新openは新ACL、close後は失敗。実UIDと実FileStore flagを独立照合。READONLY true/falseと全errorはpublic call portからのliteral戻り値/flagで検証し、当機でRO credential mountを構築・起動したとは主張しない。Linux aarch64の許可ABI分岐は検証するが、実走行はx86_64のみ。実root-manager credential/IO reader/main/親gateは後続確認。
