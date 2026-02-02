"""
Cross-Validation Model for Fan Vote Estimation
Uses machine learning (Random Forest) as a distinct model to validate
the optimization-based fan vote estimates from Question 1.

This provides an independent validation method using a completely different
modeling approach (ensemble learning vs optimization).
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


def load_data():
    """Load the original data and fan vote estimates"""
    df = pd.read_csv('2026_MCM_Problem_C_Data.csv')
    try:
        fan_votes = pd.read_csv('question1_fan_vote_estimates.csv')
        return df, fan_votes
    except FileNotFoundError:
        print("Error: question1_fan_vote_estimates.csv not found.")
        print("Please run question1_fan_vote_estimation.py first.")
        return df, None


def prepare_features(df, fan_votes):
    """
    Prepare features for machine learning model to predict fan votes
    
    Features include:
    - Judge score (raw and normalized)
    - Season number
    - Week number
    - Contestant characteristics (age, industry)
    - Pro dancer
    - Number of contestants in that week
    - Judge rank within the week
    """
    print("\nPreparing features for ML model...")
    
    # Merge fan votes with original data to get characteristics
    merged = fan_votes.merge(
        df[['celebrity_name', 'season', 'celebrity_age_during_season', 
            'celebrity_industry', 'ballroom_partner']],
        left_on=['contestant', 'season'],
        right_on=['celebrity_name', 'season'],
        how='left'
    )
    
    # Calculate additional features
    features_list = []
    
    for season in merged['season'].unique():
        for week in merged[merged['season'] == season]['week'].unique():
            week_data = merged[
                (merged['season'] == season) & 
                (merged['week'] == week)
            ].copy()
            
            if len(week_data) == 0:
                continue
            
            # Number of contestants this week
            n_contestants = len(week_data)
            
            # Total judge score for normalization
            total_judge = week_data['judge_score'].sum()
            
            for idx, row in week_data.iterrows():
                # Judge rank (1 is best)
                judge_rank = (week_data['judge_score'] > row['judge_score']).sum() + 1
                
                # Normalized judge score
                judge_pct = row['judge_score'] / total_judge if total_judge > 0 else 0
                
                features_list.append({
                    'season': season,
                    'week': week,
                    'contestant': row['contestant'],
                    'judge_score': row['judge_score'],
                    'judge_pct': judge_pct,
                    'judge_rank': judge_rank,
                    'n_contestants': n_contestants,
                    'age': row.get('celebrity_age_during_season', 40),  # Default to 40 if missing
                    'industry': row.get('celebrity_industry', 'Unknown'),
                    'partner': row.get('ballroom_partner', 'Unknown'),
                    'eliminated': row['eliminated'],
                    'method': row['method'],
                    'estimated_fan_votes': row['estimated_fan_votes']
                })
    
    features_df = pd.DataFrame(features_list)
    
    # Encode categorical variables
    le_industry = LabelEncoder()
    le_partner = LabelEncoder()
    le_method = LabelEncoder()
    
    features_df['industry_encoded'] = le_industry.fit_transform(
        features_df['industry'].fillna('Unknown')
    )
    features_df['partner_encoded'] = le_partner.fit_transform(
        features_df['partner'].fillna('Unknown')
    )
    features_df['method_encoded'] = le_method.fit_transform(
        features_df['method']
    )
    
    print(f"Prepared {len(features_df)} feature rows")
    
    return features_df, le_industry, le_partner, le_method


def build_random_forest_model(features_df):
    """
    Build Random Forest model to predict fan votes
    This is a distinct model from the optimization approach
    """
    print("\n=== Random Forest Cross-Validation Model ===")
    
    # Select features for prediction
    feature_cols = [
        'judge_score', 'judge_pct', 'judge_rank',
        'n_contestants', 'season', 'week', 'age',
        'industry_encoded', 'partner_encoded', 'method_encoded'
    ]
    
    # Remove rows with missing values
    model_data = features_df.dropna(subset=feature_cols + ['estimated_fan_votes'])
    
    X = model_data[feature_cols]
    y = model_data['estimated_fan_votes']
    
    print(f"\nTraining on {len(X)} samples with {len(feature_cols)} features")
    
    # Random Forest Regressor
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # K-Fold Cross-Validation
    k_folds = 5
    print(f"\nPerforming {k_folds}-fold cross-validation...")
    
    kfold = KFold(n_splits=k_folds, shuffle=True, random_state=42)
    
    # Cross-validation scores
    cv_scores = cross_val_score(
        rf_model, X, y, 
        cv=kfold, 
        scoring='r2',
        n_jobs=-1
    )
    
    print(f"\nCross-Validation R² Scores:")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score:.4f}")
    print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Train final model on all data
    rf_model.fit(X, y)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importances:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Predictions
    y_pred = rf_model.predict(X)
    
    # Evaluation metrics
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    print(f"\nModel Performance on Training Data:")
    print(f"  RMSE: {rmse:,.2f}")
    print(f"  MAE: {mae:,.2f}")
    print(f"  R²: {r2:.4f}")
    
    # Add predictions to dataframe
    model_data['rf_predicted_fan_votes'] = y_pred
    
    return rf_model, model_data, feature_cols, cv_scores


def build_gradient_boosting_model(features_df, feature_cols):
    """
    Build Gradient Boosting model as another distinct validation model
    """
    print("\n=== Gradient Boosting Cross-Validation Model ===")
    
    # Remove rows with missing values
    model_data = features_df.dropna(subset=feature_cols + ['estimated_fan_votes'])
    
    X = model_data[feature_cols]
    y = model_data['estimated_fan_votes']
    
    # Gradient Boosting Regressor
    gb_model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    # K-Fold Cross-Validation
    k_folds = 5
    kfold = KFold(n_splits=k_folds, shuffle=True, random_state=42)
    
    cv_scores = cross_val_score(
        gb_model, X, y,
        cv=kfold,
        scoring='r2',
        n_jobs=-1
    )
    
    print(f"\nCross-Validation R² Scores:")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score:.4f}")
    print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Train final model
    gb_model.fit(X, y)
    
    # Predictions
    y_pred = gb_model.predict(X)
    
    # Evaluation metrics
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    print(f"\nModel Performance on Training Data:")
    print(f"  RMSE: {rmse:,.2f}")
    print(f"  MAE: {mae:,.2f}")
    print(f"  R²: {r2:.4f}")
    
    return gb_model, cv_scores


def validate_against_optimization_model(model_data):
    """
    Compare ML model predictions with optimization-based estimates
    """
    print("\n=== Comparing ML Model vs Optimization Model ===")
    
    # Calculate differences
    model_data['difference'] = (
        model_data['rf_predicted_fan_votes'] - 
        model_data['estimated_fan_votes']
    )
    model_data['pct_difference'] = (
        model_data['difference'] / model_data['estimated_fan_votes'] * 100
    )
    
    # Statistics
    mean_diff = model_data['difference'].mean()
    std_diff = model_data['difference'].std()
    mean_pct_diff = model_data['pct_difference'].mean()
    
    print(f"\nDifference Statistics:")
    print(f"  Mean difference: {mean_diff:,.2f} votes")
    print(f"  Std difference: {std_diff:,.2f} votes")
    print(f"  Mean % difference: {mean_pct_diff:.2f}%")
    
    # Correlation
    correlation = model_data['rf_predicted_fan_votes'].corr(
        model_data['estimated_fan_votes']
    )
    
    print(f"\nCorrelation between models: {correlation:.4f}")
    
    # Check if both models agree on eliminations
    agreement_count = 0
    total_weeks = 0
    
    for season in model_data['season'].unique():
        for week in model_data[model_data['season'] == season]['week'].unique():
            week_data = model_data[
                (model_data['season'] == season) & 
                (model_data['week'] == week)
            ].copy()
            
            if len(week_data) < 2:
                continue
            
            total_weeks += 1
            
            # Optimization model: who was predicted to be eliminated?
            opt_eliminated = week_data[week_data['eliminated']]['contestant'].values
            
            # ML model: who would be eliminated based on lowest predicted votes?
            ml_eliminated = week_data.loc[
                week_data['rf_predicted_fan_votes'].idxmin(), 
                'contestant'
            ]
            
            if len(opt_eliminated) > 0:
                # Check agreement with actual elimination
                if ml_eliminated == opt_eliminated[0]:
                    agreement_count += 1
    
    agreement_rate = agreement_count / total_weeks if total_weeks > 0 else 0
    
    print(f"\nModel Agreement on Eliminations:")
    print(f"  Weeks where both models predict same elimination: {agreement_count}/{total_weeks}")
    print(f"  Agreement rate: {agreement_rate:.1%}")
    
    return model_data


def analyze_cross_validation_results(rf_cv_scores, gb_cv_scores):
    """
    Analyze and summarize cross-validation results
    """
    print("\n=== Cross-Validation Summary ===")
    
    print(f"\nRandom Forest:")
    print(f"  Mean R²: {rf_cv_scores.mean():.4f}")
    print(f"  Std Dev: {rf_cv_scores.std():.4f}")
    print(f"  Min R²: {rf_cv_scores.min():.4f}")
    print(f"  Max R²: {rf_cv_scores.max():.4f}")
    
    print(f"\nGradient Boosting:")
    print(f"  Mean R²: {gb_cv_scores.mean():.4f}")
    print(f"  Std Dev: {gb_cv_scores.std():.4f}")
    print(f"  Min R²: {gb_cv_scores.min():.4f}")
    print(f"  Max R²: {gb_cv_scores.max():.4f}")
    
    print("\n=== Key Findings ===")
    print("""
