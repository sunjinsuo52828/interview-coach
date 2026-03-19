"""
测试UI模块导入和基本功能
"""
import sys
sys.path.insert(0, '.')

try:
    print("Testing UI module import...")
    from ui.app import init_session_state, render_sidebar, render_setup_page
    print("[OK] UI module imported")

    print("\nTesting Orchestrator import...")
    from agents import create_orchestrator
    print("[OK] Orchestrator imported")

    print("\nCreating Orchestrator instance...")
    orchestrator = create_orchestrator()
    print("[OK] Orchestrator created")

    print("\nGetting initial state...")
    state = orchestrator.get_state()
    print(f"[OK] State retrieved: {list(state.keys())}")

    print("\n" + "="*50)
    print("All basic tests passed!")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
