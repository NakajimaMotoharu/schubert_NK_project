"""Independent current72; all15 executable classes remain in CRC/official four-counter inventory."""
import pg7392_api_outbox_rows_post as previous
import pg7402_api_generated_contract_host as host

METHODS={
 'genMetric001PoolRecordEqualityUsesEveryComponentAndRejectsNullAndOtherTypes',
 'genMetric002PoolRecordGeneratedHashAndTextHaveIndependentFixedVectors',
 'genMetric003OutboxRecordEqualityUsesEveryComponentAndRejectsNullAndOtherTypes',
 'genMetric004OutboxRecordGeneratedHashAndTextHaveIndependentFixedVectors',
 'genMetric005AsyncEnumGeneratedFactoriesAndDefensiveArrayAreClosed',
 'genMetric006PoolEnumGeneratedFactoriesAndDefensiveArrayAreClosed',
 'genMetric007OperationEnumGeneratedFactoriesAndDefensiveArrayAreClosed',
 'genMetric008OutboxEnumGeneratedFactoriesAndDefensiveArrayAreClosed'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7402-api-generated-contract-host-v1'
    post.OUT=post.host.BASE/'PG7404-api-generated-contract-post-v1'
    post.PRIVATE=post.host.W/'pg7404-api-generated-contract-post-v1'
    post.METHODS|=METHODS
    post.EXPECTED_SUITES[host.SUITES[8]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=72;post.SOURCE_FILE_COUNT=18
    post.main()
