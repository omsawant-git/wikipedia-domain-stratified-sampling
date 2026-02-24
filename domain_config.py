"""
Microsoft Learn Agent Educational Domains
Exact list from stakeholder email (Feb 2026)
"""

# Map domains to Wikipedia category keywords
DOMAIN_CATEGORY_MAP = {
    # Social Sciences
    "government_politics": ["Politics", "Government", "Political"],
    "economics": ["Economics", "Economic"],
    "psychology": ["Psychology", "Psychological"],
    "sociology": ["Sociology", "Sociological"],
    "anthropology": ["Anthropology", "Anthropological"],
    
    # Business
    "management": ["Management", "Organizational_behavior"],
    "accounting_finance": ["Accounting", "Finance", "Financial"],
    "business_law_ethics": ["Business_law", "Business_ethics", "Corporate_law"],
    "entrepreneurship": ["Entrepreneurship", "Startups"],
    "marketing": ["Marketing", "Advertising"],
    "business_statistics": ["Business_statistics", "Econometrics"],
    
    # Nursing
    "nursing_fundamentals": ["Nursing", "Clinical_skills"],
    "nursing_maternal": ["Obstetrics", "Midwifery", "Maternal"],
    "nursing_psychiatric": ["Psychiatric_nursing", "Mental_health"],
    "nursing_medical_surgical": ["Surgery", "Internal_medicine", "Medical"],
    "nursing_nutrition_pharma": ["Nutrition", "Pharmacology", "Dietetics"],
    "nursing_community": ["Public_health", "Community_health", "Epidemiology"],
    
    # Humanities
    "history": ["History", "Historical"],
    "philosophy": ["Philosophy", "Ethics", "Logic"],
    "writing_composition": ["Writing", "Rhetoric", "Composition", "Grammar"],
    
    # Life Sciences
    "anatomy_physiology": ["Anatomy", "Physiology", "Human_body"],
    "biology": ["Biology", "Biological", "Genetics", "Ecology"],
    "microbiology": ["Microbiology", "Bacteriology", "Virology"],
    
    # Physical Sciences
    "astronomy": ["Astronomy", "Astrophysics", "Cosmology"],
    "physics": ["Physics", "Mechanics", "Thermodynamics", "Quantum"],
    "chemistry": ["Chemistry", "Chemical", "Biochemistry"],
    
    # Math and Statistics
    "mathematics": ["Mathematics", "Mathematical", "Algebra", "Calculus", "Geometry"],
    "statistics": ["Statistics", "Statistical", "Probability"],
    
    # Computer and Data Science
    "computer_science": ["Computer_science", "Algorithms", "Programming"],
    "data_science": ["Data_science", "Machine_learning", "Artificial_intelligence"],
    "python": ["Python_(programming_language)"],
    
    # Additional (less common, may not find many matches)
    "workplace_software": ["Microsoft_Office", "Word_processing", "Spreadsheet"],
    "college_success": ["Study_skills", "Education"],
}

# Build reverse lookup: category -> domain
CATEGORY_TO_DOMAIN = {}
for domain, categories in DOMAIN_CATEGORY_MAP.items():
    for cat in categories:
        CATEGORY_TO_DOMAIN[cat.lower()] = domain