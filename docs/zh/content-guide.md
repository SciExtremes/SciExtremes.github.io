# 内容维护指南

[English](../en/content-guide.md)

共享记录管理事实与显示设置，英文和中文 Markdown 分别管理正文。同一事实只维护一份，内容之间通过稳定 ID 关联。示例 ID 和路径需替换为实际记录与素材，示例本身不属于正式网站内容。

## 文件与 ID

| 栏目 | 共享记录 | 双语页面 |
|---|---|---|
| Publications | `data/publications/{id}.yaml` | `content/{en,zh}/publications/{id}/index.md` |
| Data | `data/resources/{id}.yaml` | `content/{en,zh}/data/{id}/index.md` |
| Presentations | `data/presentations/{id}.yaml` | `content/{en,zh}/presentations/{id}/index.md` |
| News | `data/news/{id}.yaml` | `content/{en,zh}/news/{id}/index.md` |

记录 ID、YAML 文件名、页面目录和 `record_id` 必须一致。题名、日期或发表状态变化时，ID 保持稳定。输出路径使用小写，因此只在大小写上不同的 ID 会被拒绝。英文位于根路径，中文位于 `/zh/`。

```markdown
---
record_id: sample-talk
title: Localized title
summary: Localized summary
image_caption: Localized caption
---

Public description or abstract.
```

论文页面读取共享的正式题名，不在 Markdown 中填写 `title`；中文页可增加辅助译名 `translated_title`。显示设置、作者、日期、DOI、链接和主图放在 YAML 中。

## 通用字段与显示

`id / date` 必填。可选值和默认值定义在 [内容规范](../../data/content_schema.yaml) 中，由 Hugo 和 Python 共同读取。显式填写的值优先，包括 `false`。

| 字段 | 含义 |
|---|---|
| `date` | 有来源依据的日期，格式为 `YYYY-MM-DD` |
| `date_precision` | `day`（默认）、`month` 或 `year` |
| `end_date` | 可选结束日期，精度与开始日期一致 |
| `updated` | 可选资源更新日期，按日精度显示 |
| `image` | 相对 `assets/images/` 的路径；不用时可省略 |
| `image_fit` | `contain`（默认）或 `cover`；科学图和工具界面使用 `contain` |
| `image_alt.en / zh` | 双语图像描述；为空时使用本地化题名 |
| `links` | 有序的 `label / url` 对象；可选双语 `name` 和布尔 `download` |
| `paper_ids` | 关联论文 ID；默认空列表 |

月精度使用 `YYYY-MM-01`，年精度使用 `YYYY-01-01`。这些日期用于排序；页面与时间元数据只显示真实已知的精度。结束日期和更新日期不能早于开始日期。RSS 不为月、年精度生成完整时间戳。

| `display` 字段 | 默认值 | 含义 |
|---|---|---|
| `visible` | `true` | 进入列表、首页选择、关联区、搜索、RSS 和 sitemap |
| `featured` | `false` | 栏目精选；论文可多条，其他每类最多一条可见精选 |
| `home` | `false` | 选择进入首页亮点；必须同时设为栏目精选 |
| `order` | `0` | 共用展示优先级；正整数优先于自动日期排序，正数之间较小值靠前 |
| `image` | `false` | 启用共享主图 |
| `media` | `false` | 仅论文：启用媒体报道 |
| `attention` | `false` | 仅论文：有 DOI 时启用 Altmetric |

首页亮点是栏目精选中进一步选择的内容：`home: true` 必须同时设置 `featured: true`，即使暂时隐藏也要满足这一规则。栏目精选可以不进入首页。校验会报告矛盾，不会静默覆盖显式值。首页显示“亮点”，栏目显示“精选”；两处共用题名、摘要、事实和素材。精选不会自动开启图片、媒体报道或关注度。

论文按年份倒序分组，每年内先精选、再普通。同一年、同一精选状态内，先比较 `order`（正整数优先、较小值靠前），再按日期倒序、稳定 ID 升序排列。普通论文不能通过 `order` 越过精选论文，精选也不跨年份置顶。论文优先使用正式 `year`；缺少正式年份时使用来源日期的年份，状态说明继续保留。每篇论文只在完整引用列表中出现一次。

首页栏目顺序为 Publications、Data、Presentations、News。首页论文从 Publications 已排序列表中筛选 `home: true` 的记录，保持相对顺序。因为首页论文都属于精选，实际按年份倒序、`order`、日期倒序、稳定 ID 升序排列。较旧年份的论文不能用更高优先级越过较新年份；两处可以展示不同数量的论文，但共用同一份排序。未填写 `order` 时使用默认值 `0`，同组自动按日期排序；相同正数也按日期和 ID 决定稳定顺序。

