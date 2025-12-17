# runner/continuous_loop.py
"""Continuous red-teaming loop with autonomous improvement"""
import json
import os
from typing import List, Dict
from attacks.attack_mutator import AttackMutator
from attacks.attack_tree import AttackTree
from attacks.genetic_attacks import GeneticAttackGenerator
from eval.response_analyzer import ResponseAnalyzer
from eval.adaptive_strategy import AdaptiveStrategy
from eval.success_tracker import SuccessTracker
from runner.runner import load_attacks, run_all
from models.client import ModelClient

class ContinuousRedTeamLoop:
    """Autonomous red-teaming loop that improves over time"""
    
    def __init__(self, model_client: ModelClient, max_iterations: int = 10):
        self.model_client = model_client
        self.max_iterations = max_iterations
        
        # Initialize components
        self.analyzer = ResponseAnalyzer(model_client)
        self.mutator = AttackMutator()
        self.attack_tree = AttackTree()
        self.adaptive_strategy = AdaptiveStrategy()
        self.success_tracker = SuccessTracker()
        self.genetic_generator = GeneticAttackGenerator()
        
        self.current_attacks = []
        self.successful_attacks = []
        self.iteration = 0
    
    def run_iteration(self, attacks: List[Dict], out_path: str = "data/results.jsonl") -> Dict:
        """Run one iteration of the red-teaming loop"""
        self.iteration += 1
        print(f"\n=== Iteration {self.iteration}/{self.max_iterations} ===")
        
        # 1. Execute attacks
        print(f"Executing {len(attacks)} attacks...")
        results = run_all(attacks, self.model_client, out_path=out_path)
        
        # 2. Analyze responses
        print("Analyzing responses...")
        analyses = self.analyzer.batch_analyze(attacks, results)
        
        # 3. Identify successful attacks
        successful = []
        for attack, analysis in zip(attacks, analyses):
            if analysis["success"]:
                successful.append(attack)
                # Update attack tree
                self.attack_tree.add_attack(attack)
                self.attack_tree.update_success_rate(
                    attack["attack_id"],
                    analysis["confidence"]
                )
                # Track success
                strategy = attack.get("metadata", {}).get("source", "unknown")
                self.success_tracker.record_attack_result(
                    attack["attack_id"],
                    True,
                    self.model_client.provider,
                    strategy
                )
            else:
                strategy = attack.get("metadata", {}).get("source", "unknown")
                self.success_tracker.record_attack_result(
                    attack["attack_id"],
                    False,
                    self.model_client.provider,
                    strategy
                )
        
        self.successful_attacks.extend(successful)
        
        # 4. Detect defense patterns
        print("Detecting defense patterns...")
        defense_patterns = self.adaptive_strategy.detect_defense_pattern(results)
        print(f"Defense patterns: {defense_patterns}")
        
        # 5. Generate new attacks
        new_attacks = []
        
        # From successful attacks (mutation)
        if successful:
            print(f"Mutating {len(successful)} successful attacks...")
            mutated = self.mutator.evolve_from_successful(successful, num_new=10)
            for attack in mutated:
                self.attack_tree.add_attack(attack, parent_id=successful[0]["attack_id"])
            new_attacks.extend(mutated)
        
        # From genetic algorithm
        if self.iteration == 1:
            # Initialize genetic population
            base_prompts = [a["prompt"] for a in attacks[:5]]
            self.genetic_generator.initialize_population(base_prompts)
        else:
            # Evolve population
            print("Evolving attack population...")
            evolved = self.genetic_generator.evolve(results[:len(self.genetic_generator.population)])
            best_attacks = self.genetic_generator.get_best_attacks(n=5)
            for i, prompt in enumerate(best_attacks):
                new_attacks.append({
                    "attack_id": f"genetic-iter{self.iteration}-{i}",
                    "prompt": prompt,
                    "tags": ["genetic", f"generation_{self.iteration}"],
                    "metadata": {"source": "genetic", "generation": self.iteration}
                })
        
        # 6. Select strategy for next iteration
        available_strategies = [
            "encoding", "token_smuggling", "semantic_evasion",
            "context_wrap", "multiturn", "fewshot", "multilingual"
        ]
        next_strategy = self.adaptive_strategy.select_strategy(available_strategies)
        print(f"Selected strategy for next iteration: {next_strategy}")
        
        # 7. Summary
        success_rate = len(successful) / len(attacks) if attacks else 0.0
        print(f"\nIteration {self.iteration} Summary:")
        print(f"  Total attacks: {len(attacks)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  New attacks generated: {len(new_attacks)}")
        
        return {
            "iteration": self.iteration,
            "attacks_tested": len(attacks),
            "successful": len(successful),
            "success_rate": success_rate,
            "new_attacks": len(new_attacks),
            "defense_patterns": defense_patterns,
            "next_strategy": next_strategy,
        }
    
    def run_continuous_loop(self, initial_attacks: List[Dict], out_dir: str = "data"):
        """Run full continuous loop"""
        current_attacks = initial_attacks.copy()
        iteration_results = []
        
        for iteration in range(self.max_iterations):
            out_path = os.path.join(out_dir, f"results_iter{iteration+1}.jsonl")
            result = self.run_iteration(current_attacks, out_path)
            iteration_results.append(result)
            
            # Prepare next iteration attacks
            if iteration < self.max_iterations - 1:
                # Mix successful attacks with new mutations
                next_attacks = []
                
                # Top successful attacks
                top_successful = self.success_tracker.get_top_attacks(n=5)
                for top in top_successful:
                    attack_id = top["attack_id"]
                    # Find original attack
                    for attack in self.successful_attacks:
                        if attack["attack_id"] == attack_id:
                            # Generate variants
                            variants = self.mutator.generate_variants(attack, num_variants=2)
                            next_attacks.extend(variants)
                
                # Add some new genetic attacks
                if self.genetic_generator.population:
                    best = self.genetic_generator.get_best_attacks(n=3)
                    for i, prompt in enumerate(best):
                        next_attacks.append({
                            "attack_id": f"genetic-next-{i}",
                            "prompt": prompt,
                            "tags": ["genetic"],
                            "metadata": {"source": "genetic"}
                        })
                
                # Add some random new attacks
                if len(next_attacks) < 10:
                    # Use some from initial set
                    next_attacks.extend(initial_attacks[:10-len(next_attacks)])
                
                current_attacks = next_attacks[:20]  # Limit to 20 per iteration
        
        # Final summary
        print("\n" + "="*50)
        print("CONTINUOUS LOOP COMPLETE")
        print("="*50)
        print(f"Total iterations: {self.max_iterations}")
        print(f"Total successful attacks found: {len(self.successful_attacks)}")
        
        top_attacks = self.success_tracker.get_top_attacks(n=10)
        print("\nTop 10 Most Successful Attacks:")
        for i, attack in enumerate(top_attacks, 1):
            print(f"  {i}. {attack['attack_id']}: {attack['success_rate']:.2%} ({attack['success']}/{attack['total']})")
        
        top_strategies = self.success_tracker.get_top_strategies(n=5)
        print("\nTop 5 Most Successful Strategies:")
        for i, strat in enumerate(top_strategies, 1):
            print(f"  {i}. {strat['strategy']}: {strat['success_rate']:.2%} ({strat['success']}/{strat['total']})")
        
        # Save final results
        summary_path = os.path.join(out_dir, "continuous_loop_summary.json")
        with open(summary_path, "w") as f:
            json.dump({
                "iterations": iteration_results,
                "top_attacks": top_attacks,
                "top_strategies": top_strategies,
                "attack_tree": self.attack_tree.to_dict(),
            }, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")
        
        return iteration_results




