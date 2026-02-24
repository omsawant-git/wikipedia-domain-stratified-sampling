# Domain Annotation and Stratified Sampling

**Author:** Om Sawant  
**Project:** Wikipedia Educational Quality Filter - Microsoft WPI GQP Spring 2026

## Overview
Domain annotation and stratified sampling pipeline for 15k Wikipedia pages. Transforms random Wikipedia sample into domain-balanced educational dataset.

## Files
- `annotate_domains.py` - Annotates Wikipedia pages with educational domain labels
- `stratified_sampler.py` - Creates stratified sample with domain balance

## Results
- Input: 15,012 random Wikipedia pages
- Output: 7,075 domain-stratified pages
- Classification: 57.6% across 25 Microsoft educational domains

## Usage
```bash
# Annotate pages
python3 annotate_domains.py

# Create stratified sample
python3 stratified_sampler.py
```
