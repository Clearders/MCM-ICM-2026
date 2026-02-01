"""
Question 1: Develop a model to estimate fan votes for each contestant/week
- Estimate fan votes that lead to results consistent with eliminations
- Provide measures of consistency
- Calculate certainty measures for each estimate
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize, differential_evolution
import warnings
warnings.filterwarnings('ignore')


def load_data():
    """Load and prepare the DWTS data"""
    df = pd.read_csv('2026_MCM_Problem_C_Data.csv')
    return df


def get_judge_scores_by_week(df, season, week):
    """Extract judge scores for a specific season and week"""
    season_data = df[df['season'] == season].copy()
    
    # Get judge score columns for this week
    judge_cols = [f'week{week}_judge{j}_score' for j in range(1, 5)]
    
    scores = []
    contestants = []
    
    for idx, row in season_data.iterrows():
        contestant_scores = []
        for col in judge_cols:
            if col in row and pd.notna(row[col]) and row[col] != 'N/A' and row[col] != 0:
                try:
                    contestant_scores.append(float(row[col]))
                except:
                    pass
        
        # Only include if contestant competed this week (has scores)
        if len(contestant_scores) > 0:
            total_score = sum(contestant_scores)
            contestants.append(row['celebrity_name'])
            scores.append(total_score)
    
    return contestants, scores


def get_eliminated_contestant(df, season, week):
    """Get the contestant eliminated in a specific week"""
    season_data = df[df['season'] == season]
    
    for idx, row in season_data.iterrows():
        result = str(row['results'])
        if f'Eliminated Week {week}' in result:
            return row['celebrity_name']
    
    return None


def estimate_fan_votes_rank_method(judge_scores, eliminated_idx):
    """
    Estimate fan votes using rank-based method
    Returns fan votes that would lead to the correct elimination
    
    Method: Use optimization to find fan votes where:
    - Combined ranks lead to correct elimination
    - Fan votes are realistic (constrained)
    """
    n = len(judge_scores)
    if n <= 1:
        return [1.0] * n, 1.0
    
    # Judge ranks (1 is best)
    judge_ranks = np.argsort(np.argsort(-np.array(judge_scores))) + 1
    
    def objective(fan_votes):
        """Minimize deviation from inverse judge ranking (fans compensate for judges)"""
        # Assume fans tend to vote opposite to judge rankings (to save underdogs)
        target_votes = []
        for i in range(n):
            # Higher judge rank (worse) → higher fan votes (compensation)
            target_votes.append(1000000 * judge_ranks[i])
        
        return np.sum((fan_votes - target_votes) ** 2)
    
    def constraint_correct_elimination(fan_votes):
        """Ensure the eliminated contestant has worst combined rank"""
        fan_ranks = np.argsort(np.argsort(-fan_votes)) + 1
        combined_ranks = judge_ranks + fan_ranks
        
        # Eliminated should have highest combined rank
        eliminated_rank = combined_ranks[eliminated_idx]
        
        # Must be strictly worst
        for i in range(n):
            if i != eliminated_idx and combined_ranks[i] >= eliminated_rank:
                return -1
        
        return 1
    
    # Initial guess: inverse of judge ranks
    x0 = np.array([1000000 * judge_ranks[i] for i in range(n)])
    
    # Bounds: fan votes must be positive
    bounds = [(100000, 10000000) for _ in range(n)]
    
    # Try to find valid fan votes
    constraints = {'type': 'ineq', 'fun': constraint_correct_elimination}
    
    try:
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, 
                         constraints=constraints, options={'maxiter': 1000})
        
        if result.success and constraint_correct_elimination(result.x) >= 0:
            # Calculate certainty based on how much we had to deviate from uniform
            certainty = 1.0 / (1.0 + np.std(result.x) / np.mean(result.x))
            return result.x.tolist(), certainty
        else:
            # Use differential evolution as backup
            result = differential_evolution(
                lambda x: objective(x) if constraint_correct_elimination(x) >= 0 else 1e10,
                bounds, seed=42, maxiter=500
            )
            certainty = 1.0 / (1.0 + np.std(result.x) / np.mean(result.x))
            return result.x.tolist(), certainty
            
    except:
        # Fallback: assign votes inversely proportional to judge rank
        fan_votes = []
        for i in range(n):
            if i == eliminated_idx:
                fan_votes.append(100000)  # Lowest votes
            else:
                fan_votes.append(1000000 * (n - judge_ranks[i]))
        return fan_votes, 0.5


def estimate_fan_votes_percentage_method(judge_scores, eliminated_idx):
    """
    Estimate fan votes using percentage-based method (seasons 3-27)
    """
    n = len(judge_scores)
    if n <= 1:
        return [1.0] * n, 1.0
    
    total_judge_score = sum(judge_scores)
    judge_percentages = [score / total_judge_score for score in judge_scores]
    
    def objective(fan_votes):
        """Minimize deviation from compensating distribution"""
        # Fans tend to compensate for lower judge scores
        target = []
        for i in range(n):
            # Lower judge percentage → higher target fan votes
            target.append(1000000 * (1 - judge_percentages[i]))
        return np.sum((fan_votes - target) ** 2)
    
    def constraint_correct_elimination(fan_votes):
        """Ensure eliminated contestant has lowest combined percentage"""
        total_fan = sum(fan_votes)
        if total_fan == 0:
            return -1
        
        fan_percentages = [v / total_fan for v in fan_votes]
        combined_percentages = [judge_percentages[i] + fan_percentages[i] 
                               for i in range(n)]
        
        eliminated_pct = combined_percentages[eliminated_idx]
        
        # Must be strictly lowest
        for i in range(n):
            if i != eliminated_idx and combined_percentages[i] <= eliminated_pct:
                return -1
        
        return 1
    
    # Initial guess: compensating distribution
    x0 = np.array([1000000 * (1 - judge_percentages[i]) for i in range(n)])
    bounds = [(100000, 10000000) for _ in range(n)]
    
    try:
        constraints = {'type': 'ineq', 'fun': constraint_correct_elimination}
        result = minimize(objective, x0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'maxiter': 1000})
        
        if result.success and constraint_correct_elimination(result.x) >= 0:
            certainty = 1.0 / (1.0 + np.std(result.x) / np.mean(result.x))
            return result.x.tolist(), certainty
        else:
            result = differential_evolution(
                lambda x: objective(x) if constraint_correct_elimination(x) >= 0 else 1e10,
                bounds, seed=42, maxiter=500
            )
            certainty = 1.0 / (1.0 + np.std(result.x) / np.mean(result.x))
            return result.x.tolist(), certainty
            
    except:
        # Fallback
        fan_votes = []
        for i in range(n):
            if i == eliminated_idx:
                fan_votes.append(100000)
            else:
                fan_votes.append(1000000 * (1 - judge_percentages[i]))
        return fan_votes, 0.5


def estimate_all_fan_votes(df):
    """Estimate fan votes for all weeks in all seasons"""
    results = []
    
    seasons = sorted(df['season'].unique())
    
    for season in seasons:
        print(f"Processing Season {season}...")
        
        # Determine which method was used
        if season <= 2 or season >= 28:
            method = 'rank'
        else:
            method = 'percentage'
        
        # Process each week
        for week in range(1, 12):  # Max 11 weeks
            contestants, judge_scores = get_judge_scores_by_week(df, season, week)
            
            if len(contestants) == 0:
                continue
            
            eliminated = get_eliminated_contestant(df, season, week)
            
            if eliminated and eliminated in contestants:
                eliminated_idx = contestants.index(eliminated)
                
                if method == 'rank':
                    fan_votes, certainty = estimate_fan_votes_rank_method(
                        judge_scores, eliminated_idx)
                else:
                    fan_votes, certainty = estimate_fan_votes_percentage_method(
                        judge_scores, eliminated_idx)
                
                for i, contestant in enumerate(contestants):
                    results.append({
                        'season': season,
                        'week': week,
                        'contestant': contestant,
                        'judge_score': judge_scores[i],
                        'estimated_fan_votes': fan_votes[i],
                        'eliminated': (i == eliminated_idx),
                        'method': method,
                        'certainty': certainty
                    })
    
    return pd.DataFrame(results)


def validate_consistency(fan_vote_estimates):
    """Validate that estimated fan votes lead to correct eliminations"""
    consistency_metrics = []
    
    for season in fan_vote_estimates['season'].unique():
        for week in fan_vote_estimates[fan_vote_estimates['season'] == season]['week'].unique():
            week_data = fan_vote_estimates[
                (fan_vote_estimates['season'] == season) & 
                (fan_vote_estimates['week'] == week)
            ]
            
            if len(week_data) == 0:
                continue
            
            method = week_data.iloc[0]['method']
            
            # Check if our estimates lead to correct elimination
            if method == 'rank':
                # Rank-based
                judge_ranks = week_data['judge_score'].rank(ascending=False)
                fan_ranks = week_data['estimated_fan_votes'].rank(ascending=False)
                combined_ranks = judge_ranks + fan_ranks
                predicted_elimination = combined_ranks.idxmax()
            else:
                # Percentage-based
                total_judge = week_data['judge_score'].sum()
                total_fan = week_data['estimated_fan_votes'].sum()
                
                judge_pct = week_data['judge_score'] / total_judge
                fan_pct = week_data['estimated_fan_votes'] / total_fan
                combined_pct = judge_pct + fan_pct
                predicted_elimination = combined_pct.idxmin()
            
            actual_elimination = week_data[week_data['eliminated']].index
            
            if len(actual_elimination) > 0:
                correct = (predicted_elimination == actual_elimination[0])
                
                consistency_metrics.append({
                    'season': season,
                    'week': week,
                    'correct': correct,
                    'certainty': week_data.iloc[0]['certainty']
                })
    
    consistency_df = pd.DataFrame(consistency_metrics)
    
    if len(consistency_df) > 0:
        overall_accuracy = consistency_df['correct'].mean()
        avg_certainty = consistency_df['certainty'].mean()
        
        print(f"\n=== Consistency Validation ===")
        print(f"Overall Accuracy: {overall_accuracy:.2%}")
        print(f"Average Certainty: {avg_certainty:.3f}")
        print(f"Total Weeks Validated: {len(consistency_df)}")
        
        return consistency_df
    
    return None


def main():
    """Main execution function"""
    print("="*60)
    print("Question 1: Fan Vote Estimation Model")
    print("="*60)
    
    # Load data
    df = load_data()
    print(f"\nLoaded {len(df)} contestant records from {df['season'].nunique()} seasons")
    
    # Estimate fan votes
    print("\nEstimating fan votes for all seasons and weeks...")
    fan_vote_estimates = estimate_all_fan_votes(df)
    
    # Save results
    fan_vote_estimates.to_csv('question1_fan_vote_estimates.csv', index=False)
    print(f"\nSaved {len(fan_vote_estimates)} fan vote estimates to 'question1_fan_vote_estimates.csv'")
    
    # Validate consistency
    consistency_results = validate_consistency(fan_vote_estimates)
    
    if consistency_results is not None:
        consistency_results.to_csv('question1_consistency_metrics.csv', index=False)
        print("\nSaved consistency metrics to 'question1_consistency_metrics.csv'")
    
    # Summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Certainty by Method:")
    print(fan_vote_estimates.groupby('method')['certainty'].agg(['mean', 'std', 'min', 'max']))
    
    print("\n✓ Question 1 complete!")
    

if __name__ == "__main__":
    main()
