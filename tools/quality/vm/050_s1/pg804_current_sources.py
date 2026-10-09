"""New796 current-source normal owned readback; no old unknown close normalization."""
from pathlib import Path
from pg798_probe_sources import java as previous_java,helper as previous_helper
from pg799_pending_sources import SOURCE,DIGEST,OLD_SOURCE,OLD_DIGEST
R=Path(__file__).resolve().parent
__all__=['java','helper','SOURCE','DIGEST','bind']

def bind(raw):
 return raw.replace('Pg798DatabaseProbe','Pg804CurrentReadback').replace('pg798','pg804').replace('PG798','PG804').replace('pg804-scope-tools-v1','pg804-current-tools-v1').replace('pg804-scope-probe-v1','pg804-current-readback-v1').replace('0.1.0-PG750','0.1.0-PG796').replace('"PG750"','"PG796"').replace('"pg750"','"pg796"').replace(OLD_SOURCE,SOURCE).replace(OLD_DIGEST,DIGEST)

def java():return bind(previous_java())

def helper():
 raw=bind(previous_helper())
 return raw.replace('pg787-retired-post-v1/after.private.json','pg803-published-handoff-v2/after.private.json').replace('07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2','d82a4626f8b9a0cb00130087413d1dd227dd04ced4f9add680668f99b27c6a92')
