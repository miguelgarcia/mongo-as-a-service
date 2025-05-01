.PHONY: test test-cov coverage-html run clean

test:
	pytest -v --ignore=tests/test_integration.py

test-cov:
	pytest --cov=app --ignore=tests/test_integration.py tests/ 

coverage-html:
	pytest --cov=app --ignore=tests/test_integration.py --cov-report=html tests/

run:
	uvicorn app.main:create_app --reload

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
