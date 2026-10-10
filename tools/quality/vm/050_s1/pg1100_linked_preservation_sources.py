"""New SSC251 family: preserve linked old part only, no repeated publication."""
import ast
from pg1094_cold_activation_sources_v2 import files as previous
from pg1091_cold_activation_sources import PUBLISH
from pg1100_linked_preservation_refs import source as refs_source
from pg1069_cold_candidate_sources import replace_once


PRESERVE=r'''
  static void publication(dev.codex.schubert.nk.bootstrap.ReleaseApproval candidate,References refs,MaintenanceRunFiles.Session session)throws Exception {
    require(candidate.version().equals("0.1.0-PG1068")&&candidate.manifestSha256().equals("0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d"));
    require(Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG1068")));
    require(Arrays.equals(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")),candidate.encode()));
    byte[] epoch=Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"));
    require(Arrays.equals(epoch,Files.readAllBytes(Path.of("/var/lib/pgpt-s1-preservation/pg1094-cold-activate-v1/new-epoch.private"))));
    phase="FIXED_LINKED_ORIGINAL_PRESERVATION";refs.check("preserve");original(session);
    require(!Files.exists(Path.of("/opt/schubert-nk/pg1088-current.part"),LinkOption.NOFOLLOW_LINKS));
    require(Files.readSymbolicLink(SAVE.resolve("current-link.private")).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG932")));
    require(Arrays.equals(epoch,Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"))));
    var verified=dev.codex.schubert.nk.bootstrap.StartupReleaseManifest.createHost(
        new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().configurationGroup()).verify(candidate);
    require(verified.version().equals("0.1.0-PG1068"));
  }
'''


def files():
    result={}
    for name,text in previous().items():
        if name.endswith('.py'):continue
        if not name.endswith('Test.java'):
            old=PUBLISH.replace('pg1091-approval.part','pg1094-approval.part')
            text=replace_once(text,old,PRESERVE)
            text=replace_once(text,'Set.of("prepare","prepared","epoch","approval","exchange","run")','Set.of("prepare","preserve","run")')
            text=replace_once(text,'Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));',
                             'Files.readAllBytes(Path.of("/var/lib/pgpt-s1-preservation/pg1094-cold-activate-v1/old-approval.private"))));')
            text=replace_once(text,'phase="FINITE_COLD_PUBLICATION"','phase="LINKED_ORIGINAL_ONLY"')
            text=text.replace('finiteColdActivation=true','linkedOriginalPreserved=true')
        for old,new in [('Pg1094ColdActivation','Pg1100LinkedPreservation'),('pg1094_cold_refs.py','pg1100_linked_refs.py'),
            ('pg1094-cold-tools-v1','pg1100-linked-tools-v1'),('pg1094-cold-activate-v1','pg1100-linked-preservation-v1'),
            ('PG1094_','PG1100_'),('"activate"','"preserve"')]:
            name=name.replace(old,new)
            # Original failed private evidence keeps its fixed old path.
            if old=='pg1094-cold-activate-v1':
                text=replace_once(text,'static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/'+old+'")','static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/'+new+'")') if 'static final Path SAVE=Path.of' in text else text
            else:text=text.replace(old,new)
        result[name]=text
    result['pg1100_linked_refs.py']=refs_source();ast.parse(result['pg1100_linked_refs.py']);return result
