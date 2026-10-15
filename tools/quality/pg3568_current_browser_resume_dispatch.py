"""New-only immutable stage and finite prepare; no external Root dispatch."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import bind, sources, TOOLS, CLASS, SOURCE, BOM
from pg3566_current_browser_resume_compile import TARGET
import pg3104_full_native_resume_dispatch as template

REMOTE='/home/ubuntu/pg3568-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
OPTIONS=['-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-i',str(P/'vm-access')]
STAGE=bind(template.STAGE)


def source():
    raw=bind(template.source())
    if any(x in raw+STAGE for x in ['pg3100','pg3102','pg3104','PG2802','pg2802']):
        raise ValueError('legacy final dispatcher role refused')
    compile(raw,'<new-only actual current Browser dispatcher>','exec')
    compile(STAGE,'<new-only immutable current Browser stage>','exec')
    return raw


def main():
    ns={'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'Path':Path,
        'subprocess':subprocess,'sys':sys,'tarfile':tarfile,'W':W,'P':P,'SSH':SSH,
        'management_gate':management_gate,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,
        'CANDIDATE':SOURCE,'BOM':BOM,'TARGET':TARGET,'REMOTE':REMOTE,'GUEST':GUEST,
        'OPTIONS':OPTIONS,'STAGE':STAGE}
    exec(compile(source(),'<actual final current Browser dispatch>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
