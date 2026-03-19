# 测试环境准备指南

**问题**: Python 3.14.0a5 (alpha版本) 与部分依赖包不兼容，导致段错误

**解决方案**: 安装稳定的Python版本 (3.11/3.12) 或使用虚拟环境

---

## 🔧 方案1: 安装Python 3.11/3.12 (推荐)

### Windows

1. **下载Python 3.11**
   - 访问: https://www.python.org/downloads/
   - 下载Python 3.11.x (64-bit)
   - 安装时勾选 "Add Python to PATH"

2. **设置虚拟环境**
   ```batch
   cd C:\Practice\learning\interview-coach

   # 创建虚拟环境
   py -3.11 -m venv venv

   # 激活虚拟环境
   venv\Scripts\activate

   # 安装依赖
   pip install -r requirements.txt
   ```

3. **运行测试**
   ```batch
   pytest tests/unit/ -v
   ```

---

## 🔧 方案2: 使用conda (推荐)

### 安装Miniconda

1. **下载Miniconda**
   - 访问: https://docs.conda.io/en/latest/miniconda.html
   - 下载Windows installer
   - 安装时选择"Add to PATH"

2. **创建环境**
   ```batch
   # 创建Python 3.11环境
   conda create -n interviewcoach python=3.11 -y

   # 激活环境
   conda activate interviewcoach

   # 切换到项目目录
   cd C:\Practice\learning\interview-coach

   # 安装依赖
   pip install -r requirements.txt
   ```

3. **运行测试**
   ```batch
   pytest tests/unit/ -v
   ```

---

## 🔧 方案3: 使用pyenv-win (高级)

1. **安装pyenv-win**
   ```batch
   pip install pyenv-win --target %USERPROFILE%\\.pyenv\\pyenv-win
   ```

2. **安装Python 3.11**
   ```batch
   pyenv install 3.11.7
   pyenv global 3.11.7
   ```

3. **设置项目环境**
   ```batch
   cd C:\Practice\learning\interview-coach
   pyenv local 3.11.7

   # 验证版本
   python --version
   ```

4. **安装依赖并测试**
   ```batch
   pip install -r requirements.txt
   pytest tests/unit/ -v
   ```

---

## 📋 核心依赖清单

必需的Python包：
```
anthropic>=0.40.0          # Claude API
pydantic>=2.10.0           # 数据验证
pydantic-settings>=2.6.0   # 配置管理
pytest>=8.3.0               # 测试框架
python-dotenv>=1.0.0        # 环境变量
```

---

## ✅ 验证环境安装成功

安装完成后，请运行以下验证：

```batch
# 1. 检查Python版本
python --version
# 应该显示: Python 3.11.x 或 3.12.x

# 2. 检查pip
pip list | findstr /i "pydantic anthropic pytest"

# 3. 测试导入
cd C:\Practice\learning\interview-coach
python -c "from models import ParsedResume; print('models OK')"
```

---

## 🚨 故障排除

### 问题: pip安装失败
```batch
# 清除缓存并重试
pip install --upgrade pip
pip install --no-cache-dir pydantic
```

### 问题: 找不到Python
```batch
# 添加Python到PATH
setx PATH "%PATH%;C:\Python311\Scripts;%PATH%"
```

### 问题: 虚拟环境激活失败
```batch
# 使用完整路径激活
C:\Practice\learning\interview-coach\venv\Scripts\activate.bat
```

---

## 📝 完成后请反馈

环境准备完成后请运行：
```batch
pytest tests/unit/ -v
```

并告诉我结果。
