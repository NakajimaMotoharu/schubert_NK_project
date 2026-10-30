"""Qualified no-trace resource DOM post for whole original Logs8; no backend or Java counter credit."""
import reviewed_resource_dom_post_v2 as core
import pg14824_log_search_template_eight_pt as original

PROFILE=dict(rawFolder='PG14824-log-search-template-eight-pt-v1',rawSha256='4ee07f6b943058d0c7f8491e9bc084cac57b89949ab292e612916bbb2d2f7805',postFolder='PG14826-log-search-template-eight-post-v1',resourceOwners={'templates/logs.html':'WBS-P016-14','templates/fragments/log-pagination.html':'WBS-P015-07'})

if __name__=='__main__':core.verify_profile(original,PROFILE)
