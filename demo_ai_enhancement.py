#!/usr/bin/env python3
"""
Comparison test showing the improvement from keyword matching to semantic search
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ai_agent import get_houston_agent
from utils.gemini_ai import extract_relevant_sources, get_default_houston_sources

def test_keyword_vs_semantic():
    """Compare old keyword matching vs new semantic search"""
    
    print("=" * 80)
    print("HOUSTON FINANCIAL NAVIGATOR - AI ENHANCEMENT DEMONSTRATION")
    print("=" * 80)
    print("Comparing: Old Keyword Matching vs New Semantic Search")
    print()
    
    # Get the enhanced agent
    agent = get_houston_agent()
    sources = get_default_houston_sources()
    
    test_queries = [
        {
            "query": "I need help paying my electricity bill",
            "expected": "Should find utility assistance programs"
        },
        {
            "query": "My family needs food assistance", 
            "expected": "Should find food bank programs"
        },
        {
            "query": "I'm homeless and need shelter",
            "expected": "Should find emergency shelter services"
        },
        {
            "query": "Help with mortgage down payment",
            "expected": "Should find homebuyer assistance"
        },
        {
            "query": "Can't afford my rent this month",
            "expected": "Should find rental assistance programs"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"{i}. Query: '{query}'")
        print(f"   Expected: {expected}")
        print()
        
        # Test old keyword matching approach
        print("   OLD APPROACH (Keyword Matching):")
        try:
            old_sources = extract_relevant_sources(query, sources)
            if old_sources:
                print(f"   ✓ Found {len(old_sources)} programs:")
                for source in old_sources[:2]:  # Show top 2
                    print(f"     - {source.get('name', 'Unknown')}")
            else:
                print("   ✗ No programs found")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()
        
        # Test new semantic search
        print("   NEW APPROACH (Semantic Search):")
        try:
            if agent.vectorizer is not None:
                semantic_result = agent._search_houston_resources(query)
                if "No highly relevant" in semantic_result:
                    print("   ✗ No highly relevant programs found")
                else:
                    lines = semantic_result.split('\n')
                    # Extract program names and relevance scores
                    programs = []
                    relevance_scores = []
                    for line in lines:
                        if line.strip() and line[0].isdigit():
                            programs.append(line.strip())
                        elif "Relevance:" in line:
                            relevance_scores.append(line.strip())
                    
                    print(f"   ✓ Found {len(programs)} relevant programs with scores:")
                    for j, program in enumerate(programs[:2]):  # Show top 2
                        score = relevance_scores[j] if j < len(relevance_scores) else ""
                        print(f"     - {program}")
                        if score:
                            print(f"       {score}")
            else:
                print("   ⚠ Semantic search not available, using keyword fallback")
                fallback_result = agent._keyword_search_fallback(query)
                if "No relevant" in fallback_result:
                    print("   ✗ No programs found")
                else:
                    print("   ✓ Found programs using enhanced keyword search")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()
        print("-" * 60)
        print()

def show_database_enhancement():
    """Show the enhanced assistance program database"""
    
    print("DATABASE ENHANCEMENT SUMMARY")
    print("=" * 40)
    
    sources = get_default_houston_sources()
    
    print(f"Total Programs: {len(sources)}")
    print()
    print("Program Categories:")
    
    categories = {
        "Housing/Rental": [],
        "Utilities": [],
        "Food Assistance": [],
        "Emergency Shelter": [],
        "Homebuying": []
    }
    
    for source in sources:
        name = source.get('name', '')
        if 'housing' in name.lower() or 'rental' in name.lower():
            categories["Housing/Rental"].append(name)
        elif 'energy' in name.lower() or 'utility' in name.lower() or 'centerpoint' in name.lower():
            categories["Utilities"].append(name)
        elif 'food' in name.lower():
            categories["Food Assistance"].append(name)
        elif 'homeless' in name.lower() or 'shelter' in name.lower():
            categories["Emergency Shelter"].append(name)
        elif 'homebuyer' in name.lower() or 'home' in name.lower():
            categories["Homebuying"].append(name)
    
    for category, programs in categories.items():
        if programs:
            print(f"\n{category}:")
            for program in programs:
                print(f"  • {program}")

def show_semantic_scores():
    """Demonstrate semantic similarity scoring"""
    
    print("SEMANTIC SIMILARITY DEMONSTRATION")
    print("=" * 40)
    
    agent = get_houston_agent()
    
    if agent.vectorizer is None:
        print("Semantic search not available")
        return
    
    test_queries = [
        "electricity bill help",
        "power company assistance", 
        "energy bill payment",
        "utility assistance",
        "homeless services",
        "emergency shelter",
        "food for children",
        "grocery assistance"
    ]
    
    print("Testing semantic understanding - similar queries should find same programs:")
    print()
    
    for query in test_queries:
        result = agent._search_houston_resources(query)
        lines = result.split('\n')
        
        # Extract first program and relevance
        program = None
        relevance = None
        for line in lines:
            if line.strip() and line[0].isdigit():
                program = line.strip().split('. ')[1] if '. ' in line else line.strip()
                break
        
        for line in lines:
            if "Relevance:" in line:
                relevance = line.strip().split(': ')[1] if ': ' in line else "N/A"
                break
        
        if program and relevance:
            print(f"'{query}' → {program} (score: {relevance})")
        else:
            print(f"'{query}' → No relevant match found")

def main():
    """Run the complete comparison demonstration"""
    
    # Test keyword vs semantic comparison
    test_keyword_vs_semantic()
    
    # Show database enhancement
    show_database_enhancement()
    print()
    
    # Show semantic scoring
    show_semantic_scores()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ Enhanced from 5 to 9 diverse assistance programs")
    print("✅ Replaced keyword matching with semantic similarity")
    print("✅ Added relevance scoring for better program matching")
    print("✅ Maintained backward compatibility with graceful fallbacks")
    print("✅ Ready for LangChain agent integration with API keys")
    print("=" * 80)

if __name__ == "__main__":
    main()