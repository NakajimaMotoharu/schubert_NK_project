"""Pure rebind of qualified stop ABI to actual current fullseal/four generation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
from pg1334_published_owned_stop_sources_v2 import sources as previous

SOURCE='4d6bcbddb417b76d27e52d5d9640752c300edccf'
BEFORE='52faff7f880f73f6020ac40d7aa1d8fe170e0e3ed6dfd7f10fd7fbddd8c4f9a9'
GUEST_BEFORE='/var/lib/pgpt-s1-preservation/pg1578-current-completed-seal-v1/before.private.json'
TOOLS='pg1579-current-owned-stop-tools-v1'
OWNED={'caddy.service':('161708','b62723b53ece4420b783a627e3548012'),'schubert-nk-web.service':('159826','fb683eeb6d3b4e90b66c1576f9108a0c'),'schubert-nk-api.service':('158794','2111873a431743359c0627a8f5e394c8'),'artemis.service':('118964','6e745372ba4e4c7683cda767c607b93c')}
CHANGES=[('Pg1334','Pg1579'),('PG1334','PG1579'),('pg1334-native-tools-v1',TOOLS),('pg1334','pg1579'),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99','e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'),('0.1.0-PG1292','0.1.0-PG1544'),('pg1292','pg1544'),('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),('cbca87383b244090b77cbf029677cdd6','3d69f5af6bac46b1a5407591c4a79a0d'),('8e5e15d65b69a5ca28cee870eed0c71969e36545d34b237a19cfd5a845f8db91',BEFORE),('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/published-completed-capture-v2/before.private.json',GUEST_BEFORE),('400b2e34105149ff8f3a11c21da0be6a','c52c914a72804a89b0fd5f252f6ac0fc'),("'120359'","'50856'"),('73654946447','32043431270'),('75132489604','33583425972'),('75454946447','33843431270'),('d2e3a86f-27a4-4c2a-be21-b512eebf1216','15700a87-9117-4f63-a0ff-768dd604d0f1'),('2026-10-10T23:30:23.481632Z','2026-10-11T21:18:59.040097Z'),('2026-10-10T23:30:23.481632+00:00','2026-10-11T21:18:59.040097+00:00'),('841b507c-2713-4ffe-8882-68f5fb3f87f5','9e706936-a3c9-4a09-bb66-e2b1e8bbef66'),('2026-10-10T23:54:39.918039Z','2026-10-12T05:02:52.617413Z'),('811700','161708'),('ab9156db01204f128fba490163785bef','b62723b53ece4420b783a627e3548012'),('809511','159826'),('588c880aed434af6a6bb89c7ad3bf076','fb683eeb6d3b4e90b66c1576f9108a0c'),('808288','158794'),('0d384fd8429449a4957538aedcece601','2111873a431743359c0627a8f5e394c8'),('715021','118964'),('1e638b051f644578ac4d6459e6845fbb','6e745372ba4e4c7683cda767c607b93c')]

def sources():
    import json
    from pg1446_current_cold_stage import W
    seal=json.loads((W/'pg1578-current-completed-seal-v1/manifest.safe.json').read_bytes())
    genuine=json.loads((W/'pg1577-current-root-done-receipt-v1.safe.json').read_bytes())
    if seal['actualExit']!=0 or seal['privateBeforeSha256']!=BEFORE or genuine['actualExit']!=0 or genuine['source']!=SOURCE or genuine['receipt']['endMonotonicUs']!=33583425972:raise ValueError('actual current whole seal and independent receipt required')
    result={}
    for name,s in previous().items():
        name=name.replace('1334','1579')
        for a,b in CHANGES:s=s.replace(a,b)
        # Actual Root absence and verifier audit label are current-generation
        # literals too; historical helper class names alone are reusable ABI.
        s=s.replace('702983','108847').replace('PG1292','PG1544')
        forbidden=['702983','PG1292','pg1292','0.1.0-PG1068','cbca8738',
                   '400b2e34105149ff8f3a11c21da0be6a','d2e3a86f-27a4-4c2a-be21-b512eebf1216']
        if any(value in s for value in forbidden):raise ValueError('historical authority survived current binding')
        if name.endswith('.py'):compile(s,'<actual current owned stop source>','exec')
        result[name]=s
    return result
