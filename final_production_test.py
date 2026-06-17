#!/usr/bin/env python3
"""Final test of Internshala search in production mode."""

import sys
import time
sys.path.insert(0, 'backend')

from job_search.internshala import search_internshala

# Test all major roles
test_roles = [
    "Machine Learning",
    "Data Science", 
    "Web Development",
    "Python Development",
    "Java Development",
    "Backend Development",
    "Full Stack Development"
]

print("\n" + "="*70)
print("PRODUCTION TEST - HEADLESS MODE")
print("="*70)

total_jobs = 0
for role in test_roles:
    start = time.time()
    results = search_internshala(role)
    elapsed = time.time() - start
    total_jobs += len(results)
    status = "✓" if len(results) > 0 else "✗"
    print(f"{status} {role:25} -> {len(results):2} jobs ({elapsed:.1f}s)")

print("="*70)
print(f"TOTAL JOBS FOUND: {total_jobs}")
print("="*70 + "\n")
