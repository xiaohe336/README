# VS Code Continue 本地模型配置指南 (YAML 版)

本文档说明如何将部署在本地服务器上的 Ollama 模型（Qwen3 Coder）通过 `config.yaml` 导入到 VS Code Continue 插件中。

---

## 步骤一：打开配置文件

1. 在 VS Code 中打开 Continue 插件侧边栏。
2. 点击**齿轮图标 (⚙️)**。

---

## 步骤二：添加 YAML 配置

将以下内容直接复制并粘贴到您的 `config.yaml` 文件中。该配置已包含对话、编辑、代码应用及自动补全的完整功能：

```yaml
name: Local Ollama Config
version: 1.0.0
schema: v1
models:
  - name: Qwen3 Coder (Local Server)
    provider: openai
    apiBase: http://192.168.11.188:11434/v1
    model: qwen3-coder-next:latest
    capabilities:
      - tool_use
    roles:
      - chat
      - edit
      - apply
      - autocomplete
    defaultCompletionOptions:
      temperature: 0.3
      maxTokens: 4096
    autocompleteOptions:
      debounceDelay: 1000 
      maxPromptTokens: 1024
```

---

## 核心配置参数说明

* **基础信息 (`name`, `provider`, `model`)**: 
  * 模型名称显示为 `Qwen3 Coder (Local Server)`。
  * 采用 `openai` 接口协议来桥接 Ollama 的服务。
  * 指定模型版本为 `qwen3-coder-next:latest`。
* **API 地址 (`apiBase`)**: 
  * 指向您的本地局域网服务器地址：`http://192.168.11.188:11434/v1`（请确保 VS Code 所在设备能 Ping 通此 IP）。
* **功能支持 (`capabilities` & `roles`)**:
  * 启用了工具使用 (`tool_use`) 能力。
  * 分配了多项角色任务：常规对话 (`chat`)、代码编辑 (`edit`)、代码应用 (`apply`) 以及代码自动补全 (`autocomplete`)。
* **生成与补全选项 (`Options`)**:
  * **`temperature: 0.3`**: 较低的温度值能让代码生成更加精确、稳定。
  * **`maxTokens: 4096`**: 对话和生成的最大上下文输出长度。
  * **`debounceDelay: 1000`**: 代码自动补全的防抖时间设置为 1000 毫秒（1秒），避免打字时频繁请求导致卡顿。
  * **`maxPromptTokens: 1024`**: 限制传递给代码补全的上下文 Token 数量，提升响应速度。

---

## 步骤三：验证生效

1. 保存 `config.yaml` 文件。
2. 检查本地服务器 `192.168.11.188` 上的 Ollama 服务是否已正常启动，并确认已下载该 Qwen3 Coder 模型。
3. 在 Continue 插件的对话框底部分支菜单中，选择 **Qwen3 Coder (Local Server)**。
4. 尝试进行一次对话或在编辑器中敲击代码，测试补全功能是否在 1 秒后正常触发。
