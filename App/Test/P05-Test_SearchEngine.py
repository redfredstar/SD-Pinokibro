#!/usr/bin/env python3
"""
Test script for P05_SearchEngine
Tests search functionality with queries and filters.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.P05_SearchEngine import P05_SearchEngine

def test_search_engine():
    """Basic unit test for P05_SearchEngine functionality."""
    print("=== P05_SearchEngine Unit Test ===\n")
    
    # Initialize search engine
    engine = P05_SearchEngine("data/cleaned_pinokio_apps.json")
    
    # Get stats
    stats = engine.get_stats()
    print(f"Database loaded: {stats['total_apps']} apps")
    print(f"Categories: {stats['categories']}")
    print(f"Unique tags: {stats['unique_tags']}\n")
    
    # Test search with query and filter
    print("Searching for 'diffusion' in category 'AI-Art'...")
    results = engine.search(
        query="diffusion",
        filters={"category": "AI-Art"}
    )
    
    print(f"Found {len(results)} results:\n")
    
    # Display top 5 results
    for i, app in enumerate(results[:5], 1):
        print(f"{i}. {app['name']} (Score: {app['relevance_score']:.1f})")
        print(f"   Category: {app['category']}")
        print(f"   Tags: {', '.join(app['tags'][:3])}")
        print(f"   GPU Required: {app['gpu_required']}\n")
    
    print("✓ Test completed successfully")

if __name__ == "__main__":
    test_search_engine()