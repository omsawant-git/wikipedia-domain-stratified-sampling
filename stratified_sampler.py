"""
Stratified Random Sampling for 10k Dataset - Strict Cap Enforcement
Author: Om Sawant
"""

import json
import random
from collections import defaultdict, Counter

INPUT_FILE = "dataset_15k_annotated_v2.jsonl"
OUTPUT_FILE = "dataset_10k_stratified.jsonl"
TARGET_TOTAL = 10000

def main():
    print("=" * 60)
    print("Stratified Random Sampler")
    print("Author: Om Sawant")
    print("=" * 60)
    
    # Load and group by domain
    domain_pages = defaultdict(list)
    
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            row = json.loads(line.strip())
            domain = row.get("domain", "unclassified")
            domain_pages[domain].append(row)
    
    total_rows = sum(len(pages) for pages in domain_pages.values())
    print(f"Total rows: {total_rows:,}")
    print(f"Domains: {len(domain_pages)}\n")
    
    # Define strict percentage caps
    PERCENTAGE_CAPS = {
        "history": 5.0,              # Max 500 pages
        "nursing": 5.0,              # Max 500 pages
        "government_politics": 7.0,  # Max 700 pages
        "biology": 6.0,              # Max 600 pages
        "unclassified": 30.0,        # Max 3000 pages - STRICT
    }
    
    domain_targets = {}
    allocated = 0
    
    # First pass: allocate capped domains (STRICT - no override later)
    capped_domains = set(PERCENTAGE_CAPS.keys())
    for domain in capped_domains:
        if domain in domain_pages:
            available = len(domain_pages[domain])
            max_allowed = int(PERCENTAGE_CAPS[domain] * TARGET_TOTAL / 100)
            target = min(max_allowed, available)
            domain_targets[domain] = target
            allocated += target
    
    # Second pass: allocate remaining domains proportionally
    remaining_budget = TARGET_TOTAL - allocated
    remaining_domains = {d: pages for d, pages in domain_pages.items() 
                        if d not in capped_domains}
    remaining_total = sum(len(pages) for pages in remaining_domains.values())
    
    for domain, pages in remaining_domains.items():
        available = len(pages)
        if remaining_total > 0:
            proportion = available / remaining_total
            target = int(proportion * remaining_budget)
            target = min(target, available)
            domain_targets[domain] = target
            allocated += target
    
    # Final adjustment - distribute any remainder among NON-CAPPED domains only
    current_total = sum(domain_targets.values())
    diff = TARGET_TOTAL - current_total
    
    if diff > 0:
        # Add to non-capped domains that have room
        non_capped_with_room = []
        for domain in domain_targets.keys():
            if domain not in capped_domains:
                available = len(domain_pages[domain])
                current = domain_targets[domain]
                if current < available:
                    non_capped_with_room.append((domain, available - current))
        
        # Sort by available space descending
        non_capped_with_room.sort(key=lambda x: -x[1])
        
        # Distribute remainder
        for domain, room in non_capped_with_room:
            if diff <= 0:
                break
            add = min(diff, room)
            domain_targets[domain] += add
            diff -= add
    
    elif diff < 0:
        # Reduce from largest non-capped domains
        non_capped = [(d, domain_targets[d]) for d in domain_targets.keys() 
                     if d not in capped_domains]
        non_capped.sort(key=lambda x: -x[1])
        
        for domain, current in non_capped:
            if diff >= 0:
                break
            reduction = min(abs(diff), current)
            domain_targets[domain] -= reduction
            diff += reduction
    
    # Summary
    final_total = sum(domain_targets.values())
    
    print("Sampling targets:")
    print("-" * 60)
    for domain in sorted(domain_targets.keys()):
        target = domain_targets[domain]
        available = len(domain_pages[domain])
        pct = 100 * target / final_total if final_total > 0 else 0
        cap_indicator = " [CAPPED]" if domain in capped_domains else ""
        print(f"{domain:30s}: {target:4,} / {available:5,} ({pct:4.1f}%){cap_indicator}")
    
    print(f"\nTotal allocated: {final_total:,} (target was {TARGET_TOTAL:,})")
    
    # Sample
    print("\n" + "=" * 60)
    print("Sampling...")
    sampled = []
    
    for domain, target in domain_targets.items():
        pages = domain_pages[domain]
        if target > 0 and len(pages) > 0:
            sample = random.sample(pages, min(target, len(pages)))
            sampled.extend(sample)
    
    random.shuffle(sampled)
    
    # Write
    print(f"\nWriting to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for row in sampled:
            f.write(json.dumps(row) + "\n")
    
    # Stats
    final_domains = Counter(row["domain"] for row in sampled)
    final_quality = Counter(row.get("quality_class_best", "Unknown") for row in sampled)
    
    print(f"\n{'='*60}")
    print(f"FINAL STRATIFIED SAMPLE")
    print("=" * 60)
    print(f"Total pages: {len(sampled):,}\n")
    
    print("Domain distribution:")
    print("-" * 60)
    for domain, count in sorted(final_domains.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(sampled)
        print(f"  {domain:28s}: {count:4,} ({pct:5.1f}%)")
    
    print("\nQuality class distribution:")
    print("-" * 60)
    for q, count in sorted(final_quality.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(sampled)
        print(f"  {q:28s}: {count:4,} ({pct:5.1f}%)")
    
    print(f"\nStratified sample saved to: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Summary for reporting
    classified = sum(count for domain, count in final_domains.items() if domain != "unclassified")
    unclass = final_domains.get("unclassified", 0)
    print(f"\nSummary:")
    print(f"  Classified domains: {classified:,} ({100*classified/len(sampled):.1f}%)")
    print(f"  Unclassified: {unclass:,} ({100*unclass/len(sampled):.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    random.seed(42)
    main()