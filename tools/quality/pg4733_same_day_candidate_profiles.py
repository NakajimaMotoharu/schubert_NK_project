"""Before-only redacted route histogram after limited4732 refused applicability."""
import types
from pyflakes.api import check
import pg4732_same_day_oracle_preflight as previous
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4733-same-day-candidate-profiles-v1'


def payload():
    raw=previous.payload()
    marker="expected=candidates(before,cutoff.isoformat());inbox=classify_inbox(before,expected['inbox_scan_candidates'])"
    replacement="""expected=candidates(before,cutoff.isoformat())
 profiles={};selected=set(expected['inbox_scan_candidates']);sessions={str(r['id'])for r in before['schubert.auth_sessions']}
 for row in before['schubert.request_inbox']:
  if row['message_id']not in selected:continue
  profile='|'.join(str(row[k])for k in ['request_layout_id','response_layout_id','processing_state','result_ref_type'])+'|sessionPresent='+str(str(row['result_ref_uuid'])in sessions)
  profiles[profile]=profiles.get(profile,0)+1
 inbox={'deleted':[],'protected':[]}
""".rstrip()
    if raw.count(marker)!=1:raise ValueError('one unsupported route boundary')
    raw=raw.replace(marker,replacement)
    raw=raw.replace("'sameDayOracleCompatible':compatible","'limitedOracleApplicabilityAssumed':False,'candidateProfiles':profiles")
    raw=raw.replace(" compatible=not missing and 'CLEAN_INBOX_OUTBOX'not in skips and not inbox['deleted']and not any(other.values())and {'CLEAN_SESSION','CLEAN_LOG'}<=skips"," missingHistory=missing")
    raw=raw.replace("'history':{s:","'missingHistory':missingHistory,'history':{s:")
    if check(raw,'<redacted unsupported profiles>'):raise ValueError('complete emitted namespace')
    compile(raw,'<before only route counts>','exec');return raw


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':previous.current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
