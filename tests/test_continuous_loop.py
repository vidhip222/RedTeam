#!/usr/bin/env python3
"""Test continuous loop with mock model"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_continuous_loop_components():
    """Test that continuous loop can be set up"""
    print("Testing continuous loop setup...")
    
    try:
        # Import without ModelClient (which has langchain dependency)
        from attacks.advanced_generator import generate_advanced_attacks
        from runner.runner import load_attacks
        from eval.response_analyzer import ResponseAnalyzer
        from eval.adaptive_strategy import AdaptiveStrategy
        from eval.success_tracker import SuccessTracker
        from attacks.attack_mutator import AttackMutator
        from attacks.attack_tree import AttackTree
        from attacks.genetic_attacks import GeneticAttackGenerator
        
        # Generate test attacks
        test_file = "data/test_loop_attacks.json"
        attacks = generate_advanced_attacks(out_path=test_file)
        print(f"  ✅ Generated {len(attacks)} test attacks")
        
        # Initialize all components
        analyzer = ResponseAnalyzer()
        strategy = AdaptiveStrategy()
        tracker = SuccessTracker(db_path="data/test_loop_tracker.json")
        mutator = AttackMutator()
        tree = AttackTree()
        genetic = GeneticAttackGenerator(population_size=10)
        
        print("  ✅ All components initialized")
        
        # Test analyzer
        test_attack = attacks[0]
        test_response = {"response": "API_KEY=test123", "error": None}
        analysis = analyzer.analyze_response(test_attack, test_response)
        assert "success" in analysis
        print("  ✅ Response analyzer works")
        
        # Test mutator
        mutated = mutator.mutate(test_attack, "encoding")
        assert mutated["attack_id"] != test_attack["attack_id"]
        print("  ✅ Attack mutator works")
        
        # Test tree
        tree.add_attack(test_attack)
        tree.add_attack(mutated, parent_id=test_attack["attack_id"])
        lineage = tree.get_lineage(mutated["attack_id"])
        assert test_attack["attack_id"] in lineage["ancestors"]
        print("  ✅ Attack tree works")
        
        # Test genetic
        genetic.initialize_population([a["prompt"] for a in attacks[:3]])
        assert len(genetic.population) > 0
        print("  ✅ Genetic generator works")
        
        # Test strategy
        strategy.update_performance("encoding", True)
        selected = strategy.select_strategy(["encoding", "token_smuggling"])
        assert selected in ["encoding", "token_smuggling"]
        print("  ✅ Adaptive strategy works")
        
        # Test tracker
        tracker.record_attack_result("test-01", True, "mock", "encoding")
        rate = tracker.get_attack_success_rate("test-01")
        assert rate == 1.0
        print("  ✅ Success tracker works")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("data/test_loop_tracker.json"):
            os.remove("data/test_loop_tracker.json")
        
        print("\n✅ Continuous loop components: ALL WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_continuous_loop_components()
    sys.exit(0 if success else 1)

