import os
import sys

# 测试 API 密钥
api_key = input("请输入你的 Anthropic API 密钥 (sk-ant-...): ").strip()

if not api_key or not api_key.startswith("sk-ant-"):
    print("❌ 无效的 API 密钥格式")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("安装 Anthropic SDK...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
    from anthropic import Anthropic

try:
    client = Anthropic(api_key=api_key)
    print("🔄 测试 API 连接...")
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say 'API is working' if you can read this"}]
    )
    
    print(f"✅ API 密钥有效！")
    print(f"Claude 回复: {response.content[0].text}")
    print("\n现在你可以将这个密钥添加到 GitHub Secrets 中")
    
except Exception as e:
    print(f"❌ API 测试失败: {e}")
    print("\n可能的原因：")
    print("1. API 密钥无效或过期")
    print("2. 账户没有额度")
    print("3. 网络连接问题")
