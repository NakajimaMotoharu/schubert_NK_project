# NK-PRO-002 Semantic未網羅条件・実行結果（是正後同source検証済み）

## 修正後sourceの真正結果（2026-10-25）

修正source `fd3d04df5710ca28f0e34f919cbc103e569a607b`、新Testの同値layout定数化だけ。修正前000270の動的結果を移さず、現sourceのnormal/静的/実15/4/独立postを実施した。全PayloadSemanticValidatorのline315/315・method38/38・class1/1・branch197/197（全missed0）、F/E/S/aborted/container failure0。**当classだけの四100実測**であり全Program/全source/CHR/正式受入ではない。新SEM3件は本群一度だけ新規ID、旧PAGE3/必要既存12/修正前15の手戻り再実行と混同しない。

| 現source証拠（各evidence/provisional下manifest.json） | SHA-256 |
|---|---|
| ../018_NK-OPS-001/.../PG9694-semantic-direct-fixed-six-compile-v1 | 7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a |
| PG9696-semantic-fixed-host-v1 | 54b0e549a70cf6a0928a3a467d00ecea68dfc745b9e75120046c978ada1458e3 |
| PG9698-semantic-fixed-post-v1 | c4695d0343472bc44e4998c78e5ed331ae7c7cdedfd523e84493df4a7ce99839 |
| PG9700-semantic-direct-fixed-static-v1 | 5c749b367ae03a141e6b6ba256a6900de0980b58d77d21e42af7a81dd0b5abee |
| PG9702-semantic-fixed-quality-source-post-v1 | 4b5478aefdf326b64aec579988cf4fd53795b0013715de1fc60d3eaddcc1d749 |

9700は現Test PMD/Checkstyle指摘/処理error各0、原規則/抑制/除外変更0。9702は新normalの全1843Main classを9666v2の全入力class byte/hashと独立比較して同一・旧外部依存のhash不変を確認したため、既Main SpotBugsの純粋同byte解析根拠だけ再利用し無変更の全六解析を反復していない。元static解析source3154の表示を保持し、現sourceで再実行したとは記録しない。全正式same-source/run品質への合格拡張0。

現Main965/Test826/Java1791、旧1911Test class同byte＋新一class＝1912。新Test SHAa1febb6e/三method/TestID/011の当commit byteを照合、定数化を逆置換すると原source文字列と完全一致し、入力/assert変更0。Mainの主担当は原941artifactのP002-02、追加Testは同担当候補でmaster登録は後続。registryの1782/1790は3154の限定履歴を保持。BUG1756/YKT1507はfixfd3d04df5/origin一致、原静的1・元source/原証拠d8d1995e8を保全し、Test静的scopeだけcloseする。

最新fresh11:26:48UTC sharedused9/残91/reset1793513544、開始9→9丸め差0≠専有0。実N/T/配賦/工数null、usagec5c2bc72。元計画の不足三境界を補完し、別に同値定数化/再compile/PT15は手戻りとして記録。次はnamed type/canonical fixtureの残通常PT/当source所有traceへ進み、完了済みsemantic-only再確認のためだけの反復はしない。正式1964-53/17-190/QA051final/全actualHOLD/G07残4493/全WBS監査HOLD不変。

## 修正前sourceの原結果（履歴保全）

2026-10-25、source0002706babad635c5ca7ade76cdbaee134ace432、群2206/011、Main最終64446。新SEM001～003を含む15件/4suite成功、F/E/S/aborted/container failure0。新ID3件と必要既存12件を区別、旧PAGE3は新規へ再加算0。production Main/上位設計/既oracle変更0。

| 証拠（各evidence/provisional下manifest.json） | SHA-256 |
|---|---|
| ../018_NK-OPS-001/.../PG9686-semantic-direct-six-compile-v1 | 890012b6561777b4f8d19e1f4118f4fe11d26cf2eeedd005f24f60c33f2356cc |
| PG9688-semantic-boundaries-host-v1 | d2253a3e1f05c0cbe788df0d62054557ddd8d0ca72ebfeca35afd2e7dd1ab898 |
| PG9690-semantic-boundaries-post-v1 | 18c5455142999da2bd264d4b83b16208ffdbc0d1c9ed867408acfc717ee8f7d5 |
| PG9692-semantic-direct-static-v1（実終了1） | 292e8572d78309be883cb732e55104e15dbf0319521eff7b252f0411223888c5 |

当source/単一sessionの全PayloadSemanticValidatorはline315/315、method38/38、class1/1、branch197/197、全四missed0。9690は元XML15/4、helper宣言数/ケース名、全source/依存/実exec hash、当session/物理class CRC64を独立照合し、315行と38methodの明細も保存。旧exec union/到達不能偽装/除外0。これは単一classの実測であり、全Program/全source/正式/CHR/native/全oracleの受入ではない。normal64-layout一件のroundtripは唯一のoracleにせず、既P06と新SEM固定条件の独立期待値を011/1967へ結ぶ。

正常compileは6jar/NullAway・lint/format/実PT0、JDK25.0.4/Maven3.9.12。新Test PMD7.28.0はAvoidDuplicateLiterals priority3一件（LGSREQ01七回）、Checkstyle14.3.0は0、解析error0。Main同byteのold static入力根拠だけを参照するが、現Test静的gateは実1で未成立。BUG1756/YKT1507を修正前起票し、原source SHA9be12624/全report/真exitを保持。次はliteralを同値定数へ集約し、修正後source固定/必要compile/PT/static/独立postを実施する。旧000270の100%や実15件を新sourceへそのまま転用しない。

元normal68865/JUnit47807/post52380/static82160はいずれも真正終端確認、staticだけ実1を保持。並列したcompileと新Test静的は別slotで、source不変更、外部job/VM/DB/Root/native等の操作0。実command/environment/開始終了/JDK/OS/source/dependency/hashは各manifest/stageへ保存。現source Main965/Test826/Java1791相当は次source-input postで確定予定、registryの1782/1790は3154の歴史観測として保持。正式1964-53/17-190/工数null/QA051final/全actualHOLDは未更新。
