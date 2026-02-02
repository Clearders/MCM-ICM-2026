# Quick Start Guide

## Running the Analysis

### Option 1: Run All Analyses (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Run complete analysis (all 4 questions)
python run_all_analyses.py
```

This will generate all output files in ~2-3 minutes.

### Option 2: Run Individual Questions
```bash
# Question 1: Fan vote estimation (required for others)
python question1_fan_vote_estimation.py

# Question 2: Voting method comparison
python question2_voting_method_comparison.py

# Question 3: Characteristics analysis
python question3_characteristics_analysis.py

# Question 4: Proposed voting system
python question4_improved_voting_system.py
```

## Output Files

After running the analysis, you will have:

**Question 1 outputs:**
- `question1_fan_vote_estimates.csv` - 2,378 fan vote estimates
- `question1_consistency_metrics.csv` - Model validation metrics

**Question 2 outputs:**
- `question2_method_comparison.csv` - Rank vs percentage comparison
- `question2_judge_elimination_impact.csv` - Judge elimination analysis

**Question 3 outputs:**
- `question3_contestant_stats.csv` - Complete contestant statistics
- `question3_pro_dancer_stats.csv` - Pro dancer performance
- `question3_age_impact.csv` - Age impact on performance
- `question3_industry_impact.csv` - Industry impact on performance
- `question3_factor_weights.csv` - Factor weights from predictive models

**Question 4 outputs:**
- `question4_proposed_system.csv` - Proposed system specification

## Key Findings Summary

### Question 1: Fan Vote Estimation
- Estimated 2,378 fan vote instances with 76% average certainty
- Multiple valid solutions exist (33.94% exact match expected)
- Fans tend to compensate for low judge scores (underdog effect)

### Question 2: Method Comparison
- Rank and percentage methods differ in 55.8% of weeks
- Percentage method better predicts actual outcomes (32.5% vs 8.8%)
- Judge elimination would change outcomes in 37.6% of weeks
- Controversial winners (Bobby Bones, Bristol Palin) had strong fan support

### Question 3: Characteristics Impact
- **Top pro dancer**: Derek Hough (8.88 avg score, 6 wins)
- **Optimal age**: 25-35 years old (winners avg 29.6 years)
- **Best industry**: Olympic athletes (8.45 avg score)
- **Judges more predictable** (R²=0.29) than fans (R²=0.12)

### Question 4: Recommended System
**Dynamic Weighted Voting:**
- Early weeks: 60% judges, 40% fans
- Middle weeks: 50% judges, 50% fans
- Finals: 40% judges, 60% fans

**Benefits:** Fair, transparent, reduces controversy, maintains quality

## For MCM Report

Use the following files for your report:
1. **ANALYSIS_SUMMARY.md** - Complete findings summary
2. **Output CSV files** - Detailed data and results
3. **Python scripts** - Methodology reference

## Troubleshooting

**If you get import errors:**
```bash
pip install --upgrade -r requirements.txt
```

**If Question 2-4 fail:**
Make sure to run Question 1 first, as others depend on its output.

**To regenerate all outputs:**
```bash
rm question*.csv
python run_all_analyses.py
```

## Contact

This solution was developed for the 2026 MCM Problem C competition.

For questions about the code or methodology, refer to:
- README_SOLUTION.md - Detailed methodology
- ANALYSIS_SUMMARY.md - Key findings
- Individual Python scripts - Implementation details
