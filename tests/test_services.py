from app_services import AuditService
from config import get_config


def test_audit_service_summary_has_reasonable_values():
    service = AuditService(get_config())
    corpus = service.load_corpus()
    results = service.summarize(
        service.run_audit(failure_rate=0.0, seed=1, corpus_path=get_config().corpus_path)[0]
    )
    assert results.total_sessions == len(corpus)
    assert 0 <= results.score <= 100
