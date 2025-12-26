#!/bin/bash

# Test runner script for Adaptive Resume ATS Scorer
# Evolution Phase: 0

echo "=============================================="
echo "Adaptive Resume ATS Scorer - Test Suite"
echo "Phase 0: Environment Setup"
echo "Phase 1: Resume Parsing & Structure Detection"
echo "=============================================="
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "❌ ERROR: Virtual environment not activated"
    echo ""
    echo "Please activate your virtual environment first:"
    echo ""
    echo "  On Linux/Mac:"
    echo "    source venv/bin/activate"
    echo ""
    echo "  On Windows:"
    echo "    venv\\Scripts\\activate"
    echo ""
    echo "Then run this script again."
    echo "=============================================="
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ ERROR: pytest not found"
    echo ""
    echo "Please install dependencies first:"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Or install in development mode:"
    echo "  pip install -e ."
    echo "=============================================="
    exit 1
fi

# Run tests with coverage
echo "✓ Virtual environment: ${VIRTUAL_ENV}"
echo "✓ pytest found: $(which pytest)"
echo ""
echo "Running tests with coverage..."
echo ""

pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "=============================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
    echo "  Coverage report: htmlcov/index.html"
else
    echo "✗ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=============================================="

exit $TEST_EXIT_CODE