Data、Presentations、News 每类最多一条可见精选和一条可见首页亮点；有首页亮点时，必须与栏目顶部精选是同一条。没有首页亮点时，可以单独设置栏目精选。这三个栏目的精选从普通年度列表中移出，避免同页重复；普通列表按年份、`order`、日期和 ID 排列。论文可有多条可见精选和多条首页亮点。数量限制只计算可见记录。

```yaml
display:
  visible: true
  featured: true
  home: true
  order: 10
  image: false
```

隐藏记录仍生成可访问的详情页，并标注 `noindex`；显示开关不是访问控制。私人材料不放入源码。未来日期不会预约发布，是否进入列表、搜索和关联入口仍由可见性决定。

## 链接、关联与素材

链接标签是两份 `i18n` 文件中的界面词条键。可选 `name.en / zh` 用来区分同类资源。第一项是主要操作；同一组中的重复 URL 按原顺序去重。支持 HTTPS、`mailto:` 和站点相对地址。

```yaml
links:
  - label: accessData
    url: https://example.org/dataset
    name:
      en: Historical dataset
      zh: 历史数据集
  - label: documentation
    url: https://example.org/documentation
```

媒体列表维护在 `data/media/{paper-id}.yaml`，包含 `outlet / title / url`。正文可使用 `{{< media paper="sample-paper" >}}` 和 `{{< paper id="sample-paper" >}}`，读取统一媒体列表与正式题名。引用的 ID 必须存在；隐藏目标会退出关联链接组。

```markdown
![Image description](/images/example/figure.svg)
[Supplement](/uploads/supplement.pdf)
{{< figure src="/images/example/figure.svg" alt="Image description" caption="Figure caption" >}}
```

全站图片放在 `assets/images/`，下载放在 `static/uploads/`。PNG/JPEG/WebP 会优化处理，SVG/GIF 保留矢量或动画信息。主图与详情图共享图像描述，图注独立维护。页面专属素材可放在 `index.md` 旁边，用相对链接引用。检查覆盖主图、正文内联与参考式链接、figure 短码和附件。删除内容时清理不再引用的素材。

## 论文与其他成果

必填字段为 `title / authors`。默认 `type: article / status: published`。作者使用完整正式署名，不在姓名中添加角色符号或称谓。

| `type` | 已发表或在线发表时的必要字段 | BibTeX |
|---|---|---|
| `article` | `journal / year` | `@article` |
| `conference` | `booktitle / year` | `@inproceedings` |
| `preprint` | 对应 `status: preprint`；可选 `repository` | `@misc` |
| `chapter` | `booktitle / year` | `@incollection` |
| `report` | `institution / year` | `@techreport` |

状态支持 `published / online_first / accepted / preprint`，分别表示已发表、在线发表、已接收和预印本。已接收成果与预印本可省略正式年份，分组和 BibTeX 使用来源日期的年份，并附带状态说明。取得确认信息后再补充。在线日期与正式发表年份可以不同。

可选字段包括 `doi / url / volume / number / pages / article_number / booktitle / publisher / institution / repository / identifier / author_roles / related_version_ids`。`pages` 和 `article_number` 二选一，文章编号导出为 `eid`。DOI 使用裸值。无 DOI 时可用 `url` 或 `links`，不显示 DOI 操作和 Altmetric；仍生成引用下载与题名、作者元数据。Altmetric 只展示官方加载的分数，不可用时显示空心中性圆环。

```yaml
id: sample-paper
date: '2027-01-01'
title: Example academic study
authors: [Example Researcher, Coauthor Name]
status: accepted
author_roles:
  equal_contribution: [Example Researcher, Coauthor Name]
  corresponding: [Example Researcher]
```

作者角色必须引用作者列表中的精确署名，页面显示 `* / †` 及说明，引用中的姓名不带标记。可选 `profile.author_names: [Example Researcher, E. Researcher]` 控制本人姓名加粗；省略时匹配个人资料中的英文姓名。

`related_version_ids` 关联同组记录。可以更新原记录以保留 URL，也可以保留不同版本并关联。两条可见版本分别列出，不自动统计或合并。资源地址维护在 Data，相关论文自动汇总读取。

## 报告

`event / kind` 必填。地点、活动网址、图片、材料和论文关联都可省略，只填写有来源依据的信息。

