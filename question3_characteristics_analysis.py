"""
Question 3: Analyze impact of pro dancers and celebrity characteristics
- Model relationship between pro dancers and performance
- Analyze celebrity characteristics (age, industry, etc.)
- Compare impact on judge scores vs fan votes
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """Load DWTS data and fan vote estimates"""
    df = pd.read_csv('2026_MCM_Problem_C_Data.csv')
    try:
        fan_votes = pd.read_csv('question1_fan_vote_estimates.csv')
        return df, fan_votes
    except:
        print("Warning: Fan vote estimates not found.")
        return df, None


def calculate_average_scores(df):
    """Calculate average judge scores for each contestant across their season"""
    results = []
    
    for idx, row in df.iterrows():
        total_score = 0
        total_dances = 0
        
        for week in range(1, 12):
            week_score = 0
            week_dances = 0
            
            for judge in range(1, 5):
                col = f'week{week}_judge{judge}_score'
                if col in row and pd.notna(row[col]) and row[col] not in ['N/A', 0]:
                    try:
                        score = float(row[col])
                        week_score += score
                        week_dances += 1
                    except:
                        pass
            
            if week_dances > 0:
                total_score += week_score
                total_dances += week_dances
        
        avg_score = total_score / total_dances if total_dances > 0 else 0
        
        results.append({
            'celebrity_name': row['celebrity_name'],
            'ballroom_partner': row['ballroom_partner'],
            'celebrity_industry': row['celebrity_industry'],
            'celebrity_age_during_season': row['celebrity_age_during_season'],
            'season': row['season'],
            'placement': row['placement'],
            'avg_judge_score': avg_score,
            'total_dances': total_dances
        })
    
    return pd.DataFrame(results)


def analyze_pro_dancer_impact(contestant_stats, fan_votes):
    """Analyze impact of professional dancers on performance"""
    print("\n=== Pro Dancer Impact Analysis ===")
    
    # Group by pro dancer
    pro_stats = contestant_stats.groupby('ballroom_partner').agg({
        'avg_judge_score': ['mean', 'std', 'count'],
        'placement': ['mean', 'median']
    }).round(3)
    
    # Filter pros with at least 3 partnerships
    pro_stats = pro_stats[pro_stats[('avg_judge_score', 'count')] >= 3]
    pro_stats = pro_stats.sort_values(('avg_judge_score', 'mean'), ascending=False)
    
    print("\nTop Professional Dancers (by average judge score, min 3 partnerships):")
    print(pro_stats.head(10))
    
    # Analyze fan vote impact
    if fan_votes is not None:
        # Merge fan votes with contestant stats to get ballroom partner
        merged = fan_votes.merge(
            contestant_stats[['celebrity_name', 'season', 'ballroom_partner']], 
            left_on=['contestant', 'season'],
            right_on=['celebrity_name', 'season'],
            how='left'
        )
        
        pro_fan_votes = merged.groupby('ballroom_partner')['estimated_fan_votes'].mean()
        
        print("\nPro dancers by average fan votes (top 10):")
        print(pro_fan_votes.sort_values(ascending=False).head(10))
    
    # Save results
    pro_stats.to_csv('question3_pro_dancer_stats.csv')
    print("\nSaved pro dancer stats to 'question3_pro_dancer_stats.csv'")
    
    return pro_stats


def analyze_celebrity_characteristics(contestant_stats, fan_votes):
    """Analyze impact of celebrity characteristics"""
    print("\n=== Celebrity Characteristics Impact ===")
    
    # Age impact
    print("\n--- Age Impact ---")
    age_groups = pd.cut(contestant_stats['celebrity_age_during_season'], 
                       bins=[0, 30, 40, 50, 60, 100],
                       labels=['Under 30', '30-39', '40-49', '50-59', '60+'])
    
    contestant_stats['age_group'] = age_groups
    
    age_impact = contestant_stats.groupby('age_group').agg({
        'avg_judge_score': ['mean', 'std', 'count'],
        'placement': ['mean', 'median']
    }).round(3)
    
    print("\nPerformance by age group:")
    print(age_impact)
    
    # Industry impact
    print("\n--- Industry Impact ---")
    industry_impact = contestant_stats.groupby('celebrity_industry').agg({
        'avg_judge_score': ['mean', 'std', 'count'],
        'placement': ['mean', 'median']
    }).round(3)
    
    # Filter industries with at least 5 contestants
    industry_impact = industry_impact[industry_impact[('avg_judge_score', 'count')] >= 5]
    industry_impact = industry_impact.sort_values(('avg_judge_score', 'mean'), ascending=False)
    
    print("\nPerformance by industry (min 5 contestants):")
    print(industry_impact.head(10))
    
    # Save results
    age_impact.to_csv('question3_age_impact.csv')
    industry_impact.to_csv('question3_industry_impact.csv')
    
    print("\nSaved age impact to 'question3_age_impact.csv'")
    print("\nSaved industry impact to 'question3_industry_impact.csv'")
    
    return age_impact, industry_impact


def build_predictive_model(contestant_stats, fan_votes):
    """Build models to predict judge scores and fan votes based on characteristics"""
    print("\n=== Predictive Model Analysis ===")
    
    # Prepare data
    model_data = contestant_stats.copy()
    
    # Encode categorical variables
    le_partner = LabelEncoder()
    le_industry = LabelEncoder()
    
    model_data['partner_encoded'] = le_partner.fit_transform(model_data['ballroom_partner'].fillna('Unknown'))
    model_data['industry_encoded'] = le_industry.fit_transform(model_data['celebrity_industry'].fillna('Unknown'))
    
    # Features for prediction
    features = ['celebrity_age_during_season', 'partner_encoded', 'industry_encoded', 'season']
    
    # Remove rows with missing values
    model_data = model_data.dropna(subset=features + ['avg_judge_score'])
    
    X = model_data[features]
    y_judge = model_data['avg_judge_score']
    
    # Judge score prediction
    model_judge = LinearRegression()
    model_judge.fit(X, y_judge)
    
    r2_judge = model_judge.score(X, y_judge)
    
    print(f"\nJudge Score Prediction Model:")
    print(f"  R² Score: {r2_judge:.3f}")
    print(f"  Feature Importances (coefficients):")
    for i, feature in enumerate(features):
        print(f"    {feature}: {model_judge.coef_[i]:.4f}")
    
    # Prepare weights data for CSV export
    weights_data = []
    for i, feature in enumerate(features):
        weights_data.append({
            'Factor': feature,
            'Judge_Score_Weight': model_judge.coef_[i],
            'Judge_Score_R2': r2_judge
        })
    
    # Fan vote prediction (if available)
    if fan_votes is not None:
        # Merge fan votes with contestant stats
        fan_vote_avg = fan_votes.groupby(['season', 'contestant'])['estimated_fan_votes'].mean().reset_index()
        fan_vote_avg.columns = ['season', 'celebrity_name', 'avg_fan_votes']
        
        model_data_fan = model_data.merge(fan_vote_avg, on=['season', 'celebrity_name'], how='inner')
        
        if len(model_data_fan) > 0:
            X_fan = model_data_fan[features]
            y_fan = model_data_fan['avg_fan_votes']
            
            model_fan = LinearRegression()
            model_fan.fit(X_fan, y_fan)
            
            r2_fan = model_fan.score(X_fan, y_fan)
            
            print(f"\nFan Vote Prediction Model:")
            print(f"  R² Score: {r2_fan:.3f}")
            print(f"  Feature Importances (coefficients):")
            for i, feature in enumerate(features):
                print(f"    {feature}: {model_fan.coef_[i]:.4f}")
            
            # Add fan vote weights to the data
            for i, factor_dict in enumerate(weights_data):
                factor_dict['Fan_Vote_Weight'] = model_fan.coef_[i]
                factor_dict['Fan_Vote_R2'] = r2_fan
            
            # Compare judge vs fan coefficient patterns
            print("\n--- Comparison: Judge Scores vs Fan Votes ---")
            print("Feature impacts (relative):")
            for i, feature in enumerate(features):
                judge_coef = abs(model_judge.coef_[i])
                fan_coef = abs(model_fan.coef_[i])
                
                if judge_coef > 0 or fan_coef > 0:
                    ratio = fan_coef / judge_coef if judge_coef > 0 else float('inf')
                    print(f"  {feature}:")
                    print(f"    Judge impact: {model_judge.coef_[i]:.4f}")
                    print(f"    Fan impact: {model_fan.coef_[i]:.4f}")
                    print(f"    Fan/Judge ratio: {ratio:.2f}")
    
    # Save factor weights to CSV
    weights_df = pd.DataFrame(weights_data)
    weights_df.to_csv('question3_factor_weights.csv', index=False)
    print("\nSaved factor weights to 'question3_factor_weights.csv'")
    
    return model_judge


def analyze_placement_patterns(contestant_stats):
    """Analyze patterns in final placements"""
    print("\n=== Placement Pattern Analysis ===")
    
    # Winners analysis
    winners = contestant_stats[contestant_stats['placement'] == 1]
    
    print(f"\nWinners Analysis (n={len(winners)}):")
    print(f"  Average age: {winners['celebrity_age_during_season'].mean():.1f}")
    print(f"  Average judge score: {winners['avg_judge_score'].mean():.2f}")
    
    print("\nMost common industries for winners:")
    print(winners['celebrity_industry'].value_counts().head(5))
    
    print("\nMost successful pro dancers (by wins):")
    print(winners['ballroom_partner'].value_counts().head(10))
    
    # Last place analysis
    last_place = contestant_stats.groupby('season')['placement'].max()
    early_eliminations = []
    
    for idx, row in contestant_stats.iterrows():
        season_max = last_place[row['season']]
        if row['placement'] >= season_max - 2:  # Bottom 3
            early_eliminations.append(row)
    
    early_elim_df = pd.DataFrame(early_eliminations)
    
    print(f"\nEarly Eliminations Analysis (bottom 3, n={len(early_elim_df)}):")
    print(f"  Average age: {early_elim_df['celebrity_age_during_season'].mean():.1f}")
    print(f"  Average judge score: {early_elim_df['avg_judge_score'].mean():.2f}")


def main():
    """Main execution function"""
    print("="*60)
    print("Question 3: Pro Dancer & Celebrity Characteristics Analysis")
    print("="*60)
    
    # Load data
    df, fan_votes = load_data()
    
    # Calculate contestant statistics
    print("\nCalculating contestant statistics...")
    contestant_stats = calculate_average_scores(df)
    
    # Analyze pro dancer impact
    pro_stats = analyze_pro_dancer_impact(contestant_stats, fan_votes)
    
    # Analyze celebrity characteristics
    age_impact, industry_impact = analyze_celebrity_characteristics(contestant_stats, fan_votes)
    
    # Build predictive models
    model = build_predictive_model(contestant_stats, fan_votes)
    
    # Analyze placement patterns
    analyze_placement_patterns(contestant_stats)
    
    # Save comprehensive stats
    contestant_stats.to_csv('question3_contestant_stats.csv', index=False)
    print("\nSaved contestant statistics to 'question3_contestant_stats.csv'")
    
    print("\n✓ Question 3 complete!")


if __name__ == "__main__":
    main()
