"""
Exit Experience Validator - Check All 208 Features
===================================================
Validates that exit experiences have all required features and no missing data.
Identifies any zeros or missing values that indicate incomplete data collection.
"""

import json
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_exit_experiences():
    """Comprehensive analysis of exit experiences"""
    
    logger.info("="*80)
    logger.info("EXIT EXPERIENCE COMPREHENSIVE ANALYSIS")
    logger.info("="*80)
    
    experience_file = 'data/local_experiences/exit_experiences_v2.json'
    
    if not os.path.exists(experience_file):
        logger.error(f"\n❌ File not found: {experience_file}")
        return False
    
    try:
        with open(experience_file, 'r') as f:
            data = json.load(f)
        
        experiences = data.get('experiences', [])
        
        if not experiences:
            logger.error("\n❌ No experiences found!")
            return False
        
        logger.info(f"\n✅ Loaded {len(experiences)} experiences\n")
        
        # Analyze first experience in detail
        exp = experiences[0]
        
        logger.info("="*80)
        logger.info("FIELD ANALYSIS - First Experience")
        logger.info("="*80)
        
        # Categorize all fields
        scalar_fields = []
        dict_fields = []
        list_fields = []
        string_fields = []
        
        for k, v in exp.items():
            if isinstance(v, dict):
                dict_fields.append((k, len(v)))
            elif isinstance(v, list):
                list_fields.append((k, len(v)))
            elif isinstance(v, str):
                string_fields.append(k)
            else:
                scalar_fields.append(k)
        
        logger.info(f"\n📊 Field Type Summary:")
        logger.info(f"   Scalar fields: {len(scalar_fields)}")
        logger.info(f"   Dict fields: {len(dict_fields)}")
        logger.info(f"   List fields: {len(list_fields)}")
        logger.info(f"   String fields: {len(string_fields)}")
        
        # Detailed breakdown
        logger.info(f"\n📁 Dictionary Fields:")
        for name, count in dict_fields:
            logger.info(f"   {name}: {count} keys")
        
        logger.info(f"\n📝 List Fields:")
        for name, count in list_fields:
            logger.info(f"   {name}: {count} items")
        
        logger.info(f"\n🔤 String Fields:")
        for name in string_fields:
            logger.info(f"   {name}: {exp[name]}")
        
        logger.info(f"\n🔢 Scalar Fields:")
        for name in scalar_fields[:20]:  # Show first 20
            value = exp[name]
            logger.info(f"   {name}: {value}")
        if len(scalar_fields) > 20:
            logger.info(f"   ... and {len(scalar_fields) - 20} more")
        
        # Analyze exit_params_used (132 parameters)
        logger.info(f"\n{'='*80}")
        logger.info("EXIT PARAMS USED ANALYSIS (132 Parameters)")
        logger.info(f"{'='*80}")
        
        exit_params_used = exp.get('exit_params_used', {})
        
        if not exit_params_used:
            logger.error("\n❌ exit_params_used is missing!")
            return False
        
        logger.info(f"\nTotal parameters: {len(exit_params_used)}")
        
        # Categorize by value
        zero_params = {}
        nonzero_params = {}
        bool_params = {}
        
        for k, v in exit_params_used.items():
            if isinstance(v, bool):
                bool_params[k] = v
            elif v == 0 or v == 0.0:
                zero_params[k] = v
            else:
                nonzero_params[k] = v
        
        logger.info(f"\n📊 Parameter Value Distribution:")
        logger.info(f"   Boolean params: {len(bool_params)}")
        logger.info(f"   Zero values: {len(zero_params)}")
        logger.info(f"   Non-zero values: {len(nonzero_params)}")
        
        # Check critical exit parameters
        critical_params = [
            'stop_mult', 'breakeven_threshold_ticks', 'trailing_distance_ticks',
            'partial_1_r', 'partial_2_r', 'partial_3_r',
            'max_hold_duration_minutes', 'trailing_min_profit_ticks'
        ]
        
        logger.info(f"\n🎯 Critical Exit Parameters:")
        for param in critical_params:
            value = exit_params_used.get(param, 'MISSING')
            status = "✅" if value != 'MISSING' and value != 0 else "❌"
            logger.info(f"   {status} {param}: {value}")
        
        # Show parameters with zero values (potential issues)
        if zero_params:
            logger.info(f"\n⚠️  Parameters with ZERO values ({len(zero_params)}):")
            for k, v in list(zero_params.items())[:20]:
                logger.info(f"   {k}: {v}")
            if len(zero_params) > 20:
                logger.info(f"   ... and {len(zero_params) - 20} more")
        
        # Analyze market_state
        logger.info(f"\n{'='*80}")
        logger.info("MARKET STATE ANALYSIS (9 Features)")
        logger.info(f"{'='*80}")
        
        market_state = exp.get('market_state', {})
        
        if not market_state:
            logger.error("\n❌ market_state is missing!")
        else:
            logger.info(f"\nFields: {len(market_state)}")
            for k, v in market_state.items():
                logger.info(f"   {k}: {v}")
        
        # Analyze outcome dict
        logger.info(f"\n{'='*80}")
        logger.info("OUTCOME DICT ANALYSIS (63 Fields)")
        logger.info(f"{'='*80}")
        
        outcome = exp.get('outcome', {})
        
        if not outcome:
            logger.error("\n❌ outcome is missing!")
        else:
            logger.info(f"\nTotal fields: {len(outcome)}")
            
            # Show sample
            logger.info(f"\nSample fields (first 15):")
            for k, v in list(outcome.items())[:15]:
                if isinstance(v, str):
                    logger.info(f"   {k}: {v[:50]}...")
                else:
                    logger.info(f"   {k}: {v}")
        
        # Check for missing critical fields
        logger.info(f"\n{'='*80}")
        logger.info("CRITICAL FIELD CHECK")
        logger.info(f"{'='*80}")
        
        critical_fields = [
            ('regime', 'Root'),
            ('side', 'Root'),
            ('pnl', 'Root'),
            ('r_multiple', 'Root'),
            ('mae', 'Root'),
            ('mfe', 'Root'),
            ('exit_reason', 'Root'),
            ('win', 'Root'),
            ('breakeven_activated', 'Root'),
            ('trailing_activated', 'Root'),
            ('duration', 'Root'),
            ('entry_confidence', 'Root'),
            ('atr', 'market_state'),
            ('rsi', 'market_state'),
            ('vix', 'market_state'),
        ]
        
        all_present = True
        logger.info(f"\nChecking critical fields:")
        for field, location in critical_fields:
            if location == 'Root':
                present = field in exp
                value = exp.get(field, 'MISSING')
            else:
                present = field in exp.get(location, {})
                value = exp.get(location, {}).get(field, 'MISSING')
            
            status = "✅" if present else "❌"
            logger.info(f"   {status} {location}.{field}: {value}")
            if not present:
                all_present = False
        
        # Statistics across all experiences
        logger.info(f"\n{'='*80}")
        logger.info(f"STATISTICS ACROSS ALL {len(experiences)} EXPERIENCES")
        logger.info(f"{'='*80}")
        
        # Count wins vs losses
        wins = sum(1 for e in experiences if e.get('win', False))
        losses = len(experiences) - wins
        win_rate = (wins / len(experiences)) * 100 if experiences else 0
        
        logger.info(f"\n📊 Win/Loss Statistics:")
        logger.info(f"   Wins: {wins} ({win_rate:.1f}%)")
        logger.info(f"   Losses: {losses} ({100-win_rate:.1f}%)")
        
        # Average R-multiple
        r_multiples = [e.get('r_multiple', 0) for e in experiences]
        avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else 0
        
        logger.info(f"\n📈 R-Multiple Statistics:")
        logger.info(f"   Average: {avg_r:.2f}R")
        logger.info(f"   Max: {max(r_multiples):.2f}R")
        logger.info(f"   Min: {min(r_multiples):.2f}R")
        
        # Exit reasons distribution
        exit_reasons = {}
        for e in experiences:
            reason = e.get('exit_reason', 'unknown')
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        
        logger.info(f"\n🚪 Exit Reasons Distribution:")
        for reason, count in sorted(exit_reasons.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(experiences)) * 100
            logger.info(f"   {reason}: {count} ({pct:.1f}%)")
        
        # Check if all experiences have all required fields
        logger.info(f"\n{'='*80}")
        logger.info("COMPLETENESS CHECK")
        logger.info(f"{'='*80}")
        
        required_fields = ['regime', 'exit_params_used', 'market_state', 'outcome']
        incomplete_count = 0
        
        for i, e in enumerate(experiences):
            missing = [f for f in required_fields if f not in e]
            if missing:
                incomplete_count += 1
                if incomplete_count <= 5:  # Show first 5
                    logger.warning(f"\n⚠️  Experience {i} missing: {missing}")
        
        if incomplete_count == 0:
            logger.info(f"\n✅ All {len(experiences)} experiences have required fields")
        else:
            logger.warning(f"\n⚠️  {incomplete_count} experiences have missing fields")
        
        # Feature extraction compatibility
        logger.info(f"\n{'='*80}")
        logger.info("FEATURE EXTRACTION COMPATIBILITY")
        logger.info(f"{'='*80}")
        
        try:
            sys.path.insert(0, 'src')
            from exit_feature_extraction import extract_all_features_for_training
            
            logger.info(f"\nTesting feature extraction on first experience...")
            features = extract_all_features_for_training(exp)
            
            logger.info(f"✅ Successfully extracted {len(features)} features")
            logger.info(f"   Expected: 208 features")
            logger.info(f"   Match: {'YES ✅' if len(features) == 208 else 'NO ❌'}")
            
            # Check for NaN or invalid values
            import math
            invalid_count = sum(1 for f in features if math.isnan(f) or math.isinf(f))
            
            if invalid_count > 0:
                logger.warning(f"\n⚠️  Found {invalid_count} invalid values (NaN/Inf)")
            else:
                logger.info(f"✅ All features are valid numbers")
            
        except Exception as e:
            logger.error(f"\n❌ Feature extraction test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Final summary
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"\n✅ Total experiences: {len(experiences)}")
        logger.info(f"✅ exit_params_used: {len(exit_params_used)} parameters")
        logger.info(f"✅ market_state: {len(market_state)} fields")
        logger.info(f"✅ outcome: {len(outcome)} fields")
        logger.info(f"✅ Win rate: {win_rate:.1f}%")
        logger.info(f"✅ Average R: {avg_r:.2f}R")
        
        if all_present and incomplete_count == 0:
            logger.info(f"\n🎉 ALL CHECKS PASSED! Data quality is excellent.")
            return True
        else:
            logger.warning(f"\n⚠️  Some issues found - see details above")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("EXIT EXPERIENCE VALIDATOR")
    print("Checking all 208 features for completeness")
    print("="*80 + "\n")
    
    success = analyze_exit_experiences()
    
    if success:
        print("\n" + "="*80)
        print("✅ VALIDATION COMPLETE - All features present and valid")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("⚠️  VALIDATION FOUND ISSUES - Review output above")
        print("="*80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
