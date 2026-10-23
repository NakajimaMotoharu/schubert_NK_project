"""BUG1661: new-only static review, correct actual RecordsFilter-to-Matcher delegation; no PT replay."""
import pg7411_api_generated_value_review as review

if __name__=='__main__':
    review.OUT=review.host.BASE/'PG7413-api-generated-value-review-v2'
    review.main()
