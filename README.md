# MCM-ICM-2026

## 2026 MCM Problem C: Data With The Stars

Complete Python solution for analyzing Dancing with the Stars voting systems across 34 seasons.

### 📊 Problem Overview

Analyze the Dancing with the Stars competition to:
1. Estimate unknown fan votes based on elimination results
2. Compare rank vs percentage voting methods and analyze controversial cases
3. Analyze impact of pro dancers and celebrity characteristics on performance
4. Propose an improved voting system that is fairer and more exciting

### ✅ Solution Summary

This repository contains a comprehensive data science solution with:
- **6 Python scripts** (1,855+ lines of code)
- **11 CSV output files** with analysis results
- **4 documentation files** with methodology and findings

**NEW: Cross-Validation Model** - Independent ML-based validation using Random Forest and Gradient Boosting to verify fan vote estimates

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run complete analysis
python run_all_analyses.py
```

Runtime: ~2-3 minutes

### 📁 Repository Structure

```
├── 2026_MCM_Problem_C.pdf              # Problem statement
├── 2026_MCM_Problem_C_Data.csv         # Contest data (34 seasons)
│
├── question1_fan_vote_estimation.py    # Q1: Fan vote estimation model
├── cross_validation_model.py           # Cross-validation using ML models
├── question2_voting_method_comparison.py # Q2: Voting method comparison
├── question3_characteristics_analysis.py # Q3: Characteristics analysis
├── question4_improved_voting_system.py # Q4: Proposed voting system
├── run_all_analyses.py                 # Master script
│
├── README_SOLUTION.md                  # Complete methodology
├── ANALYSIS_SUMMARY.md                 # Key findings & results
├── QUICK_START.md                      # Usage guide
└── requirements.txt                    # Python dependencies
```

### 🔑 Key Findings

**Question 1**: Fan votes estimated with 76% average certainty; fans tend to compensate for low judge scores

**Cross-Validation**: ML models (Random Forest & Gradient Boosting) validate optimization estimates with high correlation (R² > 0.85)

**Question 2**: Percentage method outperforms rank method; controversial winners had strong, sustained fan support

**Question 3**: Derek Hough is top pro dancer (8.88 avg score); optimal contestant age is 25-35; athletes perform best

**Question 4**: Recommended **Dynamic Weighted Voting** with progressive shift from judge-heavy (60/40) to fan-heavy (40/60) through the season

### 📊 Results Generated

- `question1_fan_vote_estimates.csv` - 2,378 fan vote estimates
- `question1_consistency_metrics.csv` - Model validation metrics
- `cross_validation_summary.csv` - ML cross-validation results
- `cross_validation_comparison.csv` - Model comparison analysis
- `question2_method_comparison.csv` - 274 week comparisons
- `question2_judge_elimination_impact.csv` - 103 weeks affected by judge method
- `question3_contestant_stats.csv` - 421 contestant statistics
- `question3_pro_dancer_stats.csv` - Pro dancer rankings
- `question3_age_impact.csv` - Age impact analysis
- `question3_industry_impact.csv` - Industry impact analysis  
- `question4_proposed_system.csv` - Proposed system specification

### 📖 Documentation

- **README_SOLUTION.md** - Detailed methodology and approach
- **ANALYSIS_SUMMARY.md** - Complete findings with statistics
- **CROSS_VALIDATION.md** - Cross-validation model documentation
- **QUICK_START.md** - Usage instructions and troubleshooting

### 🛠️ Technologies Used

- Python 3.8+
- pandas - Data manipulation
- numpy - Numerical computing
- scipy - Optimization
- scikit-learn - Predictive modeling
- matplotlib & seaborn - Visualization

### 👥 Team

Solution developed for the 2026 MCM/ICM Competition

### 📄 License

This code is provided for educational purposes as part of the MCM/ICM competition.