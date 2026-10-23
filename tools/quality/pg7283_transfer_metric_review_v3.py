"""BUG1658 correction: new Transfer violations zero, unchanged original approved heuristic rows preserved."""
import pg7282_transfer_metric_review_v2 as review

if __name__=='__main__':
    review.OUT=review.host.BASE/'PG7283-transfer-metric-review-v3'
    review.main()
