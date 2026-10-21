# 真玥桌面版下载

此仓库提供公开安装包、使用说明和校验清单，不包含私有应用源码、账号凭据或业务数据。

## 最新真玥统一投标版

- [Mac Apple Silicon 统一版 0.10.0-preview.35 下载助手](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-bid-local-0.10.0-preview.35/ZhenyueBid-0.10.0-preview.35-macOS-Download.zip) · [Mac 35 版完整分卷、校验值与版本说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-bid-local-0.10.0-preview.35)
- [Windows x64 统一版 0.10.0-preview.6 下载助手](https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-bid-local-0.10.0-preview.6/ZhenyueBid-Windows-Download.zip) · [Windows 6 版发布说明](https://github.com/guot603/zhenyue-desktop-releases/releases/tag/zhenyue-bid-local-0.10.0-preview.6)

Mac 35 版已完成安装版验收与公开下载校验。官网入口和在线升级清单尚未切换，当前请使用上面的下载助手手动升级。Windows 保持既有 6 版，本次未发布 Windows 35 版。

同一真玥、同一单位账号选择本机或云端任务。本机任务可选本机、平台自动、指定平台或自定义模型；发送真实资料前预览具体文字、模型与批次，并逐次确认。原件和本地项目不自动上传或同步，用量与在线对话留存按平台账号规则处理。

Mac 35 版在已有本地记忆中保存已确认的项目背景、修改意见和待办，支持查看、修改、删除及下次续接。对话资料、已选知识库和聊天原文共用检索入口，点击出处回读原文；资料变化后重新核验。保留 Qwen 4B/9B、本机语音转文字和 Serena 朗读。

继续提供本地 OCR、企业资料库、响应矩阵、企业/人员/业绩附表补录复用、原始证照附件排序合并和带目录页码的 Word 草稿。安装包自带运行环境、文档组件和本地模型，无需另装 Python 或 Office；账号验证需要联网，模型按需启动。

Windows 完整解压助手后运行 `下载并安装.cmd`，或使用 `下载并安装.cmd --download-only` 仅下载、校验和解压，供离线分发。安装需要管理员权限。Mac 完整解压助手后运行 `下载并打开.command`，校验 DMG 后把应用拖入“应用程序”替换旧版。建议至少 16 GB 内存，下载、组装与安装均预留 80 GB 磁盘。全部分卷和完整安装包均须通过 SHA-256 校验。

升级沿用 `cn.adapora.zhenyue.bid.local`，保留原投标项目和企业资料库；旧普通桌面版的独立资料目录不会自动迁入。Mac 35 版安装前后的 763 个既有文件哈希一致，记忆续接、统一检索、出处回读及 Serena 播放完成检查通过。公开下载校验覆盖全部分卷、完整 DMG 和下载助手；具体收据见发布页。

Mac 35 版预置独立签名升级入口，网站清单上线后可在“设置与说明 → 检查更新”使用；更早统一版尚未配置该通道。下载仍需用户确认，不自动替换应用。报价、签章、企业事实核验和正式提交仍由人工确认，生成结果须复核。

Windows 原生安装及文档测试在 Windows Server 2025 完成，客户 Windows 10/11 实机、真实账号及平台模型仍需验收。Windows 尚无发行者数字签名，Mac 尚未完成 Developer ID 签名和公证，均为手动安装预览。系统阻止时请管理员核实来源，不要关闭防护。

发布维护：`Public bid Windows download and native installation` 工作流可传入独立候选下载器的文件名和 SHA-256。先在 Windows Server 2022/2025 使用小型虚构夹具检查空 PATH、中文及特殊字符路径、32 位启动器、无 curl 回退和损坏拒绝，再在 Windows Server 2025 运行未修改的已发布下载器，完成原安装包下载、校验、安装、重装保留和窗口检查。候选测试不修改官网下载入口，也不替代客户 Windows 10/11 实机验收；公开仓不需要私有应用源码或客户凭据。

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
