import asyncio
import uuid
import json
import os
from workflow.graph import build_graph

async def main():
    print("========================================")
    print("🎥 Omni AI - Production Engine CLI 🎥")
    print("========================================")
    
    print("\nSelect a Template:")
    print("1. Advertisement")
    print("2. Story Film")
    print("3. Social Media Reel")
    
    template_choice = input("Enter number (1/2/3): ")
    template_map = {"1": "Advertisement", "2": "Story Film", "3": "Social Media Reel"}
    template = template_map.get(template_choice, "Advertisement")
    
    prompt = input("\nEnter your creative prompt: ")
    
    print(f"\n[AI ENGINE] Initializing execution for '{template}'...")
    
    # Enable interrupt for clarification
    graph = build_graph(interrupt_after_clarification=True)
    
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    initial_state = {
        "prompt": prompt,
        "template_name": template
    }
    
    # Run until interruption
    print("\n[AI ENGINE] Running initial requirements analysis...")
    state = await graph.ainvoke(initial_state, config)
    
    # Check if we were interrupted for clarification
    current_state = graph.get_state(config)
    
    if current_state.next:
        # We hit an interrupt!
        questions = current_state.values.get("clarification_questions", [])
        
        if questions:
            print("\n[!] The AI Director needs some clarification before continuing:\n")
            answers = {}
            for q in questions:
                answer = input(f"❓ {q}\n> ")
                answers[q] = answer
                
            print("\n[AI ENGINE] Resuming execution with your answers...")
            
            # Update state with answers and resume
            graph.update_state(config, {"clarification_answers": answers})
            final_state = await graph.ainvoke(None, config)
        else:
            print("\n[AI ENGINE] Resuming execution...")
            final_state = await graph.ainvoke(None, config)
    else:
        final_state = state
        
    print("========================================")
    print("✅ Generation Planning Complete!")
    print("========================================")
    
    cost_data = final_state.get('cost_estimation', {})
    planning = cost_data.get('planning_metrics', {})
    breakdown = cost_data.get('breakdown', {})
    
    print(f"Total AI Compute Cost (Planning): ${planning.get('total_cost_usd', 0.0):.4f}")
    print(f"Total Execution Time: {planning.get('total_time_sec', 0.0):.2f} seconds")
    print(f"Total API Calls: {planning.get('api_calls', 0)}")
    
    print("\n--- Production Asset & Cost Breakdown ---")
    
    img_data = breakdown.get('image_generation', {})
    vid_data = breakdown.get('video_generation', {})
    voice_data = breakdown.get('voice_generation', {})
    music_data = breakdown.get('music_generation', {})
    
    print(f"Images Required: {img_data.get('images', 0)} (Cost: ${img_data.get('cost', 0):.2f})")
    print(f"Videos Required: {vid_data.get('clips', 0)} (Cost: ${vid_data.get('cost', 0):.2f})")
    print(f"Voice Tracks Required (Cost: ${voice_data.get('cost', 0):.2f})")
    print(f"Music Tracks Required (Cost: ${music_data.get('cost', 0):.2f})")
    print(f"\nEstimated Final Production Cost: ${cost_data.get('estimated_cost', 0.0):.2f}\n")
    
    print("========================================")
    print("Final Generation Manifest (JSON):")
    print("========================================")
    
    plan_to_dump = final_state.get("creative_plan")
    if hasattr(plan_to_dump, "model_dump"):
        plan_to_dump = plan_to_dump.model_dump()
        
    print(json.dumps(plan_to_dump, indent=2, default=str))
    print("\n[AI ENGINE] Generation Complete!")
    
    # Write to final.json in the root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        final_output_path = os.path.join(root_dir, "final.json")
        
        plan_to_dump = final_state.get('creative_plan', {})
        with open(final_output_path, "w") as f:
            json.dump(plan_to_dump, f, indent=2, default=str)
            
        print(f"\n[AI ENGINE] Successfully saved Generation Manifest to: {final_output_path}")
            
    except Exception as e:
        print(f"[AI ENGINE] Failed to write final.json to root: {e}")

if __name__ == "__main__":
    asyncio.run(main())