| 字段 | 支持的值 |
|---|---|
| `kind` | `poster / oral / seminar / lightning / other` |
| `event_type` | `conference / seminar / workshop / other`，或省略 |
| `role` | `contributed / invited / keynote`，或省略 |
| `participation` | `onsite / online / hybrid`，或省略 |

`other` 要求非空 `kind_label.en / zh`。可选 `event_label / location_label` 提供显示译名。`oral + seminar` 显示为研讨报告，受邀身份增加相应标签。主旨身份要求 oral/seminar 形式。线上或混合参与方式会显示，常规现场和投稿身份不增加重复标签。

```yaml
id: sample-talk
date: '2027-05-02'
end_date: '2027-05-04'
event: Example seminar
kind: oral
event_type: seminar
role: invited
participation: online
```

## 资源与动态

Data 必填共享 `name`。可选 `resource_type` 支持 `dataset / code / software / tool / other`。元信息包括 `version / license / doi / updated / related_version_ids`。

结构化 `citation` 必填 `title / authors / year`，可选 `publisher / doi / url`，生成详情页引用说明与 `@misc` 下载。资源 DOI 与引用 DOI 同时存在时必须一致。

```yaml
id: sample-dataset
date: '2027-01-01'
name: Example dataset
resource_type: dataset
version: '2.0'
license: CC BY 4.0
citation:
  title: Example dataset title
  authors: [Example Researcher]
  year: 2027
  publisher: Example archive
```

在双语正文中说明覆盖范围、定义、版本、使用和引用。News 可使用 `paper_ids / presentation_ids`，报告材料仍由对应报告记录维护。

## 研究与个人资料

`data/questions.yaml` 管理科学问题的标题、正文和代表成果。ID 使用唯一的小写安全锚点键，按列表顺序展示。可选 `label` 提供独立于锚点 ID 的简短显示编号。每个问题包含两种语言各三段正文，以及可为空的 `paper_ids / data_ids`。共用小标题分别表示研究意义与目标、研究方法与进展、下一步工作。问题 ID 与链接只用于 Research 内部。

桌面端编号在左、正文在右，手机端编号位于标题上方。标题、段落和成果共用正文列，不设置段落专属宽度或语言专属手动换行。

`data/framework.yaml` 管理框架文字和引用。术语使用双语 `label / detail` 和可选 `paper_id`。只有概念直接作为论文的主要研究对象、核心分析或主要结果时才关联。相同层级的术语具有一致字体样式，关联论文增加箭头。隐藏论文后，术语保留但不显示链接。

`data/research_layout.yaml` 独立配置显示方式，包括框架可见性、段落标签键、代表论文数量上限、阶段图标、色彩和调节连接。四阶段预设包含四个阶段、四个基础列和三个调节因素，前两个因素归为一组，不要求固定阶段或因素名称。设为 `framework_enabled: false` 时仅显示文字概览，并可省略 `data/framework.yaml`。科学问题继续使用三段结构。改变图的连接结构时，需要同步调整预设与渲染组件。

首页关键词和介绍位于 `data/focus.yaml`，背景和署名位于 `data/home.yaml`。个人资料、机构、教育、经历、简历和社交链接位于 `data/profile.yaml`。同一 CV 路径供首页与 About 使用，`languages` 控制社交链接的显示语言。导师显示名称可包含称谓，论文署名不包含称谓。

导航顺序位于 `config/_default/menus.yaml`，标签位于 `i18n`。字体、颜色、间距和容器宽度使用共用 CSS 变量。科学图片不裁切，各平台读取同一份正文。

## 创建与删除记录

```bash
npm run new -- presentations sample-talk --date 2027-01-01 --title-en "Presentation title" --title-zh "报告题目" --event "Example meeting" --kind oral
npm run new -- publications sample-paper --date 2027-01-01 --title-en "Official title" --title-zh "辅助译名" --author "Example Researcher" --status accepted
npm run new -- data sample-resource --date 2027-01-01 --title-en "Resource description" --title-zh "资源介绍" --name "Example resource"
npm run new -- news sample-story --date 2027-01-01 --precision year --title-en "News title" --title-zh "动态标题"
```

生成器创建 YAML 和 EN/ZH 页面，拒绝覆盖与大小写冲突。新记录显式设置 `visible: false`，完成公开正文并选择可见性后再构建。手工维护记录时，`archetypes/` 提供仅生成 Markdown 的辅助模板。

删除共享记录与两种语言的页面，清理 Research、媒体、记录和短码关联，再移除不再使用的素材。随后校验、构建和检查，命令见 [检查与测试](testing.md)。
