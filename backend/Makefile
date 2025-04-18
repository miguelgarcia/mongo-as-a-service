.PHONY: test test-cov coverage-html run clean

test:
	pytest -v

test-cov:
	pytest --cov=app tests/

coverage-html:
	pytest --cov=app --cov-report=html tests/

run:
	uvicorn app.main:app --reload

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