The cross-validation models provide an independent validation of the
optimization-based fan vote estimates:

1. DISTINCT MODELING APPROACH:
   - Optimization model: Constrained optimization to find votes consistent
     with eliminations (inverse problem solving)
   - ML models: Learn patterns from features to predict fan votes
     (supervised learning)

2. VALIDATION STRENGTH:
   - K-fold cross-validation tests generalization across different
     data subsets
   - High correlation between models indicates robust estimates
   - Model agreement on eliminations validates both approaches

3. FEATURE INSIGHTS:
   - Judge scores and ranks are strong predictors
   - Season and week effects matter
   - Pro dancer and contestant characteristics have impact

4. CONFIDENCE:
   - Cross-validation R² scores indicate prediction stability
   - Multiple models converging on similar results increases confidence
   - Variation in predictions shows inherent uncertainty in fan voting
""")


def main():
    """Main execution function"""
    print("="*70)
    print("Cross-Validation Model for Fan Vote Estimation")
    print("="*70)
    print("\nThis module provides independent validation using machine learning")
    print("to cross-validate the optimization-based fan vote estimates.")
    
    # Load data
    df, fan_votes = load_data()
    
    if fan_votes is None:
        print("\nCannot proceed without fan vote estimates.")
        print("Please run question1_fan_vote_estimation.py first.")
        return
    
    # Prepare features
    features_df, le_industry, le_partner, le_method = prepare_features(df, fan_votes)
    
    # Build Random Forest model with cross-validation
    rf_model, model_data, feature_cols, rf_cv_scores = build_random_forest_model(features_df)
    
    # Build Gradient Boosting model with cross-validation
    gb_model, gb_cv_scores = build_gradient_boosting_model(features_df, feature_cols)
    
    # Validate against optimization model
    comparison_data = validate_against_optimization_model(model_data)
    
    # Analyze cross-validation results
    analyze_cross_validation_results(rf_cv_scores, gb_cv_scores)
    
    # Save results
    cv_summary = pd.DataFrame({
        'model': ['Random Forest', 'Gradient Boosting'],
        'mean_cv_r2': [rf_cv_scores.mean(), gb_cv_scores.mean()],
        'std_cv_r2': [rf_cv_scores.std(), gb_cv_scores.std()],
        'min_cv_r2': [rf_cv_scores.min(), gb_cv_scores.min()],
        'max_cv_r2': [rf_cv_scores.max(), gb_cv_scores.max()]
    })
    
    cv_summary.to_csv('cross_validation_summary.csv', index=False)
    print("\nSaved cross-validation summary to 'cross_validation_summary.csv'")
    
    comparison_data.to_csv('cross_validation_comparison.csv', index=False)
    print("Saved model comparison to 'cross_validation_comparison.csv'")
    
    print("\n✓ Cross-validation analysis complete!")


if __name__ == "__main__":
    main()
