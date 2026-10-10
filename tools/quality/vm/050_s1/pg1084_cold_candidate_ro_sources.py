"""SSC249 finite candidate hostRO/full verifier only; current and empty epoch stay old."""
import ast
from pg1079_cold_candidate_sources_v3 import files as previous
from pg1069_cold_candidate_sources import replace_once
from pg835_pending_v5 import METHOD,ORACLE


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1079ColdCandidateStage','Pg1084ColdCandidateRo'),
                        ('pg1079_cold_refs.py','pg1084_cold_refs.py'),
                        ('pg1079-cold-tools-v1','pg1084-cold-tools-v1'),
                        ('pg1079-cold-candidate-v1','pg1084-cold-candidate-ro-v1'),
                        ('PG1079_','PG1084_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.java')and not name.endswith('Test.java'):
            text=replace_once(text,'"place".equals(args[0])','"prepare-ro".equals(args[0])')
            marker='              phase="SIGNED_UNUSED_CANDIDATE_PLACEMENT";'
            text=replace_once(text,marker,r'''
              phase="CANDIDATE_HOST_NAMESPACE";
              require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))));
              Pg387TrustedDeployment.LABEL="PG1068";Pg387TrustedDeployment.STEM="pg1068";
              Pg387TrustedDeployment.SOURCE="d5b00104280028d9ea81b44c1d1c805f3c2861ed";
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1068");
              phase="NECESSARY_CANDIDATE_HOST_RO";
              String target=Pg387TrustedDeployment.RELEASE.toString();
              String mounts=Files.readString(Path.of("/proc/self/mountinfo"));
              if(!readOnlyMount(mounts,target)) {
                for(String line:mounts.split("\n")) {
                  String[] fields=line.split(" ");require(fields.length>=6&&!fields[4].equals(target)&&!fields[4].startsWith(target+"/"));
                }
                Pg387TrustedDeployment.freezeCandidate();
              }
              require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),target));
              phase="FULL_IMMUTABLE_CANDIDATE";
              var candidate=Pg387TrustedDeployment.verify();
              require(candidate.version().equals("0.1.0-PG1068")&&candidate.manifestSha256().equals("0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d"));
              Pg387TrustedDeployment.LABEL="PG932";Pg387TrustedDeployment.STEM="pg932";
              Pg387TrustedDeployment.SOURCE="40ef6e894573d2ffab1d1732124960f9c98d5f97";
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG932");
''')
            method=METHOD.replace('PG832','PG1068').replace('\\\\n','\\n')
            text=replace_once(text,'  public static void main(String[] args)throws Exception {',method+'\n  public static void main(String[] args)throws Exception {')
            text=text.replace('unusedCandidatePlacement=true','candidateImmutableVerified=true')
        elif name.endswith('Test.java'):
            text=text.replace('"place"','"prepare-ro"')
            oracle=ORACLE.replace('PG832','PG1068').replace('Pg835PendingDeployment','Pg1084ColdCandidateRo').replace('\\\\n','\\n')
            text=replace_once(text,'    System.out.println(',oracle+'\n    System.out.println(')
        else:
            text=replace_once(text,"b'Pg1084ColdCandidateRo',b'place',b''","b'Pg1084ColdCandidateRo',b'prepare-ro',b''")
            # Drop the unused archive action entirely; no re-placement is allowed.
            begin=text.index("phase='SIGNED_UNUSED_STAGE';require(sys.stdin.readline()=='prepared\\n')")
            end=text.index(' authenticate()',begin)+len(' authenticate()')
            ro=CANDIDATE_AUTH[CANDIDATE_AUTH.index(' candidate_options='):]
            text=text[:begin]+"phase='CANDIDATE_RO_POST';require(sys.stdin.readline()=='prepared\\n')\n"+ro+text[end:]
            marker="phase='BYTE_AUTH';captured_parent=parent();controls()"
            auth=CANDIDATE_AUTH[:CANDIDATE_AUTH.index(' candidate_options=')]
            text=replace_once(text,marker,marker+";authenticate()\n"+auth)
            ast.parse(text)
        result[name]=text
    return result


CANDIDATE_AUTH=r'''
 candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068')
 candidate_manifest=(candidate_root/'RELEASE-MANIFEST.json').read_bytes()
 require(hashlib.sha256(candidate_manifest).hexdigest()=='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
 candidate=json.loads(candidate_manifest);require(candidate['source']['commit']=='d5b00104280028d9ea81b44c1d1c805f3c2861ed')
 candidate_records=candidate['artifacts'];candidate_sums=contract.canonical_sum_bytes(candidate_records,hashlib.sha256(candidate_manifest).hexdigest())
 held.append(contract.HeldInventory(str(candidate_root),candidate_records+[
  {'path':'RELEASE-MANIFEST.json','size':len(candidate_manifest),'sha256':hashlib.sha256(candidate_manifest).hexdigest()},
  {'path':'SHA256SUMS','size':len(candidate_sums),'sha256':hashlib.sha256(candidate_sums).hexdigest()}],0).open())
 hold_material(pathlib.Path('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig'),64,'5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b')
 require((candidate_root/'SHA256SUMS').read_bytes()==candidate_sums)
 candidate_options=command(['findmnt','--target',str(candidate_root),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
 require('ro'in candidate_options and 'rw'not in candidate_options)
'''
