"""Existing SS343 unused candidate hostRO/full verifier, current partial unchanged."""
from pg1478_partial_original_profile_sources import java as old_java
from pg1512_original_component_profile_sources import refs as old_refs
from pg1517_original_profile_retry import remap

CLASS='Pg1546PendingCandidateHostRo'
TOOLS='pg1546-pending-candidate-ro-tools-v1'
SAVE='pg1549-pending-candidate-host-ro-v1'
BOM='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'

def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('fixed candidate RO source boundary refused')
    return raw.replace(old,new)

def java():
    s=old_java().replace('Pg1478PartialOriginalProfile',CLASS).replace('pg1478-partial-original-tools-v1',TOOLS).replace('pg1481-partial-original-profile-v1',SAVE).replace('pg1478_partial_original_refs.py','pg1546_pending_candidate_ro_refs.py').replace('PG1481_','PG1549_').replace('PG266-readonly-profile','PG269-candidate-ro')
    s=once(s,'"profile".equals(args[0])','"prepare-ro".equals(args[0])')
    marker='              refs.check("prepared");original(session);'
    s=once(s,marker,RO_JAVA+'\n'+marker)
    s=s.replace('readonlyProfile=true','candidateHostRo=true').replace('readonlyProfile','candidateHostRo')
    s=s.replace('  public static void main(String[] args)throws Exception {',RO_OPTIONS+'\n  public static void main(String[] args)throws Exception {')
    return s

RO_OPTIONS=r'''
  static boolean readonlyOptions(String text) {
    if(text==null||text.isEmpty()||!text.equals(text.strip()))return false;
    var parts=text.split(",",-1);var seen=new HashSet<String>();
    for(String part:parts)if(part.isEmpty()||!part.matches("[a-z0-9_=.-]+")||!seen.add(part))return false;
    return seen.contains("ro")&&!seen.contains("rw");
  }
'''
RO_JAVA=r'''
              phase="CANDIDATE_ONLY_HOST_RO";
              Pg387TrustedDeployment.LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544";
              Pg387TrustedDeployment.SOURCE="4d6bcbddb417b76d27e52d5d9640752c300edccf";
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1544");
              var mounted=new ProcessBuilder("/usr/bin/findmnt","-n","-o","OPTIONS","--mountpoint",Pg387TrustedDeployment.RELEASE.toString()).start();
              byte[] options=mounted.getInputStream().readAllBytes();require(options.length<=4096);
              int mountStatus=mounted.waitFor();
              mounted.getInputStream().close();mounted.getOutputStream().close();mounted.getErrorStream().close();
              if(mountStatus==1)Pg387TrustedDeployment.freezeCandidate();
              else require(mountStatus==0&&readonlyOptions(new String(options,StandardCharsets.US_ASCII).strip()));
              phase="CANDIDATE_ONLY_FULL_VERIFIER";
              var candidate=Pg387TrustedDeployment.verify();
              require(candidate.version().equals("0.1.0-PG1544")&&candidate.manifestSha256().equals("e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c"));
              Pg387TrustedDeployment.LABEL="PG1292";Pg387TrustedDeployment.STEM="pg1292";
              Pg387TrustedDeployment.SOURCE="769ddb15cd735c25fef581b5f9850ef9d0053c0f";
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1292");
'''

def refs():
    s=remap(old_refs()).replace('Pg1517OriginalComponentProfile',CLASS).replace('pg1517-original-component-tools-v2',TOOLS).replace('pg1519-original-component-profile-v2',SAVE).replace('PG269-original-io-profile','PG269-candidate-ro').replace("b'profile'","b'prepare-ro'")
    marker=' before_inventory=[h.capture()for h in held];fixed_parent=actor()'
    s=once(s,marker,CANDIDATE_HELD+'\n'+marker)
    marker="  if action=='release':\n   require(PEER_CLOSED)"
    s=once(s,marker,POST_RO+'\n'+marker)
    s=s.replace("'mutation0':True","'candidateOnlyHostRo':True,'currentApprovalEpochDbUnitsPreserved':True")
    compile(s,'<fixed partial original candidate RO observer>','exec')
    return s

CANDIDATE_HELD=r'''
 candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544');candidate_bom='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'
 candidate_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(candidate_raw).hexdigest()==candidate_bom)
 candidate_data=json.loads(candidate_raw);require(candidate_data['source']['commit']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'and len(candidate_data['artifacts'])==187 and candidate_data['versions']['schema']=='028')
 candidate_sums=contract.canonical_sum_bytes(candidate_data['artifacts'],candidate_bom)
 candidate_rows=candidate_data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(candidate_raw),'sha256':candidate_bom},{'path':'SHA256SUMS','size':len(candidate_sums),'sha256':hashlib.sha256(candidate_sums).hexdigest()}]
 held.append(contract.HeldInventory(str(candidate),candidate_rows,0).open())
 held.append(contract.HeldInventory(str(BASE),[{'path':'pg1544-manifest.sig','size':64,'sha256':'fed7f4c24a2356f095aed4310c5a826f9896452cc731971fbd3589f94ae6d232'}],0).open_file())
'''
POST_RO=r'''
  if action in {'prepared','run','release'}:
   mounted=command(['findmnt','-n','-o','OPTIONS','--mountpoint',str(candidate)],4096).decode('ascii').strip()
   flags=mounted.split(',');require(len(flags)==len(set(flags))and 'ro'in flags and 'rw'not in flags)
'''

def argument_test():
    return r'''public final class Pg1546ReadonlyArgumentTest {
 public static void main(String[]args){
  if(!Pg1546PendingCandidateHostRo.readonlyOptions("ro,relatime")||!Pg1546PendingCandidateHostRo.readonlyOptions("relatime,ro"))throw new AssertionError();
  for(String s:new String[]{null,"","rw,relatime","ro,rw","ro,ro","ro,","ro,foreign value"," ro","ro\n"})if(Pg1546PendingCandidateHostRo.readonlyOptions(s))throw new AssertionError();
  for(String[] a:new String[][]{null,new String[0],new String[]{"profile"},new String[]{"prepare-ro","extra"}}){
   try{Pg1546PendingCandidateHostRo.arguments(a);throw new AssertionError();}catch(IllegalStateException expected){}
  }
  Pg1546PendingCandidateHostRo.arguments(new String[]{"prepare-ro"});
 }
}'''
