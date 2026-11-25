# CI・BOM工具の相対Mavenキャッシュ指定

Program NK-OPS-001。WBS-P018-02/2、SCM-005／RD171、UI201/243/261、SS352 §13・SS354。実キャッシュやMavenは起動せず、合成worktree、空白を含むcache名、同名ディレクトリを持つCDPATH、引数を記録するwrapperを独立fixtureとした。

| Test ID | 入力と操作 | 独立期待値 |
|---|---|---|
| PT-OPS-CI-PRO006 | Protocolの合成wrapper。CDPATH設定時に相対名、次に作業dirにはないcache名 | 指定作業dirの絶対pathが1引数、不要stdoutなし。作業dirにcacheがないと終了2・wrapper起動なし |
| PT-OPS-SBOM-029 | BOMの合成wrapper。上と同じ相対入力と欠落 | 指定作業dirの絶対pathが1引数、stdoutは生成したBOMの1行。欠落入力は非0・wrapper起動なし |

PG43562、source `667558f950329245e67201c1a0ea687d994bdae1`、bash構文2件成功、`python3 -B -m unittest -v test_verify_protocol_ci test_generate_maven_sbom` で工具試験11成功、失敗・skip・未実行0。修正前の二工具に同じ最終fixtureを入力して新規2件の失敗を確認済み。原PG43560の仮試験名は既存仕様と重複していたため訂正し、最終の11件と重ねて成功数に加えない。両側の出力は個別hashで保存。製品PT・coverageの変更0。BUG-3714／YKT-2914。配布承認、実CI、同候補の署名付き配布と全451は保留。

- manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG43562-release-cache-path-corrected-id-v1/manifest.json`
- SHA-256 `311ae4b933c08a8a9a8f2d753f1d310e4c685affa587aa14bd16d131e4b2010a`

BUG-3862／YKT-3000。ShellCheck SC1007を再確認し、文字列として空のCDPATHを二入口に明示する。元の相対パス、CDPATHの囮、cache欠落の試験を含む現12件を再実行する。先行の正規SBOMの入出力結果およびProtocol全製品PTは各元証跡で保持する。実製品試験の再実行は行わない。
