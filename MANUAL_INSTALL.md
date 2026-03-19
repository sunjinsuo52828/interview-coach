# Python 3.11 手动安装指南

**日期**: 2026-03-17
**状态**: 自动安装失败，需要手动安装

---

## 当前情况

| 检查项 | 状态 |
|--------|------|
| Python 3.14 (alpha) | ✅ 已安装 |
| pydantic 2.12.5 | ✅ 已安装 |
| **兼容性** | ❌ 段错误 |
| Python 3.11 | ❌ 未安装 |

安装程序已下载到: `C:\Users\jason\AppData\Local\Temp\python-3.11.9-amd64.exe`

---

## 手动安装步骤

### 步骤 1: 运行安装程序

**方法 A - 文件资源管理器**:
1. 按 `Win + R` 打开运行对话框
2. 输入: `%TEMP%` 并回车
3. 找到 `python-3.11.9-amd64.exe`
4. 双击运行

**方法 B - 命令行**:
```batch
"C:\Users\jason\AppData\Local\Temp\python-3.11.9-amd64.exe"
```

### 步骤 2: 安装选项

安装时请确保:
- ✅ **勾选** "Add Python to PATH" (重要!)
- ✅ 选择 "Install for all users" (可选但推荐)

或使用自定义安装到: `C:\Python311`

### 步骤 3: 验证安装

安装完成后，**关闭所有终端窗口**，然后打开新的终端运行:

```batch
py -0
```

应该看到类似输出:
```
 -V:3.14 *        Python 3.14 (64-bit)
 -V:3.11          Python 3.11 (64-bit)  <-- 这行应该出现
```

---

## 安装后的设置

### 1. 创建虚拟环境

```batch
cd C:\Practice\learning\interview-coach
py -3.11 -m venv venv
```

### 2. 激活虚拟环境

```batch
venv\Scripts\activate.bat
```

### 3. 安装依赖

```batch
pip install -r requirements.txt
```

### 4. 运行验证

```batch
python validate_tdd.py
```

---

## 故障排除

### 问题: py -0 不显示 Python 3.11

**解决**: Python 3.11 可能安装到了不同的位置。检查:
```batch
dir "C:\Users\%USERNAME%\AppData\Local\Programs\Python"
dir "C:\Python311"
```

找到 python.exe 后，直接使用完整路径创建虚拟环境:
```batch
"C:\Python311\python.exe" -m venv venv
```

### 问题: pip install 失败

**解决**: 先升级 pip:
```batch
python -m pip install --upgrade pip
```

---

## 快速命令清单

安装完成后按顺序执行:

```batch
REM 1. 切换到项目目录
cd C:\Practice\learning\interview-coach

REM 2. 创建虚拟环境
py -3.11 -m venv venv

REM 3. 激活虚拟环境
venv\Scripts\activate.bat

REM 4. 升级pip
python -m pip install --upgrade pip

REM 5. 安装依赖
pip install -r requirements.txt

REM 6. 运行验证
python validate_tdd.py

REM 7. 运行测试
pytest tests/unit/ -v
```

---

## 完成后反馈

安装完成后，请运行以下命令并告诉我结果:

```batch
py -0
```

这将确认 Python 3.11 是否已成功安装。

---

*请手动运行安装程序后继续*
