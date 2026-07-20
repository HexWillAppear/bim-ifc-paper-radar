# Multi-topic Research Paper Radar

这个项目用于每天自动收集三个平行主题的研究论文与工作：

- `bim-ifc`：BIM、IFC、openBIM、Industry Foundation Classes。
- `self-evolving-agent`：自进化、自改进与持续学习的 AI/LLM Agent。
- `hypergraph-rag`：使用超图进行知识组织、检索或推理的 RAG。

采集结果去重后生成独立的 `JSON`、`CSV` 数据集，并汇总到一个可部署到 GitHub Pages 的静态页面。配置 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY` 后，还会为各主题的新论文生成中文 AI 摘要。

## 功能逻辑拆解

1. **定时触发**：GitHub Actions 每天 00:30 UTC 运行一次，约等于北京时间 08:30，也可以手动触发。
2. **并行主题采集**：同一次任务依次运行三个相互独立的主题模块；每个模块同时查询 OpenAlex 和 arXiv，默认回看最近 30 天。
3. **标准化**：把不同来源的标题、摘要、作者、发布日期、DOI、PDF 链接、来源期刊/会议统一成同一种记录结构。
4. **主题相关性判断**：每个主题维护独立的检索词、加权短语和共现规则；例如 BIM/IFC 缩写需要建筑语境，Hypergraph RAG 需要“超图”和“RAG”语义同时出现。
5. **去重合并**：按 DOI、论文 URL、来源 ID、标题指纹建立多键索引，只要任一键命中就合并同一篇论文。
6. **中文 AI 摘要**：如果存在 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`，采集器会按主题语境为缺失摘要的论文生成 `ai_summary_zh`，每个主题默认最多 20 篇，优先使用 DeepSeek。
7. **独立结果输出**：BIM/IFC 保留原有根路径；两个新主题分别写入 `data/self-evolving-agent/`、`data/hypergraph-rag/`，并同步到 `public/` 下的对应目录。
8. **自动部署**：Workflow 提交更新后的数据，然后把 `public/` 部署到 GitHub Pages。

更细的功能说明见 [docs/logic-breakdown.zh-CN.md](docs/logic-breakdown.zh-CN.md)。

## 本地运行

```bash
python -m pip install -e .
# 默认仍只采集 BIM/IFC，兼容原用法
python -m paper_radar.collect --days 365 --max-per-source 100

# 采集单个新主题
python -m paper_radar.collect --topic self-evolving-agent --days 30
python -m paper_radar.collect --topic hypergraph-rag --days 30

# 采集全部主题（GitHub Actions 使用此命令）
python -m paper_radar.collect --all-topics --days 30 --max-per-source 80

python -m unittest discover -s tests -v
```

运行时不依赖第三方 Python 包，采集请求使用标准库完成。

如果要在本地生成中文 AI 摘要：

```bash
set DEEPSEEK_API_KEY=你的密钥
python -m paper_radar.collect --days 30 --summarize-limit 5
```

生成结果：

- `data/papers.json`：带元数据的完整 JSON 数据。
- `data/papers.csv`：便于 Excel/表格软件打开的摘要表。
- `data/self-evolving-agent/papers.{json,csv}`：自进化 Agent 数据。
- `data/hypergraph-rag/papers.{json,csv}`：超图 RAG 数据。
- `public/index.html`：GitHub Pages 页面。
- `public/**/papers.json`：页面按主题加载的数据文件。

中文 AI 摘要字段：

- `ai_summary_zh`：中文摘要。
- `ai_summary_model`：生成摘要使用的模型。
- `ai_summary_updated_at`：摘要更新时间。

## GitHub 部署

1. 新建 GitHub 仓库并推送本项目。
2. 在仓库 `Settings -> Pages` 中将 Build and deployment 的 Source 设为 `GitHub Actions`。
3. 可选：在 `Settings -> Secrets and variables -> Actions` 添加 `OPENALEX_MAILTO`，让 OpenAlex 请求进入 polite pool。
4. 如需中文 AI 摘要，在 `Settings -> Secrets and variables -> Actions -> Secrets` 添加 `DEEPSEEK_API_KEY`；也可以添加 `OPENAI_API_KEY` 作为备用。
5. 可选：在 `Settings -> Secrets and variables -> Actions -> Variables` 添加：
   - `DEEPSEEK_MODEL`：默认 `deepseek-v4-flash`。
   - `OPENAI_MODEL`：默认 `gpt-5.5`。
   - `AI_SUMMARY_MODEL`：通用模型名变量，优先级低于 `DEEPSEEK_MODEL` 和 `OPENAI_MODEL`。
   - `AI_SUMMARY_LIMIT`：每天最多补多少篇中文摘要，默认 `20`。
6. 打开 `Actions -> Daily multi-topic paper radar`，手动运行一次；之后它会每天自动采集三个主题并部署。

## 调整检索范围

主题配置位于 `src/paper_radar/topics/`：

- `bim_ifc.py`：原 BIM/IFC 模块。
- `self_evolving_agent.py`：自进化 Agent 模块。
- `hypergraph_rag.py`：超图 RAG 模块。
- `base.py`：统一的主题配置与共现规则数据结构。

新增主题时定义一个 `TopicConfig`，再注册到 `topics/__init__.py` 即可复用采集、评分、摘要、存储和页面流程。

## 数据来源

- [OpenAlex Works API](https://docs.openalex.org/api-entities/works)
- [arXiv API](https://info.arxiv.org/help/api/index.html)
