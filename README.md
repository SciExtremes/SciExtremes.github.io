# SciExtremes

[English](README.en.md)

基于原生 Hugo 的中英文学术网站。共享 YAML 管理事实和显示设置，英文、中文 Markdown 分别管理正文。网站包含研究、论文、资源、报告、动态和个人简介，支持响应式布局与本地搜索。

## 快速开始

需要 Hugo **0.161.1** 普通版、Node.js **22+** 和 Python **3.10+**。命令使用 POSIX shell，可在 Linux、macOS 或 Windows WSL 中运行。

```bash
npm ci --ignore-scripts
python3 -m pip install -r requirements.txt
npm run check:content
npm run build
npm run check
npm run dev
```

`build` 生成 HTML 和 Pagefind 搜索索引。修改内容后重新构建，使搜索结果与页面一致。开发服务器会在终端显示本地地址。

## 个性化配置

| 配置内容 | 维护位置 |
|---|---|
| 网站地址与输出设置 | `config/_default/hugo.yaml` |
| 语言、导航与日期格式 | `config/_default/` 和 `i18n/` |
| 个人资料、机构、链接、肖像、简历与经历 | `data/profile.yaml` |
| 首页介绍、关键词与背景署名 | `data/focus.yaml` 和 `data/home.yaml` |
| 研究正文与代表成果 | `data/questions.yaml` 和 `data/framework.yaml` |
| 研究框架显示预设 | `data/research_layout.yaml` |
| 记录字段、默认值与支持的类型 | `data/content_schema.yaml` |
| 论文、资源、报告与动态的事实 | `data/` 中的对应目录 |
| 本地化题名、摘要、正文与图注 | `content/en/` 和 `content/zh/` |
| 图片与公开附件 | `assets/images/` 和 `static/uploads/` |
| 共用样式与组件 | `assets/` 和 `layouts/` |

仓库中的学术内容归其作者和来源所有。用于自己的站点时，替换个人资料、内容和素材，并更新相应署名。代码许可证不授予第三方图表或照片的使用权。

首页亮点由 `display.home` 选择，并要求 `display.featured: true`。论文可有多篇栏目精选，在各自年份内置顶；首页与 Publications 共用年份、精选状态、`display.order`、日期和 ID 的排序规则，筛选首页论文后保持相对顺序。完整规则见 [内容维护指南](docs/zh/content-guide.md)。

## 新增内容

```bash
npm run new -- presentations sample-talk --date 2027-01-01 --title-en "Presentation title" --title-zh "报告题目" --event "Example meeting" --kind oral
```

该命令创建共享记录与两种语言的页面，不覆盖已存在的 ID。完成正文、选择可见性后，再校验和构建。字段规则与示例见 [内容维护指南](docs/zh/content-guide.md)。

## 检查

```bash
npm run check:scenarios
npx playwright install --with-deps chromium
npm run check:browser
```

场景测试在临时目录中构建支持的内容类型。浏览器检查覆盖响应式布局、文字放大、菜单、搜索和触控操作。完整说明见 [检查与测试](docs/zh/testing.md)。

## 文档

- [部署说明](docs/zh/deployment.md)
- [内容维护指南](docs/zh/content-guide.md)
- [检查与测试](docs/zh/testing.md)
- [来源与署名](docs/zh/credits.md)
- [代码许可证](LICENSE.md)

构建输出、依赖、缓存和测试截图不进入源码版本管理。复制源码到新仓库时，包含 `.github/` 和 `.gitignore`。
