#!/bin/bash

# Phase-specific test runner for Adaptive Resume ATS Scorer

echo "=============================================="
echo "Adaptive Resume ATS Scorer - Phase Test Runner"
echo "=============================================="
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "❌ ERROR: Virtual environment not activated"
    echo ""
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate  # Linux/Mac"
    echo "  venv\\Scripts\\activate    # Windows"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ ERROR: pytest not found"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Parse command line argument
PHASE=${1:-all}

echo "Running tests for: $PHASE"
echo ""

case $PHASE in
    0|phase0)
        echo "📦 Phase 0: Environment Setup & Project Initialization"
        pytest tests/test_phase0/ -v --cov=src/config --cov=src/utils --cov=src/pipeline --cov-report=term-missing
        ;;
    
    1|phase1)
        echo "📄 Phase 1: Resume Parsing & Structure Detection"
        pytest tests/test_phase1/ -v --cov=src/parser --cov=src/models --cov-report=term-missing
        ;;
    
    2|phase2)
        echo "📊 Phase 2: Baseline Rule-Based ATS Scoring"
        pytest tests/test_phase2/ -v --cov=src/scoring --cov-report=term-missing
        ;;
    
    all)
        echo "🧪 Running ALL tests (Phase 0 + Phase 1 + Phase 2)"
        pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
        ;;
    
    *)
        echo "❌ Invalid phase: $PHASE"
        echo ""
        echo "Usage: $0 [phase]"
        echo ""
        echo "Available phases:"
        echo "  0 or phase0  - Environment Setup tests"
        echo "  1 or phase1  - Resume Parsing tests"
        echo "  2 or phase2  - ATS Scoring tests"
        echo "  all          - All tests (default)"
        echo ""
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo "=============================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ Tests passed!"
else
    echo "✗ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=============================================="

exit $TEST_EXIT_CODE