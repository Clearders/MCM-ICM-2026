"""
Master script to run all analyses for MCM Problem C
Executes all 4 questions in sequence
"""

import subprocess
import sys


def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "="*70)
    print(f"Running: {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {description}")
        print(f"Error: {e}")
        return False


def main():
    """Run all analysis scripts in sequence"""
    print("="*70)
    print("MCM Problem C - Dancing with the Stars Complete Analysis")
    print("="*70)
    print("\nThis script will run all 4 question analyses in sequence.")
    print("Each analysis builds on the previous ones.\n")
    
    scripts = [
        ("question1_fan_vote_estimation.py", "Question 1: Fan Vote Estimation Model"),
        ("cross_validation_model.py", "Cross-Validation: ML-based Validation of Fan Vote Estimates"),
        ("question2_voting_method_comparison.py", "Question 2: Voting Method Comparison"),
        ("question3_characteristics_analysis.py", "Question 3: Pro Dancer & Celebrity Characteristics"),
        ("question4_improved_voting_system.py", "Question 4: Improved Voting System Proposal")
    ]
    
    results = []
    
    for script, description in scripts:
        success = run_script(script, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    all_success = True
    for description, success in results:
        status = "✓ COMPLETE" if success else "✗ FAILED"
        print(f"{status}: {description}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 All analyses completed successfully!")
        print("\nGenerated files:")
        print("  - question1_fan_vote_estimates.csv")
        print("  - question1_consistency_metrics.csv")
        print("  - cross_validation_summary.csv")
        print("  - cross_validation_comparison.csv")
        print("  - question2_method_comparison.csv")
        print("  - question2_judge_elimination_impact.csv")
        print("  - question3_pro_dancer_stats.csv")
        print("  - question3_age_impact.csv")
        print("  - question3_industry_impact.csv")
        print("  - question3_contestant_stats.csv")
        print("  - question4_proposed_system.csv")
        print("\nYou can now use these results for your MCM report!")
    else:
        print("\n⚠ Some analyses failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
