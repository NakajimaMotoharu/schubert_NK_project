"""Current genuine-DONE candidate hostRO/full verifier; no placement/publication."""
import ast
from pg1293_completed_unused_stage_sources import sources as previous,once,SOURCE,DIGEST
from pg835_pending_v5 import METHOD,ORACLE


RO_METHOD=r'''
  static void candidateReadOnly()throws Exception {
    require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))));
    Pg387TrustedDeployment.LABEL="PG1292";Pg387TrustedDeployment.STEM="pg1292";
    Pg387TrustedDeployment.SOURCE="769ddb15cd735c25fef581b5f9850ef9d0053c0f";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1292");
    phase="NECESSARY_CANDIDATE_HOST_RO";String target=Pg387TrustedDeployment.RELEASE.toString();
    String mounts=Files.readString(Path.of("/proc/self/mountinfo"));
    if(!readOnlyMount(mounts,target)) {
      for(String line:mounts.split("\n")) {
        String[] fields=line.split(" ");require(fields.length>=6&&!fields[4].equals(target)&&!fields[4].startsWith(target+"/"));
      }
      Pg387TrustedDeployment.freezeCandidate();
    }
    require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),target));
    phase="FULL_IMMUTABLE_CANDIDATE";var candidate=Pg387TrustedDeployment.verify();
    require(candidate.version().equals("0.1.0-PG1292")&&candidate.manifestSha256().equals("ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99"));
    Pg387TrustedDeployment.LABEL="PG1068";Pg387TrustedDeployment.STEM="pg1068";
    Pg387TrustedDeployment.SOURCE="d5b00104280028d9ea81b44c1d1c805f3c2861ed";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1068");
  }
'''


def sources():
    result={}
    for name,text in previous().items():
        name=name.replace('Pg1293','Pg1300').replace('pg1293','pg1300').replace('UnusedStage','CandidateRo')
        text=text.replace('Pg1293','Pg1300').replace('pg1293','pg1300').replace('PG1293','PG1300').replace('UnusedStage','CandidateRo')
        if name=='Pg1300CandidateRo.java':
            text=once(text,'"place".equals(args[0])','"prepare-ro".equals(args[0])')
            text=once(text,'"place",Integer.toString(pid)','"prepare-ro",Integer.toString(pid)')
            text=once(text,'"place".equals(name)','"ro".equals(name)')
            text=once(text,'phase="SIGNED_UNUSED_PLACEMENT";refs.check("place");','phase="CANDIDATE_RO";candidateReadOnly();refs.check("ro");')
            method=METHOD.replace('PG832','PG1292').replace('\\\\n','\\n')
            text=once(text,'  public static void main',method+'\n'+RO_METHOD+'\n  public static void main')
            text=text.replace('unusedCandidatePlaced=true','candidateReadOnlyVerified=true')
        elif name=='Pg1300StopLabelTest.java':
            oracle=ORACLE.replace('PG832','PG1292').replace('Pg835PendingDeployment','Pg1300CandidateRo').replace('\\\\n','\\n')
            text=once(text,'    System.out.println(',oracle+'\n    System.out.println(')
        elif name=='pg1300_native_owned_stop.py':
            text=text.replace("b'place'","b'prepare-ro'").replace("'place'","'ro'")
        elif name=='pg1300_native_refs.py':
            text=once(text,"sys.argv[1]=='place'","sys.argv[1]=='prepare-ro'")
            tree=ast.parse(text);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
            main.body=[n for n in main.body if not(isinstance(n,ast.FunctionDef)and n.name=='place_candidate')]
            text=ast.unparse(tree)+'\n'
            text=once(text,"held = owner()",CANDIDATE_BEFORE+"\n    held = owner()")
            text=text.replace("if action == 'place':","if action == 'ro':")
            text=once(text,'            place_candidate()',"            candidate_ro_post(candidate_before)")
            text=text.replace('placed = False','placed = False')
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result


CANDIDATE_BEFORE=r'''
    candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
    def candidate_bytes():
        manifest=(candidate_root/'RELEASE-MANIFEST.json').read_bytes()
        require(hashlib.sha256(manifest).hexdigest()=='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99')
        value=json.loads(manifest);require(value['source']['commit']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'and len(value['artifacts'])==187)
        for row in value['artifacts']:
            p=candidate_root/row['path'];require(p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
        return tree(candidate_root)
    def candidate_ro_post(before):
        require(candidate_bytes()==before)
        opts=command(['findmnt','--target',str(candidate_root),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
        require('ro'in opts and'rw'not in opts)
        require(candidate_bytes()==before)
    candidate_before=candidate_bytes();require(candidate_before==candidate_bytes())
'''
