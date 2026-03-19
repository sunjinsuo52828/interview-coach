# GitHub 推送和 Streamlit Cloud 部署指南

## 📋 前置条件

✅ Git 仓库已初始化
✅ 代码已提交 (commit: 7bd6c3f)
✅ 远程仓库已配置: `https://github.com/jason52828/interview-coach.git`

---

## 🚀 部署步骤

### 步骤 1: 先在 GitHub 创建仓库

1. 访问: https://github.com/new
2. 仓库名称: `interview-coach`
3. 选择 **Public** 或 **Private**
4. **重要**: ❌ 不要勾选 "Add a README file"
5. 点击 "Create repository"

### 步骤 2: 推送代码到 GitHub

```bash
cd C:\Practice\learning\interview-coach
git push -u origin main
```

如果遇到网络问题，尝试：
- 检查代理设置
- 或使用 SSH 方式：
```bash
git remote set-url origin git@github.com:jason52828/interview-coach.git
git push -u origin main
```

### 步骤 3: 部署到 Streamlit Cloud

#### 方式 A: 网页部署（推荐）

1. 访问: https://share.streamlit.io
2. 点击 **"New app"**
3. 选择 **"Deploy an app from GitHub"**
4. 授权 GitHub 账号
5. 选择仓库: `jason52828/interview-coach`
6. 配置部署:
   ```
   Main file path: ui/app.py
   Python version: 3.11
   ```
7. 点击 **"Deploy"**

#### 方式 B: CLI 部署

```bash
pip install streamlit
cd C:\Practice\learning\interview-coach
streamlit run ui/app.py
# 按提示登录 GitHub 并部署
```

### 步骤 4: 配置环境变量

在 Streamlit Cloud 的 **Settings → Secrets** 中添加：

```bash
GLM_API_KEY=20727befa2cd4392aa69275581586e6a.OAO9HE3kD5XOFbPD
```

---

## 🔗 部署后的访问地址

- **GitHub**: https://github.com/jason52828/interview-coach
- **Streamlit Cloud**: https://jason52828-interview-coach-app.streamlit.app（部署后生成）

---

## 📝 部署检查清单

- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub
- [ ] Streamlit Cloud 应用已创建
- [ ] 环境变量已配置
- [ ] 应用可以正常访问

---

## 🐛 常见问题

### Q: Git 推送失败
**A**:
- 检查网络连接
- 尝试使用 SSH 替代 HTTPS
- 确认 GitHub 仓库已创建

### Q: Streamlit Cloud 部署失败
**A**:
- 检查 `ui/app.py` 路径是否正确
- 确保 `packages.txt` 包含所有依赖
- 检查环境变量是否配置

### Q: API 调用失败
**A**:
- 确认 `GLM_API_KEY` 已正确设置
- 检查 API 密钥是否有效

---

## 🎉 完成后

你的 Interview Coach 将在云端运行，可以通过以下链接访问：
- Streamlit Cloud 提供的 URL
- 或直接通过 GitHub 集成访问
