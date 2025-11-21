# attacks/attack_mutator.py
"""Automatically generates variations of successful attacks"""
import random
from typing import List, Dict
from attacks.encoding_attacks import apply_encoding_attack
from attacks.token_smuggling import apply_token_smuggling
from attacks.semantic_evasion import apply_semantic_evasion
from attacks.context_attacks import apply_context_attack
from attacks.multiturn_attacks import apply_multiturn_attack
from attacks.fewshot_injection import apply_fewshot_attack
from attacks.multilingual_attacks import apply_multilingual_attack

class AttackMutator:
    """Generates variations of successful attacks"""
    
    def __init__(self):
        self.mutation_strategies = [
            "encoding",
            "token_smuggling",
            "semantic_evasion",
            "context_wrap",
            "multiturn",
            "fewshot",
            "multilingual",
            "combination",
        ]
    
    def mutate(self, attack: Dict, strategy: str = None) -> Dict:
        """Mutate a single attack"""
        if strategy is None:
            strategy = random.choice(self.mutation_strategies)
        
        original_prompt = attack.get("prompt", "")
        attack_id = attack.get("attack_id", "")
        
        mutated_prompt = self._apply_mutation(original_prompt, strategy)
        
        mutated_attack = attack.copy()
        mutated_attack["prompt"] = mutated_prompt
        mutated_attack["attack_id"] = f"{attack_id}-mut-{strategy}"
        mutated_attack["tags"] = attack.get("tags", []) + [f"mutated-{strategy}"]
        mutated_attack["metadata"] = attack.get("metadata", {}).copy()
        mutated_attack["metadata"]["mutation_strategy"] = strategy
        mutated_attack["metadata"]["original_attack_id"] = attack_id
        
        return mutated_attack
    
    def _apply_mutation(self, prompt: str, strategy: str) -> str:
        """Apply specific mutation strategy"""
        if strategy == "encoding":
            encoding_type = random.choice(["base64", "rot13", "unicode_obfuscate", "hex"])
            return apply_encoding_attack(prompt, encoding_type)
        
        elif strategy == "token_smuggling":
            attack_type = random.choice(["special_tokens", "whitespace", "boundary"])
            return apply_token_smuggling(prompt, attack_type)
        
        elif strategy == "semantic_evasion":
            evasion_type = random.choice(["paraphrase", "academic", "euphemism", "question"])
            return apply_semantic_evasion(prompt, evasion_type)
        
        elif strategy == "context_wrap":
            context_type = random.choice(["long_context", "distraction", "buried"])
            return apply_context_attack(prompt, context_type)
        
        elif strategy == "multiturn":
            turn_strategy = random.choice(["gradual", "role", "poisoning"])
            return apply_multiturn_attack(prompt, turn_strategy)
        
        elif strategy == "fewshot":
            fewshot_type = random.choice(["fewshot", "instruction", "demonstration"])
            return apply_fewshot_attack(prompt, fewshot_type)
        
        elif strategy == "multilingual":
            lang = random.choice(["es", "fr", "de", "zh"])
            return apply_multilingual_attack(prompt, "translate", lang)
        
        elif strategy == "combination":
            # Apply multiple mutations
            strategies = random.sample(
                ["encoding", "semantic_evasion", "token_smuggling"], 
                k=random.randint(2, 3)
            )
            result = prompt
            for s in strategies:
                result = self._apply_mutation(result, s)
            return result
        
        return prompt
    
    def generate_variants(self, attack: Dict, num_variants: int = 5) -> List[Dict]:
        """Generate multiple variants of an attack"""
        variants = []
        strategies_used = []
        
        for i in range(num_variants):
            # Prefer unused strategies
            available_strategies = [s for s in self.mutation_strategies if s not in strategies_used]
            if not available_strategies:
                available_strategies = self.mutation_strategies
            
            strategy = random.choice(available_strategies)
            strategies_used.append(strategy)
            
            variant = self.mutate(attack, strategy)
            variant["attack_id"] = f"{attack['attack_id']}-v{i+1}"
            variants.append(variant)
        
        return variants
    
    def evolve_from_successful(self, successful_attacks: List[Dict], num_new: int = 10) -> List[Dict]:
        """Evolve new attacks from successful ones"""
        new_attacks = []
        
        for attack in successful_attacks:
            variants = self.generate_variants(attack, num_variants=num_new // len(successful_attacks))
            new_attacks.extend(variants)
        
        return new_attacks[:num_new]




