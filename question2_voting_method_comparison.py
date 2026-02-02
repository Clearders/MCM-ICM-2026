"""
Question 2: Compare and contrast voting methods (rank vs percentage)
- Apply both methods to each season
- Analyze controversial cases
- Examine impact of judge elimination of bottom two
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """Load DWTS data and fan vote estimates"""
    df = pd.read_csv('2026_MCM_Problem_C_Data.csv')
    try:
        fan_votes = pd.read_csv('question1_fan_vote_estimates.csv')
        return df, fan_votes
    except:
        print("Warning: Fan vote estimates not found. Run question1 first.")
        return df, None


def apply_rank_method(judge_scores, fan_votes):
    """Apply rank-based combination method"""
    if len(judge_scores) != len(fan_votes):
        return None
    
    n = len(judge_scores)
    judge_ranks = np.argsort(np.argsort(-np.array(judge_scores))) + 1
    fan_ranks = np.argsort(np.argsort(-np.array(fan_votes))) + 1
    combined_ranks = judge_ranks + fan_ranks
    
    # Lower combined rank is better, highest should be eliminated
    elimination_idx = np.argmax(combined_ranks)
    
    return {
        'judge_ranks': judge_ranks.tolist(),
        'fan_ranks': fan_ranks.tolist(),
        'combined_ranks': combined_ranks.tolist(),
        'eliminated_idx': elimination_idx
    }


def apply_percentage_method(judge_scores, fan_votes):
    """Apply percentage-based combination method"""
    if len(judge_scores) != len(fan_votes):
        return None
    
    total_judge = sum(judge_scores)
    total_fan = sum(fan_votes)
    
    if total_judge == 0 or total_fan == 0:
        return None
    
    judge_percentages = [s / total_judge for s in judge_scores]
    fan_percentages = [v / total_fan for v in fan_votes]
    combined_percentages = [judge_percentages[i] + fan_percentages[i] 
                           for i in range(len(judge_scores))]
    
    # Lowest combined percentage should be eliminated
    elimination_idx = np.argmin(combined_percentages)
    
    return {
        'judge_percentages': judge_percentages,
        'fan_percentages': fan_percentages,
        'combined_percentages': combined_percentages,
        'eliminated_idx': elimination_idx
    }


def compare_methods_across_seasons(df, fan_votes):
    """Compare rank and percentage methods across all seasons"""
    if fan_votes is None:
        print("Cannot compare methods without fan vote estimates")
        return None
    
    comparison_results = []
    
    for season in sorted(fan_votes['season'].unique()):
        for week in sorted(fan_votes[fan_votes['season'] == season]['week'].unique()):
            week_data = fan_votes[
                (fan_votes['season'] == season) & 
                (fan_votes['week'] == week)
            ].copy()
            
            if len(week_data) == 0:
                continue
            
            contestants = week_data['contestant'].tolist()
            judge_scores = week_data['judge_score'].tolist()
            fan_vote_estimates = week_data['estimated_fan_votes'].tolist()
            actual_eliminated = week_data[week_data['eliminated']]['contestant'].values
            
            # Apply both methods
            rank_result = apply_rank_method(judge_scores, fan_vote_estimates)
            pct_result = apply_percentage_method(judge_scores, fan_vote_estimates)
            
            if rank_result and pct_result:
                rank_eliminated = contestants[rank_result['eliminated_idx']]
                pct_eliminated = contestants[pct_result['eliminated_idx']]
                
                methods_agree = (rank_eliminated == pct_eliminated)
                
                # Check which method matches actual
                rank_correct = (len(actual_eliminated) > 0 and 
                              rank_eliminated == actual_eliminated[0])
                pct_correct = (len(actual_eliminated) > 0 and 
                             pct_eliminated == actual_eliminated[0])
                
                comparison_results.append({
                    'season': season,
                    'week': week,
                    'rank_eliminated': rank_eliminated,
                    'pct_eliminated': pct_eliminated,
                    'actual_eliminated': actual_eliminated[0] if len(actual_eliminated) > 0 else None,
                    'methods_agree': methods_agree,
                    'rank_correct': rank_correct,
                    'pct_correct': pct_correct,
                    'difference': 'Same' if methods_agree else 'Different'
                })
    
    comparison_df = pd.DataFrame(comparison_results)
    
    print("\n=== Method Comparison Results ===")
    print(f"Total weeks compared: {len(comparison_df)}")
    print(f"Methods agree: {comparison_df['methods_agree'].sum()} ({comparison_df['methods_agree'].mean():.1%})")
    print(f"Methods differ: {(~comparison_df['methods_agree']).sum()} ({(~comparison_df['methods_agree']).mean():.1%})")
    
    print(f"\nRank method accuracy: {comparison_df['rank_correct'].mean():.1%}")
    print(f"Percentage method accuracy: {comparison_df['pct_correct'].mean():.1%}")
    
    return comparison_df


def analyze_controversial_cases(df, fan_votes):
    """Analyze specific controversial cases"""
    if fan_votes is None:
        print("Cannot analyze without fan vote estimates")
        return
    
    print("\n" + "="*60)
    print("Controversial Case Analysis")
    print("="*60)
    
    controversial_cases = [
        {'season': 2, 'celebrity': 'Jerry Rice', 'description': 'Runner up despite lowest judge scores in 5 weeks'},
        {'season': 4, 'celebrity': 'Billy Ray Cyrus', 'description': '5th place despite last place judge scores in 6 weeks'},
        {'season': 11, 'celebrity': 'Bristol Palin', 'description': '3rd place with lowest judge scores 12 times'},
        {'season': 27, 'celebrity': 'Bobby Bones', 'description': 'Won despite consistently low judge scores'}
    ]
    
    for case in controversial_cases:
        print(f"\n--- {case['celebrity']} (Season {case['season']}) ---")
        print(f"Description: {case['description']}")
        
        # Get data for this celebrity
        celebrity_data = df[
            (df['season'] == case['season']) & 
            (df['celebrity_name'] == case['celebrity'])
        ]
        
        if len(celebrity_data) == 0:
            print("Data not found")
            continue
        
        result = celebrity_data.iloc[0]['results']
        placement = celebrity_data.iloc[0]['placement']
        
        print(f"Actual result: {result} (Placement: {placement})")
        
        # Analyze their judge scores vs competition
        season_data = df[df['season'] == case['season']]
        
        # Count weeks with lowest judge scores
        weeks_lowest = 0
        for week in range(1, 12):
            week_scores = []
            for idx, row in season_data.iterrows():
                score_cols = [f'week{week}_judge{j}_score' for j in range(1, 5)]
                contestant_score = 0
                for col in score_cols:
                    if col in row and pd.notna(row[col]) and row[col] not in ['N/A', 0]:
                        try:
                            contestant_score += float(row[col])
                        except:
                            pass
                if contestant_score > 0:
                    week_scores.append({
                        'celebrity': row['celebrity_name'],
                        'score': contestant_score
                    })
            
            if len(week_scores) > 0:
                min_score = min([s['score'] for s in week_scores])
                celebrity_score = [s['score'] for s in week_scores if s['celebrity'] == case['celebrity']]
                if len(celebrity_score) > 0 and celebrity_score[0] == min_score:
                    weeks_lowest += 1
        
        print(f"Weeks with lowest judge scores: {weeks_lowest}")
        
        # Analyze fan vote estimates
        celebrity_fan_votes = fan_votes[
            (fan_votes['season'] == case['season']) & 
            (fan_votes['contestant'] == case['celebrity'])
        ]
        
        if len(celebrity_fan_votes) > 0:
            avg_fan_votes = celebrity_fan_votes['estimated_fan_votes'].mean()
            print(f"Average estimated fan votes: {avg_fan_votes:,.0f}")
            
            # Compare to other contestants
            season_avg = fan_votes[fan_votes['season'] == case['season']]['estimated_fan_votes'].mean()
            print(f"Season average fan votes: {season_avg:,.0f}")
            print(f"Relative fan support: {avg_fan_votes/season_avg:.2f}x average")


def simulate_judge_elimination_method(df, fan_votes):
    """
    Simulate the season 28+ method where judges choose between bottom 2
    """
    if fan_votes is None:
        print("Cannot simulate without fan vote estimates")
        return None
    
    print("\n" + "="*60)
    print("Judge Elimination from Bottom 2 Analysis")
    print("="*60)
    
    changed_outcomes = []
    
    for season in sorted(fan_votes['season'].unique()):
        for week in sorted(fan_votes[fan_votes['season'] == season]['week'].unique()):
            week_data = fan_votes[
                (fan_votes['season'] == season) & 
                (fan_votes['week'] == week)
            ].copy()
            
            if len(week_data) < 2:
                continue
            
            contestants = week_data['contestant'].tolist()
            judge_scores = week_data['judge_score'].tolist()
            fan_vote_estimates = week_data['estimated_fan_votes'].tolist()
            
            # Find bottom 2 by combined method
            rank_result = apply_rank_method(judge_scores, fan_vote_estimates)
            
            if rank_result:
                combined_ranks = rank_result['combined_ranks']
                
                # Get indices of bottom 2 (highest combined ranks)
                bottom_2_indices = sorted(range(len(combined_ranks)), 
                                        key=lambda i: combined_ranks[i], 
                                        reverse=True)[:2]
                
                # Judges would likely eliminate the one with lower judge score
                bottom_2_judge_scores = [judge_scores[i] for i in bottom_2_indices]
                judge_choice_idx = bottom_2_indices[np.argmin(bottom_2_judge_scores)]
                
                # Compare to standard elimination
                standard_elimination_idx = rank_result['eliminated_idx']
                
                if judge_choice_idx != standard_elimination_idx:
                    changed_outcomes.append({
                        'season': season,
                        'week': week,
                        'standard_elimination': contestants[standard_elimination_idx],
                        'judge_choice': contestants[judge_choice_idx],
                        'bottom_2': [contestants[i] for i in bottom_2_indices]
                    })
    
    print(f"\nWeeks where judge choice would differ from standard: {len(changed_outcomes)}")
    
    if len(changed_outcomes) > 0:
        print("\nExamples of changed outcomes:")
        for outcome in changed_outcomes[:5]:
            print(f"  Season {outcome['season']}, Week {outcome['week']}:")
            print(f"    Standard: {outcome['standard_elimination']}")
            print(f"    Judge choice: {outcome['judge_choice']}")
            print(f"    Bottom 2: {outcome['bottom_2']}")
    
    return changed_outcomes


def main():
    """Main execution function"""
    print("="*60)
    print("Question 2: Voting Method Comparison")
    print("="*60)
    
    # Load data
    df, fan_votes = load_data()
    
    if fan_votes is None:
        print("\nPlease run question1_fan_vote_estimation.py first!")
        return
    
    # Compare methods across seasons
    comparison_results = compare_methods_across_seasons(df, fan_votes)
    
    if comparison_results is not None:
        comparison_results.to_csv('question2_method_comparison.csv', index=False)
        print("\nSaved method comparison to 'question2_method_comparison.csv'")
    
    # Analyze controversial cases
    analyze_controversial_cases(df, fan_votes)
    
    # Simulate judge elimination method
    changed_outcomes = simulate_judge_elimination_method(df, fan_votes)
    
    if changed_outcomes:
        pd.DataFrame(changed_outcomes).to_csv('question2_judge_elimination_impact.csv', index=False)
        print("\nSaved judge elimination impact to 'question2_judge_elimination_impact.csv'")
    
    print("\n✓ Question 2 complete!")


if __name__ == "__main__":
    main()
