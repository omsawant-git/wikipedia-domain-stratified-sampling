"""
Add domain labels to Era's 15k dataset - IMPROVED VERSION
Author: Om Sawant
Uses more flexible category matching
"""

import json
import time
import requests
from collections import Counter

USER_AGENT = "WPI_GQP_Project_Researcher/1.0 (mnadkarni@wpi.edu)"

# Expanded keyword matching with partial matches
DOMAIN_KEYWORDS = {
    "government_politics": ["politic", "government", "election", "democra", "republican", "legislat", "congress", "parliament", "vote", "campaign"],
    "economics": ["econom", "fiscal", "monetary", "trade", "market", "gdp", "inflation", "unemployment"],
    "psychology": ["psycholog", "cognit", "behavior", "mental process", "perception"],
    "sociology": ["sociolog", "social", "society", "culture", "community"],
    "anthropology": ["anthropolog", "cultural", "ethnic", "civilization"],
    
    "management": ["management", "organizational", "business admin", "leadership", "corporate"],
    "accounting_finance": ["accounting", "finance", "financial", "investment", "banking", "audit", "stock", "bond"],
    "business_law": ["business law", "corporate law", "contract", "commercial law", "legal"],
    "entrepreneurship": ["entrepreneur", "startup", "venture", "founder"],
    "marketing": ["marketing", "advertising", "brand", "consumer", "promotion"],
    "business_statistics": ["business stat", "econometric"],
    
    "nursing": ["nursing", "nurse", "patient care", "rn", "healthcare"],
    "clinical_medicine": ["clinical", "medicine", "medical", "diagnosis", "treatment", "disease", "hospital", "health", "patient", "doctor", "physician"],
    "obstetrics": ["obstetric", "midwife", "maternal", "pregnancy", "childbirth", "prenatal"],
    "mental_health": ["psychiatric", "mental health", "psychiatry", "depression", "anxiety", "therapy"],
    "surgery": ["surgery", "surgical", "operation", "surgeon"],
    "nutrition_pharma": ["nutrition", "pharmacolog", "dietetic", "drug", "pharmaceutical", "vitamin", "supplement"],
    "public_health": ["public health", "epidemiolog", "community health", "preventive", "vaccination"],
    
    "history": ["history", "historical", "historian", "century", "war", "ancient", "medieval"],
    "philosophy": ["philosoph", "ethics", "logic", "metaphysic", "epistemolog", "moral"],
    "writing": ["writing", "rhetoric", "composition", "grammar", "literature", "literary", "author", "poet"],
    
    "anatomy_physiology": ["anatomy", "physiolog", "human body", "organ", "muscle", "skeleton", "tissue"],
    "biology": ["biolog", "genetic", "ecology", "evolution", "organism", "species", "botany", "zoology", "cell", "dna", "protein", "ecosystem"],
    "microbiology": ["microbiolog", "bacteriolog", "virolog", "bacteria", "virus", "microbe", "pathogen"],
    
    "astronomy": ["astronomy", "astrophysic", "cosmolog", "planet", "star", "galaxy", "space", "solar", "celestial"],
    "physics": ["physics", "mechanic", "thermodynamic", "quantum", "relativity", "electromagnetic", "force", "energy", "motion", "particle"],
    "chemistry": ["chemistry", "chemical", "biochem", "organic chem", "molecule", "compound", "reaction", "element", "atom"],
    
    "mathematics": ["mathematic", "algebra", "calculus", "geometry", "trigonometry", "theorem", "equation", "proof"],
    "statistics": ["statistic", "probability", "data analysis", "variance", "distribution"],
    
    "computer_science": ["computer science", "algorithm", "programming", "software", "computing", "code", "database", "network"],
    "data_science": ["data science", "machine learning", "artificial intelligence", "neural network", "deep learning"],
}


def get_page_categories(session, title):
    """Fetch Wikipedia categories for a page."""
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "categories",
        "cllimit": 500
    }
    
    try:
        time.sleep(0.05)
        resp = session.get(
            "https://en.wikipedia.org/w/api.php", 
            params=params, 
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        
        if "missing" in page:
            return []
        
        categories = []
        for cat in page.get("categories", []):
            cat_title = cat.get("title", "").replace("Category:", "")
            categories.append(cat_title)
        
        return categories
        
    except Exception as e:
        return []


def assign_domain(categories):
    """Match page categories to domains using flexible keyword matching."""
    if not categories:
        return None
    
    # Join all categories into lowercase searchable text
    cat_text = " ".join(categories).lower()
    
    # Score each domain by partial keyword matches
    domain_scores = Counter()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            # Partial match - keyword just needs to be contained in category text
            if keyword.lower() in cat_text:
                domain_scores[domain] += 1
    
    # Return domain with highest score
    if domain_scores:
        return domain_scores.most_common(1)[0][0]
    
    return None


def main():
    INPUT_FILE = "dataset_15k_batch.jsonl"
    OUTPUT_FILE = "dataset_15k_annotated_v2.jsonl"
    
    print("=" * 60)
    print("Domain Annotation Script - IMPROVED")
    print("=" * 60)
    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}\n")
    
    # Count total rows
    print("Counting rows...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        total = sum(1 for _ in f)
    print(f"Total rows: {total:,}\n")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    })
    
    domain_stats = Counter()
    processed = 0
    errors = 0
    
    print("Processing...")
    print("-" * 60)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            processed += 1
            
            if processed % 100 == 0:
                pct = 100 * processed / total
                classified = sum(v for k, v in domain_stats.items() if k != "unclassified")
                print(f"Progress: {processed:,}/{total:,} ({pct:.1f}%) | "
                      f"Classified: {classified:,} ({100*classified/processed:.1f}%)")
            
            try:
                row = json.loads(line.strip())
                
                title = row.get("title")
                if not title:
                    row["domain"] = "unknown"
                    fout.write(json.dumps(row) + "\n")
                    domain_stats["unknown"] += 1
                    continue
                
                # Get categories and assign domain
                categories = get_page_categories(session, title)
                domain = assign_domain(categories)
                
                if domain:
                    row["domain"] = domain
                    domain_stats[domain] += 1
                else:
                    row["domain"] = "unclassified"
                    domain_stats["unclassified"] += 1
                
                fout.write(json.dumps(row) + "\n")
                
            except Exception as e:
                errors += 1
                print(f"\nError on row {processed}: {e}")
                fout.write(line)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total processed: {processed:,}")
    print(f"Errors: {errors}")
    
    classified_count = sum(v for k, v in domain_stats.items() if k not in ["unclassified", "unknown"])
    print(f"Classified: {classified_count:,} ({100*classified_count/processed:.1f}%)")
    print(f"Unclassified: {domain_stats['unclassified']:,} ({100*domain_stats['unclassified']/processed:.1f}%)")
    
    print(f"\nDomain Distribution:")
    print("-" * 60)
    
    for domain, count in sorted(domain_stats.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        print(f"{domain:30s}: {count:5,} ({pct:5.1f}%)")
    
    print(f"\nAnnotated dataset saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()