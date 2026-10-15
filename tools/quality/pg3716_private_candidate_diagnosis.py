"""Read-only instrumentation of the original refused protocol candidate; never writes Java input."""
import inspect
import json
from pathlib import Path
from lan_server import run, copy


def server(detail=False):
    import hashlib
    import json
    from pathlib import Path
    import subprocess
    b=Path('/home/mini/schubert-nk-pgpt');old=b/'runs/PG3714-private-field-candidate-v1';out=b/('runs/PG3718-private-binding-diagnosis-v1' if detail else 'runs/PG3716-private-candidate-diagnosis-v1');out.mkdir();(out/'classes').mkdir()
    payload=b/'transfer/PG3714-private-field-candidate-v1';source=(payload/'SourcePrivateFieldRename.java').read_text()
    replacements={
      'IsolatedSourceOutput.candidate(input, Path.of(args[4]), propose)':'IsolatedSourceOutput.candidate(input, Path.of(args[4]), false)',
      'if (propose) {\n      Files.createDirectories(output.getParent());':'if (false) {\n      Files.createDirectories(output.getParent());',
      'if (propose) {\n      var mapping = new StringBuilder();':'if (false) {\n      var mapping = new StringBuilder();',
      'require(actualNewFields.equals(normalized.keySet()) && beforeHashes.equals(actualHashes));':'''System.out.println("FIELDS_EQUAL\\t" + actualNewFields.equals(normalized.keySet()));
    for (var entry : beforeHashes.entrySet()) if (!entry.getValue().equals(actualHashes.get(entry.getKey()))) System.out.println("DIFFERENT\\t" + entry.getKey() + "\\t" + entry.getValue() + "\\t" + actualHashes.get(entry.getKey()));
    require(actualNewFields.equals(normalized.keySet()) && beforeHashes.equals(actualHashes));'''
    }
    for a,z in replacements.items():
        assert source.count(a)==1
        source=source.replace(a,z)
    # Instrument digest components as hashes, not literal source or runtime data.
    source=source.replace('void add(Object value) { result.append(value).append(\'\\u0000\'); }', '''void add(Object value) {
        result.append(value).append('\\u0000');
        try { trace.add(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(String.valueOf(value).getBytes(StandardCharsets.UTF_8)))); } catch (Exception e) { throw new IllegalStateException(e); }
      }''')
    source=source.replace('var result = new StringBuilder();','var result = new StringBuilder(); var trace = new ArrayList<String>();')
    source=source.replace('return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(result.toString().getBytes(StandardCharsets.UTF_8)));', '''String file = Path.of(unit.getSourceFile().toUri()).getFileName().toString();
    Files.write(Path.of(System.getProperty("diagnosticRoot")).resolve((normalized.isEmpty() ? "before-" : "after-") + file + ".safe.hashes"), trace);
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(result.toString().getBytes(StandardCharsets.UTF_8)));''')
    if detail:
        source=source.replace('trace.add(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(String.valueOf(value).getBytes(StandardCharsets.UTF_8))))', 'trace.add(String.valueOf(value).replace("\\n", "<LF>").replace("\\r", "<CR>"))')
    (out/'SourcePrivateFieldRename.java').write_text(source)
    j=b/'tools/jdk-25.0.4/bin';r=subprocess.run([str(j/'javac'),'-d',str(out/'classes'),str(out/'SourcePrivateFieldRename.java'),str(payload/'IsolatedSourceOutput.java')],capture_output=True,timeout=30);assert r.returncode==0,r.stderr.decode()
    prior=json.loads((b/'runs/PG3690-import-candidate-v1/manifest.safe.json').read_bytes());cp=prior['modules']['protocol']['phases']['after']['command'][-1];root=b/'runs/PG3692-hygiene-candidate-v1/candidate/src/schubert-nk-protocol/src/main/java';candidate=old/'candidate/src/schubert-nk-protocol/src/main/java';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for r in [root,candidate]for p in r.rglob('*.java')}
    r=subprocess.run([str(j/'java'),'-DdiagnosticRoot='+str(out),'-cp',str(out/'classes'),'SourcePrivateFieldRename','propose',str(root),cp,str(old/'protocol-requests.safe.tsv'),str(candidate)],capture_output=True,text=True,timeout=180)
    assert before=={str(p):sha(p)for r in [root,candidate]for p in r.rglob('*.java')}
    (out/'diagnostic.safe.log').write_text(r.stdout+r.stderr)
    result={'diagnosticOriginalExit':r.returncode,'inputAndCandidateUnchanged':True,'results':r.stdout.splitlines(),'stderrTail':r.stderr.splitlines()[-3:]}
    if detail:
        a=(out/'before-TypedFieldValues.java.safe.hashes').read_text().splitlines();z=(out/'after-TypedFieldValues.java.safe.hashes').read_text().splitlines()
        result['sourceBindingDifferences']=[{'tokenIndex':i,'before':x,'after':y}for i,(x,y)in enumerate(zip(a,z))if x!=y]
    print(json.dumps(result))


if __name__=='__main__':
    import os,sys
    os.umask(0o077)
    detail=sys.argv[1:]==['--detail'];name='PG3718-private-binding-diagnosis-v1' if detail else 'PG3716-private-candidate-diagnosis-v1'
    out=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')/name.lower();out.mkdir()
    p=out/'diagnose.private.py';p.write_text(inspect.getsource(server)+'\nserver('+repr(detail)+')\n')
    dest='/home/mini/schubert-nk-pgpt/transfer/'+name
    rc,_=run('mkdir -m700 '+dest,timeout=30);assert rc==0
    rc,_=copy(p,dest+'/');assert rc==0
    rc,text=run('python3 -B '+dest+'/diagnose.private.py',timeout=240)
    (out/'observer.private.log').write_text(text);print(rc,text)
