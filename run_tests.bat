@echo off
echo Installing test dependencies...
pip install -r requirements.txt

echo Running all tests...
pytest -v

echo Running offline tests only...
pytest -m offline -v

echo Generating test reports...
pytest --alluredir=test-results --cov=src --cov-report=html:coverage-report

echo.
echo ==================================================
echo TEST SUMMARY
echo ==================================================
echo - Allure results generated in: test-results/
echo - Coverage report: coverage-report/index.html
echo - To view Allure report, install allure first
echo ==================================================