#!/usr/bin/env python3
"""Debug script to test Internshala search functionality."""

import sys
sys.path.insert(0, 'backend')

from job_search.internshala import search_internshala

# Test with a simple query
print("\n" + "="*60)
print("TESTING: Machine Learning")
print("="*60)
results = search_internshala("Machine Learning")
print(f"\nResults found: {len(results)}")
for job in results:
    print(f"  - {job['title']} at {job['company']} ({job['location']})")
    print(f"    URL: {job['url']}\n")

print("\n" + "="*60)
print("TESTING: Web Development")
print("="*60)
results = search_internshala("Web Development")
print(f"\nResults found: {len(results)}")
for job in results:
    print(f"  - {job['title']} at {job['company']} ({job['location']})")
    print(f"    URL: {job['url']}\n")
