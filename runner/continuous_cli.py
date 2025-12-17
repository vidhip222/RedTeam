# runner/continuous_cli.py
"""CLI for continuous red-teaming loop"""
import argparse
from models.client import ModelClient
from runner.continuous_loop import ContinuousRedTeamLoop
from runner.runner import load_attacks
from attacks.advanced_generator import generate_advanced_attacks

def main():
    p = argparse.ArgumentParser(description="Continuous red-teaming loop")
    p.add_argument("--model", default="mock", choices=["mock", "openai"])
    p.add_argument("--api-key", default=None)
    p.add_argument("--iterations", type=int, default=5)
    p.add_argument("--attacks-file", default=None)
    p.add_argument("--generate", action="store_true", help="Generate advanced attacks first")
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    
    # Initialize model client
    client = ModelClient(provider=args.model, api_key=args.api_key, sanitize=False)
    
    # Load or generate attacks
    if args.generate:
        print("Generating advanced attacks...")
        attacks = generate_advanced_attacks()
    elif args.attacks_file:
        attacks = load_attacks(args.attacks_file)
    else:
        # Use default
        attacks = load_attacks("data/sample_attack_cases.json")
    
    print(f"Starting continuous loop with {len(attacks)} initial attacks")
    print(f"Model: {args.model}, Iterations: {args.iterations}")
    
    # Create loop
    loop = ContinuousRedTeamLoop(client, max_iterations=args.iterations)
    
    # Run continuous loop
    results = loop.run_continuous_loop(attacks)
    
    print("\nContinuous red-teaming loop complete!")

if __name__ == "__main__":
    main()




