import asyncio
import sys
import os

# Ensure src is in pythonpath
sys.path.append(os.path.abspath("src"))

from mnemosyne.poc.generator import BundleGenerator

async def verify_bundle_generation():
    print("--- MNEMOSYNE POC: HEADLESS VERIFICATION ---")
    
    generator = BundleGenerator(storage_dir="storage_poc_verify")
    
    print("Generating bundle for 'Simbli'...")
    data = await generator.generate_monthly_bundle(
        company_name="Simbli",
        industry="SaaS / AI",
        description="Organizing strategic intelligence.",
        goal="Brand Awareness",
        num_posts=4 # Compact test
    )
    
    print("\n[RESULT]")
    print(f"Strategy: {data['strategy_snapshot']}")
    print(f"Assumptions: {[a.statement for a in data['assumptions']]}")
    print(f"Generated {len(data['posts'])} posts.")
    
    for i, post in enumerate(data['posts']):
        print(f"\nPost #{i+1} ({post['date']}):")
        print(f"  Content: {post['content'][:50]}...")
        if post['image_artifact']:
            print(f"  Image: {post['image_artifact'].file_path}")
            print(f"  Intent: {post['visual_intent'].visual_style}, {post['visual_intent'].human_presence}")
        else:
            print("  Image: MISSING")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(verify_bundle_generation())
