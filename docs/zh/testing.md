# 检查与测试

[English](../en/testing.md)

使用最新构建输出执行检查：

```bash
npm run check:content
npm run build
npm run check
```

| 命令 | 检查范围 |
|---|---|
| `check:docs` | 中英文 README 与文档配对、章节结构、技术示例、语言链接、本地文件和锚点 |
| `check:content` | 字段、类型、默认值、ID、双语页面、关联、素材、个人资料和 Research 结构 |
| `check:model` | 支持的记录类型、可选字段、具体错误提示和默认值处理 |
| `check:interactions` | 菜单和焦点、搜索加载与失败、元信息转义及 Altmetric 状态 |
| `check:links` | 构建后的 URL、锚点、XML、引用、导航、精选标签、年内置顶、首页与栏目论文顺序一致性、显示开关及 Research 关联 |
| `check:scenarios` | 在临时目录测试内容类型，覆盖根路径与项目子路径 |
| `check:template` | 在临时副本中替换个人资料、内容、ID、导航顺序及框架开关 |
| `check:browser` | 真实浏览器渲染、响应式布局、搜索、键盘与模拟触控 |

`check` 依次执行文档、内容、模型、交互和输出检查。输出检查要求 `public/` 已存在；先重新构建，避免检查过期页面。命令返回非零状态表示失败。根据提示修正文件路径、字段或 URL，再运行对应检查。

## 浏览器准备

```bash
npx playwright install --with-deps chromium
npm run check:browser
```

需要多个浏览器内核时：

```bash
npx playwright install --with-deps chromium firefox webkit
TEST_BROWSERS=chromium,firefox,webkit npm run check:browser
```

测试从生成的 HTML 读取导航和语言，搜索词来自已索引页面的标题，不依赖特定研究主题。首页和栏目覆盖 320、390、520、521、760、761、768、1000、1001、1024、1279、1280、1440 和 1920px；详情覆盖 390/768/1440px。还检查横屏、文字放大两倍、Escape 与焦点恢复、本地搜索、关闭 JavaScript 后的导航，以及支持的模拟触控环境。

`TEST_SITE_DIR` 可指定其他构建目录。`TEST_SCREENSHOTS` 可指定截图输出的绝对路径；默认不写截图。生成的截图放在源码之外，或被忽略的 `test-results/` 内。

浏览器直接渲染构建文件，不请求外部服务。外部论文页面和实时 Altmetric 分数需要另外检查。浏览器内核与视口模拟不等于真实 iOS/Android 设备或 macOS Safari 的完整测试。

## 内容与个性化场景

```bash
npm run check:scenarios
npm run check:template
```

测试创建临时副本，完成校验和构建后在退出时删除，不改变正式内容。场景包括成果类型与状态、日期精度、口头与主旨报告、资源、引用、SVG/GIF、附件、版本和新增内容流程；还覆盖多篇精选论文、正式年份及缺少正式年份的分组、精选优先于普通排序、仅部分精选进入首页时的相对顺序、跨年份首页排序、隐藏及无精选状态、相同优先级和日期的稳定排序。模板检查替换站点特定信息并关闭可选框架，验证实现不依赖原始内容。

给临时场景增加浏览器检查：

```bash
TEST_SCENARIO_BROWSER=1 npm run check:scenarios
TEST_TEMPLATE_BROWSER=1 npm run check:template
```

## 项目路径与视觉检查

```bash
HUGO_BASEURL=https://example.org/academic-site/ npm run build
npm run check
npm run check:browser
```

移除环境变量覆盖后重新构建，即可恢复配置中的网站地址。在不同尺寸下检查容器边界、标题、完整科学图片、长姓名和题名、按钮组、框架术语链接及语言切换。部署后确认 PDF 和外部链接的实际行为。

GitHub Actions 执行文档、内容、模型、交互、场景和模板检查，然后构建正式页面并检查链接和 Chromium 渲染。依赖版本维护在锁文件、依赖要求与工作流中。Pull request 只校验；部署流程在检查成功后才发布。
