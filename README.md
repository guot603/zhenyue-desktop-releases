# 真玥桌面版下载

此仓库提供公开安装包、使用说明和校验清单，不包含私有应用源码、账号凭据或业务数据。

## 最新投标本地版

[Mac Apple Silicon 投标版 0.9.0-preview.13 下载助手](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-bid-local-0.9.0-preview.13/ZhenyueBid-macOS-Download.zip) · [完整分卷与版本说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-bid-local-0.9.0-preview.13)

[Windows x64 投标版 0.9.0-preview.14 下载助手](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-bid-local-0.9.0-preview.14/ZhenyueBid-Windows-Download.zip) · [完整分卷与版本说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-bid-local-0.9.0-preview.14)

同一个真玥桌面中使用对话与投标工作区，包含本地 OCR、企业资料库、响应矩阵、附表补录复用、证照附件排序和带目录页码的 Word 草稿。安装包自带运行环境、文档组件和本地模型。两端全量公开下载均经过完整文件 SHA-256 核验；Mac 安装版可正常启动，Windows 完成原生安装、离线 OCR 和投标文档回归检查。

Windows 完整解压助手后运行 `下载并安装.cmd`，或使用 `下载并安装.cmd --download-only` 仅下载、校验和解压，供离线分发。安装需要管理员权限；无需另装 Python 或 Office。Mac 打开 `下载并打开.command`，下载并校验 DMG 后把应用拖入“应用程序”。建议至少 16 GB 内存，Windows 预留 80 GB、Mac 预留 35 GB 磁盘。升级同一投标版会保留原本机项目和资料；旧普通桌面版的独立资料目录不会自动迁入。

报价、签章和正式提交仍由人工确认；自动匹配与风险提示不等于资格审核通过。此次安装/文档回归不调用生成模型，也未做客户账号验收。Windows 原生验收环境为 Windows Server 2025，不等于客户 Windows 10/11 实机验收。Windows 尚无发行者数字签名，Mac 尚未公证；均为手动安装预览，不自动推送升级。

## 历史普通桌面版 · 自带本地模型

[进入官网下载页](https://agent.adapora.cn/desktop) · [0.2.4-preview.4 公开预览发布说明与完整分卷](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-local-0.2.4-preview.4)

- [Windows x64 下载向导](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-local-0.2.4-preview.4/Zhenyue-Windows-Download.zip)：完整解压，运行 `下载并安装.cmd`。
- [Mac Apple Silicon 下载向导](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-local-0.2.4-preview.4/Zhenyue-macOS-Download.zip)：完整解压，打开 `下载并打开.command`。

向导下载所有分卷，校验每卷及完整安装包后才打开 Setup/DMG。需要离线安装时，先下载对应平台全部分卷，放在向导同一目录，向导会复用已校验文件。Windows 的 Setup 与旁边的 `model-bundle` 必须一起保留。

完整安装包包含 Qwen3.5-9B Q4_K_M、Ollama 0.40.0 和所需运行环境。安装时同时安装应用与模型，首次启动无需再下载模型。建议内存 16 GB 起，复杂任务 32 GB；下载、解压、安装期间 Windows 预留 80 GB，Mac 预留 35 GB。

支持 Windows 10/11 x64、macOS 14+ Apple Silicon；本版不支持 Intel Mac。用单位管理员已授权的真玥账号联网验证身份和授权；默认在本机保存资料、对话和草稿。主动选择云端模型并确认后，相应任务上下文会发给所选模型服务。

macOS 用户已有匹配本地模型时，可从应用“设置与说明 → 检查更新”获取经过签名清单和 SHA-256 校验的轻量升级包。首次安装仍须使用完整安装包。更新清单签名不代表 Apple 公证或 Windows 发行者签名。

开发与发行：蚁链（山东）人工智能科技有限公司，品牌 Adapora。

预览版支持个人知识库、本地资料分析、财务核对试点和 Word/Excel/PPTX 草稿，不包含云端 OA/财务写入、审批、语音或完整审计底稿能力的本地化。模型输出需要人工核对。本地 9B 的部分多轮任务可能只返回计划，需要进一步明确执行要求；以实际生成文件为准，不能只看文字“已完成”。

Windows 本次为公开手动试用验收版：安装和启动已校验，但真实模型任务在 2 线程、约 8 GB 的测试机上超时，尚待客户电脑验收，暂不推送自动升级。请使用[虚构试用资料与验收说明](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-local-0.2.4-preview.4/Zhenyue-Windows-Trial-Checklist.zip)检查实际表现。

Windows 尚未做发行者数字签名；Mac 尚无 Developer ID 签名或 Apple 公证。原生 Windows Server CI 检查不等同于 Windows 10/11 实机、重启、升级、真实账号和真实业务验收。系统阻止运行时请联系管理员核实来源，不要关闭系统防护。

本次新增修复：授权超时与连接失败使用中文提示；发送后的输入与附件按消息归位；旧 DOC 内容识别与扫描 PDF 本地文字识别；模型空响应恢复；Excel 合计从已保存文件回读复算。

## 原有桌面连接器

[桌面连接器下载与说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/desktop-preview-20260923)：Mac 1.0.3（macOS 14+，Intel/Apple Silicon）、Windows 1.0.2。

连接器供网页配对控制本机软件，与上面的独立桌面工作区不同。查询云端 OA/财务数据仍取决于本人单位和账套权限；操控本机软件需要本人配对、选定窗口并逐次确认。
