# BIM/IFC Paper Radar

这个项目用于每天自动收集 BIM、IFC、openBIM、Industry Foundation Classes 相关论文，去重后生成 `JSON`、`CSV` 和一个可部署到 GitHub Pages 的静态页面。

## 功能逻辑拆解

1. **定时触发**：GitHub Actions 每天 00:30 UTC 运行一次，约等于北京时间 08:30，也可以手动触发。
2. **论文采集**：采集器同时查询 OpenAlex 和 arXiv，默认回看最近 30 天，避免漏掉延迟入库的论文。
3. **标准化**：把不同来源的标题、摘要、作者、发布日期、DOI、PDF 链接、来源期刊/会议统一成同一种记录结构。
4. **相关性判断**：优先命中 `building information modeling`、`industry foundation classes`、`openBIM` 等明确短语；对 `BIM`、`IFC` 这类歧义缩写，则要求它们和建筑、施工、AEC、数字孪生、设施管理等上下文共同出现。
5. **去重合并**：按 DOI、论文 URL、来源 ID、标题指纹依次去重，把每日新增结果并入历史库。
6. **结果输出**：生成 `data/papers.json`、`data/papers.csv`，并同步到 `public/papers.json`，供静态页面读取。
7. **自动部署**：Workflow 提交更新后的数据，然后把 `public/` 部署到 GitHub Pages。

更细的功能说明见 [docs/logic-breakdown.zh-CN.md](docs/logic-breakdown.zh-CN.md)。

## 本地运行

```bash
python -m pip install -e .
python -m paper_radar.collect --days 365 --max-per-source 100
python -m unittest discover -s tests -v
```

运行时不依赖第三方 Python 包，采集请求使用标准库完成。

生成结果：

- `data/papers.json`：带元数据的完整 JSON 数据。
- `data/papers.csv`：便于 Excel/表格软件打开的摘要表。
- `public/index.html`：GitHub Pages 页面。
- `public/papers.json`：页面加载的数据文件。

## GitHub 部署

1. 新建 GitHub 仓库并推送本项目。
2. 在仓库 `Settings -> Pages` 中将 Build and deployment 的 Source 设为 `GitHub Actions`。
3. 可选：在 `Settings -> Secrets and variables -> Actions` 添加 `OPENALEX_MAILTO`，让 OpenAlex 请求进入 polite pool。
4. 打开 `Actions -> Daily BIM/IFC paper radar`，手动运行一次；之后它会每天自动采集并部署。

## 调整检索范围

主要配置在 `src/paper_radar/config.py`：

- `OPENALEX_QUERIES`：OpenAlex 检索词。
- `ARXIV_QUERY_TERMS`：arXiv 检索词。
- `PHRASE_WEIGHTS`：相关性短语和权重。
- `CONTEXT_TERMS`：用于判断 `BIM`、`IFC` 缩写是否属于建筑信息模型语境。

## 数据来源

- [OpenAlex Works API](https://docs.openalex.org/api-entities/works)
- [arXiv API](https://info.arxiv.org/help/api/index.html)
