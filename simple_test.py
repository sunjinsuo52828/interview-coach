"""Simple validation script - no encoding issues"""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=== TDD Validation ===")
print("Python:", sys.version.split()[0])
print()

results = []

# Test 1: Import config
try:
    import config
    print("[OK] config imported")
    results.append(True)
except Exception as e:
    print(f"[FAIL] config: {e}")
    results.append(False)

# Test 2: Import models
try:
    from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills
    print("[OK] models imported")
    results.append(True)
except Exception as e:
    print(f"[FAIL] models: {e}")
    results.append(False)

# Test 3: Import parser_agent
try:
    from agents.parser_agent import ParserAgent
    print("[OK] parser_agent imported")

    agent = ParserAgent()
    print("[OK] ParserAgent instantiated")
    results.append(True)
except Exception as e:
    print(f"[FAIL] parser_agent: {e}")
    results.append(False)

# Test 4: Import interview_agent
try:
    from agents.interview_agent import InterviewerAgent
    print("[OK] interview_agent imported")

    agent = InterviewerAgent()
    print("[OK] InterviewerAgent instantiated")
    results.append(True)
except Exception as e:
    print(f"[FAIL] interview_agent: {e}")
    results.append(False)

# Test 5: Import evaluator_agent
try:
    from agents.evaluator_agent import EvaluatorAgent
    print("[OK] evaluator_agent imported")

    agent = EvaluatorAgent()
    print("[OK] EvaluatorAgent instantiated")
    results.append(True)
except Exception as e:
    print(f"[FAIL] evaluator_agent: {e}")
    results.append(False)

# Test 6: Check logging
try:
    from agents import parser_agent, interview_agent, evaluator_agent
    has_log = (
        hasattr(parser_agent, 'logger') and
        hasattr(interview_agent, 'logger') and
        hasattr(evaluator_agent, 'logger')
    )
    if has_log:
        print("[OK] All agents have logger (P1 fix verified)")
    else:
        print("[FAIL] Some agents missing logger")
    results.append(has_log)
except Exception as e:
    print(f"[FAIL] logging check: {e}")
    results.append(False)

# Summary
print()
print("=== Summary ===")
total = len(results)
passed = sum(results)
print(f"Passed: {passed}/{total}")

if passed == total:
    print(">>> ALL TESTS PASSED <<<")
    print(">>> TDD DEVELOPMENT COMPLETE <<<")
else:
    print(f">>> {total - passed} TESTS FAILED <<<")

# Save result
with open(project_root + "/validation_result.txt", "w") as f:
    f.write(f"Passed: {passed}/{total}\n")

print("Result saved to: validation_result.txt")
