"""
Streamlit API 端点测试

使用 requests 库直接测试 Streamlit 应用的 API 接口
"""
import requests
import time
import json


class StreamlitAPITester:
    """Streamlit API 测试器"""

    def __init__(self, base_url="http://localhost:8501"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None

    def check_health(self):
        """检查应用健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/_stcore/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def get_page_content(self):
        """获取页面内容"""
        try:
            response = self.session.get(self.base_url)
            return response.status_code == 200
        except Exception as e:
            print(f"Get page failed: {e}")
            return False

    def test_streamlit_running(self):
        """测试 Streamlit 是否运行"""
        print("\n" + "="*50)
        print("Streamlit API 测试")
        print("="*50)

        # 测试 1: 健康检查
        print("\n[1/4] 健康检查...")
        if self.check_health():
            print("  [OK] 应用运行正常")
        else:
            print("  [ERROR] 应用未响应")
            return False

        # 测试 2: 页面内容
        print("\n[2/4] 检查页面内容...")
        if self.get_page_content():
            print("  [OK] 页面可访问")
        else:
            print("  [ERROR] 页面无法访问")
            return False

        # 测试 3: 检查静态资源
        print("\n[3/4] 检查静态资源...")
        try:
            response = self.session.get(f"{self.base_url}/static/js/index.js")
            if response.status_code == 200:
                print("  [OK] 静态资源可访问")
            else:
                print(f"  [WARN] 静态资源状态: {response.status_code}")
        except Exception as e:
            print(f"  [WARN] 静态资源检查失败: {e}")

        # 测试 4: Streamlit 端点
        print("\n[4/4] 检查 Streamlit 端点...")
        endpoints = [
            "/_stcore/health",
            "/_stcore/status",
        ]
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                status = "OK" if response.status_code in [200, 404] else f"ERROR:{response.status_code}"
                print(f"  {endpoint}: {status}")
            except Exception as e:
                print(f"  {endpoint}: ERROR - {e}")

        print("\n" + "="*50)
        print("API 测试完成!")
        print("="*50)
        return True


def test_ui_imports():
    """测试 UI 模块导入"""
    print("\n" + "="*50)
    print("UI 模块导入测试")
    print("="*50)

    import sys
    sys.path.insert(0, 'C:/Practice/learning/interview-coach')

    tests = []

    # 测试 1: 导入 Streamlit
    print("\n[1/4] 导入 streamlit...")
    try:
        import streamlit as st
        print(f"  [OK] streamlit 版本: {st.__version__}")
        tests.append(True)
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests.append(False)

    # 测试 2: 导入 UI 模块
    print("\n[2/4] 导入 ui.app...")
    try:
        from ui.app import init_session_state, render_sidebar, render_setup_page
        print("  [OK] ui.app 导入成功")
        tests.append(True)
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests.append(False)

    # 测试 3: 导入 Orchestrator
    print("\n[3/4] 导入 InterviewOrchestrator...")
    try:
        from agents import create_orchestrator
        orchestrator = create_orchestrator()
        state = orchestrator.get_state()
        print(f"  [OK] Orchestrator 创建成功, 状态: {list(state.keys())}")
        tests.append(True)
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests.append(False)

    # 测试 4: 导入配置
    print("\n[4/4] 导入配置...")
    try:
        from config import INTERVIEWER_LEVELS, INTERVIEWER_STYLES, FOCUS_AREAS
        print(f"  [OK] 配置加载成功:")
        print(f"       - 面试官级别: {len(INTERVIEWER_LEVELS)} 个")
        print(f"       - 面试风格: {len(INTERVIEWER_STYLES)} 个")
        print(f"       - 考察重点: {len(FOCUS_AREAS)} 个")
        tests.append(True)
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests.append(False)

    print("\n" + "="*50)
    passed = sum(tests)
    total = len(tests)
    print(f"导入测试结果: {passed}/{total} 通过")
    print("="*50)

    return all(tests)


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print(" "*15 + "Interview Coach UI 测试")
    print("="*60)

    # 测试 1: 模块导入
    import_ok = test_ui_imports()

    # 测试 2: API 端点
    print("\n等待 Streamlit 启动...")
    time.sleep(2)

    api_tester = StreamlitAPITester()
    api_ok = api_tester.test_streamlit_running()

    # 总结
    print("\n" + "="*60)
    print("测试总结:")
    print(f"  模块导入: {'[PASS]' if import_ok else '[FAIL]'}")
    print(f"  API 测试: {'[PASS]' if api_ok else '[FAIL]'}")
    print("="*60)

    if import_ok and api_ok:
        print("\n[SUCCESS] 所有测试通过!")
        return 0
    else:
        print("\n[FAILURE] 部分测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
