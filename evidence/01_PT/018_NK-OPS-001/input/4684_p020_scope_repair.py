"""PG-D-1171: preserve originals, then explicit operation-owned nonnull IO."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';base=r/'program/characterization/src/main/java/dev/codex/schubert/characterization';out=b/'evidence/PG37296-p020-source-before-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((b/'evidence/PG37016-p020-whole124-independent-v1/manifest.json').read_text())
pins={p:h for p,h in prior['sourceTestPins'].items() if '/src/main/java/' in p or '/tests/java/' in p}
assert len([p for p in pins if '/src/main/' in p])==5
assert all(sha(r/p)==h for p,h in pins.items()), 'Original source changed; inspect before retry'
assert all(sha(out/(Path(p).name+'.before'))==h for p,h in pins.items() if '/src/main/' in p)
manifest=out/'manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps(dict(actualExit=0,observedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceBefore='976a6e61c59ba8ddca45860a872640fe5d825cb9',sourceTestPins=pins,originalWholeSuites=17,all39TestAndHelperSourcesPreserved=True,originalSourceCount=5,originalBaselineNotTouched=True,earlierPartialBackupReason='Preparation asserted 17 Test source files, but original pins include 39 Test/helper files. Assertion occurred before manifest/decision/ledger/source mutation. Five backups already existed; verified rather than overwritten.'),indent=2)+'\n')
decision=r/'documents/400_PGPT/440_判断/441_実装判断記録.md'
assert '### PG-D-1171 ' not in decision.read_text()
with decision.open('a') as f:f.write('\n### PG-D-1171 P020 operation-owned nonnull IO（2026-11-17）\n\nSS355/BUG3146/YKT2615。全5工具と必要な内部共有処理をraw対象に保持し、外部CLI・JSON・DIF・baselineを変えず、非null取得契約と一回closeを明示する。IO callbackは取得前に検証し、一次例外を維持して異なる二次例外だけ抑制、同一例外は自己抑制しない。private static utility ctorは非生成invariantを確立する。TargetAdapterの正規private引数ctorは変更しない。Json出力のper-call portで既存finally優先順位・claim解放を独立検証する。実Current/NK起動・原baseline・権限・DB等のHOLD範囲へ進まない。元5sourceと39 Test/helper pinsはPG37296に保存。未試験段階でありPASS扱いしない。\n')
for number,name in [('BUG3146','915_障害表.md'),('YKT2615','916_横展開管理台帳.md')]:
 with (r/'documents/900_OTHER/910_台帳'/name).open('a') as f:f.write('\n#### '+number+' 2026-11-17 是正前保全追記\n\nPG37296で元5工具と全39 Test/helper hashを保全。PG-D-1171に基づき、非null IO所有と独立異常系port、hash衝突negative、static utility invariantを是正予定。未実装/未実行の時点ではOPEN維持。適用範囲はprogram/characterizationのみ。\n')
def replace(name,old,new):
 p=base/name;s=p.read_text();assert s.count(old)==1,(name,old[:90]);p.write_text(s.replace(old,new))
for name in ['ArtifactComparator','CorrelatedLogEvidenceValidator','GateCli','GateContractValidator']:
 replace(name+'.java','private '+name+'() {}','private '+name+'() { throw new AssertionError("'+name+' is a static tool"); }')
# Replace complete list/walk try blocks while keeping each lambda's result semantics.
replace('ArtifactComparator.java','try (Stream<Path> paths = Files.list(root)) {','return CharacterizationIoScope.acquire(() -> Files.list(root), Stream::close, paths -> {')
replace('ArtifactComparator.java','    }\n    return files;\n  }\n\n  private static void compareSets','      return files;\n    });\n  }\n\n  private static void compareSets')
for name in ['GateCli.java','GateContractValidator.java']:
 replace(name,'try (Stream<Path> files = Files.list(artifactRoot)) {','return CharacterizationIoScope.acquire(() -> Files.list(artifactRoot), Stream::close, files -> {')
 marker='          .toList();\n    }\n  }\n\n  private static int caseOrder'
 replace(name,marker,'          .toList();\n    });\n  }\n\n  private static int caseOrder')
 replace(name,'try (Stream<Path> paths = Files.walk(root)) {\n      return','return CharacterizationIoScope.acquire(() -> Files.walk(root), Stream::close, paths -> {\n      return')
 # Locate regularFiles method end without altering any adjacent filter semantics.
 p=base/name;s=p.read_text();start=s.index(' static List<Path> regularFiles') if name=='GateCli.java' else s.index(' private static List<Path> regularFiles');end=s.index('\n  private static',start+1) if name!='GateCli.java' else s.index('\n  static TreeStats',start)
 body=s[start:end];assert body.endswith('    }\n  }\n');s=s[:start]+body[:-len('    }\n  }\n')]+'    });\n  }\n'+s[end:];p.write_text(s)
 replace(name,'    try (var input = Files.newInputStream(file)) {','    CharacterizationIoScope.acquire(() -> Files.newInputStream(file), java.io.InputStream::close, input -> {')
 replace(name,'        digest.update(buffer, 0, read);\n      }\n    }','        digest.update(buffer, 0, read);\n      }\n      return Boolean.TRUE;\n    });')
replace('GateCli.java','    try (Stream<Path> paths = Files.walk(source)) {','    CharacterizationIoScope.acquire(() -> Files.walk(source), Stream::close, paths -> {')
replace('GateCli.java','        else Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);\n      }\n    }','        else Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);\n      }\n      return Boolean.TRUE;\n    });')
replace('GateCli.java','      try (Stream<Path> contents = Files.list(baseline)) {','      CharacterizationIoScope.acquire(() -> Files.list(baseline), Stream::close, contents -> {')
replace('GateCli.java','          throw new IllegalStateException("baseline already exists and is not empty");\n        }\n      }','          throw new IllegalStateException("baseline already exists and is not empty");\n        }\n        return Boolean.TRUE;\n      });')
replace('GateCli.java','    long files = 0;\n    long bytes = 0;\n    List<String> symlinks = new ArrayList<>();\n    try (Stream<Path> paths = Files.walk(root)) {','    return CharacterizationIoScope.acquire(() -> Files.walk(root), Stream::close, paths -> {\n      long files = 0;\n      long bytes = 0;\n      List<String> symlinks = new ArrayList<>();')
replace('GateCli.java','    }\n    return new TreeStats(files, bytes, List.copyOf(symlinks));','      return new TreeStats(files, bytes, List.copyOf(symlinks));\n    });')
p=base/'GateCli.java';s=p.read_text();start=s.index('    // This method owns the stream.');end=s.index('\n  private static int[] prefixes',start)
s=s[:start]+'''    // Own only the raw stream; KMP state survives each 8 KiB buffer boundary.
    return CharacterizationIoScope.acquire(() -> Files.newInputStream(file), InputStream::close, input -> {
      byte[] buffer = new byte[8192];
      for (int read = input.read(buffer); read != -1; read = input.read(buffer)) {
        for (int index = 0; index < read; index++) {
          byte next = buffer[index];
          for (int pattern = 0; pattern < targets.size(); pattern++) {
            byte[] target = targets.get(pattern);
            int position = matched[pattern];
            while (position > 0 && target[position] != next) {
              position = prefixes.get(pattern)[position - 1];
            }
            if (target[position] == next) position++;
            if (position == target.length) return true;
            matched[pattern] = position;
          }
        }
      }
      return false;
    });
  }
''' + s[end:];s=s.replace('import java.io.BufferedInputStream;\n','');p.write_text(s)
print(json.dumps(dict(actualExit=0,sourceBeforePins=len(pins),newSourcePendingTests=True,baselineChanged=False)))
