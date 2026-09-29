import json
from pathlib import Path

from backend.app.decision_engine import make_final_decision


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FILE = PROJECT_ROOT / "data" / "expected_decisions.json"


def load_expected_decisions():
    with EXPECTED_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    expected_decisions = load_expected_decisions()

    results = []
    passed = 0

    print("=" * 70)
    print("SOC ALERT TRIAGE AGENT - FULL EVALUATION")
    print("=" * 70)
    print()

    for item in expected_decisions:
        alert_id = item["alert_id"]
        expected = item["expected_verdict"]

        print(f"Evaluating {alert_id}...")

        try:
            result = make_final_decision(alert_id)

            candidate = result["candidate_verdict"]
            final = result["final_verdict"]

            is_pass = final == expected

            if is_pass:
                passed += 1

            results.append(
                {
                    "alert_id": alert_id,
                    "expected": expected,
                    "candidate": candidate,
                    "final": final,
                    "passed": is_pass,
                }
            )

            status = "PASS" if is_pass else "FAIL"

            print(
                f"  Expected : {expected}\n"
                f"  Candidate: {candidate}\n"
                f"  Final    : {final}\n"
                f"  Result   : {status}"
            )

        except Exception as exc:
            results.append(
                {
                    "alert_id": alert_id,
                    "expected": expected,
                    "candidate": "ERROR",
                    "final": "ERROR",
                    "passed": False,
                    "error": str(exc),
                }
            )

            print(f"  ERROR    : {exc}")

        print()

    total = len(expected_decisions)
    accuracy = (passed / total * 100) if total else 0

    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total alerts : {total}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {total - passed}")
    print(f"Accuracy     : {accuracy:.2f}%")
    print("=" * 70)

    print()
    print("DETAILED RESULTS")
    print("-" * 70)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{result['alert_id']} | "
            f"Expected={result['expected']} | "
            f"Final={result['final']} | "
            f"{status}"
        )

    output_file = PROJECT_ROOT / "evaluation" / "evaluation_results.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "total_alerts": total,
                "passed": passed,
                "failed": total - passed,
                "accuracy_percent": round(accuracy, 2),
                "results": results,
            },
            file,
            indent=2,
        )

    print()
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()