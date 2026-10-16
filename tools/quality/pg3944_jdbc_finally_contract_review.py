"""New-only annotated-symbol review using static source functions, not dynamic inspect wrappers."""
import pg3940_jdbc_finally_contract_review as review

if __name__ == '__main__':
    review.LABEL = 'PG3944-jdbc-finally-review-v1'
    review.SLOT = 'pg3944-jdbc-finally-review-v1'
    raise SystemExit(review.main())
