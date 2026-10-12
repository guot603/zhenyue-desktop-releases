# 真玥桌面版下载

此仓库提供公开安装包、使用说明和校验清单，不包含私有应用源码、账号凭据或业务数据。

## 独立桌面版 · 自带本地模型

[进入官网下载页](https://agent.adapora.cn/desktop) · [0.2.2-preview.3 公开预览发布说明与完整分卷](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-local-0.2.2-preview.3-preview.1)

- [Windows x64 下载向导](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-local-0.2.2-preview.3-preview.1/Zhenyue-Windows-Download.zip)：完整解压，运行 `下载并安装.cmd`。
- [Mac Apple Silicon 下载向导](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-local-0.2.2-preview.3-preview.1/Zhenyue-macOS-Download.zip)：完整解压，打开 `下载并打开.command`。

向导下载所有分卷，校验每卷及完整安装包后才打开 Setup/DMG。需要离线安装时，先下载对应平台全部分卷，放在向导同一目录，向导会复用已校验文件。Windows 的 Setup 与旁边的 `model-bundle` 必须一起保留。

完整安装包包含 Qwen3.5-9B Q4_K_M、Ollama 0.40.0 和所需运行环境。安装时同时安装应用与模型，首次启动无需再下载模型。建议内存 16 GB 起，复杂任务 32 GB；下载、解压、安装期间 Windows 预留 80 GB，Mac 预留 35 GB。

支持 Windows 10/11 x64、macOS 14+ Apple Silicon；本版不支持 Intel Mac。用现有真玥老板账号联网验证身份和授权；默认在本机保存资料、对话和草稿。主动选择云端模型并确认后，相应任务上下文会发给所选模型服务。

开发与发行：蚁链（山东）人工智能科技有限公司，品牌 Adapora。

预览版支持个人知识库、本地资料分析、财务核对试点和 Word/Excel/PPTX 草稿，不包含云端 OA/财务写入、审批、语音或完整审计底稿能力的本地化。模型输出需要人工核对。本地 9B 的部分多轮任务可能只返回计划，需要进一步明确执行要求；以实际生成文件为准，不能只看文字“已完成”。

Windows 尚未做发行者数字签名；Mac 尚无 Developer ID 签名或 Apple 公证。原生 Windows Server CI 检查不等同于 Windows 10/11 实机、重启、升级、真实账号和真实业务验收。系统阻止运行时请联系管理员核实来源，不要关闭系统防护。

## 原有桌面连接器

[桌面连接器下载与说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/desktop-preview-20260923)：Mac 1.0.3（macOS 14+，Intel/Apple Silicon）、Windows 1.0.2。

连接器供网页配对控制本机软件，与上面的独立桌面工作区不同。查询云端 OA/财务数据仍取决于本人单位和账套权限；操控本机软件需要本人配对、选定窗口并逐次确认。
