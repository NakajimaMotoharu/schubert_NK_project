# WBS65 Protocol旧受入三契約・PT記述整合結果

2026-11-12。PG26068。Production Main7aed8eace7c844c2f79f2e39db766faf914890d5、照合HEAD689e2af901c1c6cc970939f8110a6d2f178a966d。原群.6/1.5/3pp・上限4を保持。

| 対象 | 現byte/独立根拠 | Test ID/具体条件 | 判定・残条件 |
|---|---|---|---|
| P00101 | MQ014～018、UI232、SS322、Header六Source/30method参照、原normal120内HeaderModel | H01許容enum/result literal、H02長さ上限、H03/HDR3266-001九参照nullのfield名即時拒否 | Main六file・Test同byte。旧受入の再認証資料であり新規受入0。全分岐oracle個別・終端451は未閉鎖 |
| P00102 | UI233～236の独立TSV、SS323、20Source/84method参照 | L01 64layout、L02不正構造、L03 immutable/unknown。Field/Metadata元Test | 現byte一致、構造不正と内部nonnull前提を区別。各branch独立期待値・終了依存は未閉鎖 |
| P00203 | UI232/SS322、五Source/14method参照、原MessageCodec固定golden | header byte offset/length、route/transport/encode例外。主Program002既仕様を正とする | 現byte一致。自然B0の二Sourceをbranch100へ作り替えない。個別oracle/終了条件は未閉鎖 |

元正常120は再実行せず、現在の31Main、五Testと二独立TSVの全byteを元preflight hashへ照合した。集計miss0は元runの参照値であり新測定、全owner受入、per-case probe attributionを意味しない。coverage合成/旧source成果の加算なし。

BUG2629/YKT2310: 既104で明記済みの内部Java requireNonNull契約と外部不正wireのtyped validationを区別し、一次spec二file三記述だけを同期した。元before20仕様書・八一致行を保全し、他18仕様書はHEADと同byte。Production/Test/期待例外/上位仕様は変更しない。偶発NPEやNPEを正常業務結果へ変換する実装は禁止を維持。外部境界の欠落/null防止を緩和しない。

BUG2630/YKT2311: 新照合工具のsuffix条件が補足語付き七specを漏らしたcount guard1と、根拠labelの誤字guard1をPG26072へ保全。元beforeと同じ001_*.md全20へ修正し、実根拠の旧仕様H03字句に同期した。最終PG26068 actualExit0。製品試験を起動した失敗ではない。

証拠はevidence/PG26068-protocol-three-contracts-v1/manifest.json（9b8d942d98ad9e9cc85dcbeff89fc3db7db8cb6f467ffaae7904ea36d7b7bd49）。仕様書の変更前hash/変更後hash/三差分と31Main/七入力pin、三参照manifestを含む。製品試験実行0・新coverage0・新190受入0、正式1964PT/53scopeと工数nullを維持。次はC02全14設定の個別判定→初回20pp見直し→許可済み独立作業。
