# 部署说明

[English](../en/deployment.md)

## 配置站点

在 `config/_default/hugo.yaml` 中将 `baseURL` 设为最终网站地址，保留结尾的斜杠。

| 站点类型 | 仓库名称 | 地址示例 |
|---|---|---|
| 用户或组织站点 | `USERNAME.github.io` | `https://USERNAME.github.io/` |
| 项目站点 | `academic-site` | `https://USERNAME.github.io/academic-site/` |

按照 [README](../../README.md) 列出的配置位置，替换个人资料、内容和素材。素材署名见 [来源与署名](credits.md)；复用代码时保留代码许可证。

检查项目子路径：

```bash
HUGO_BASEURL=https://example.org/academic-site/ npm run build
npm run check
```

部署工作流通过 `actions/configure-pages` 获取实际 Pages 地址，并覆盖生产构建的 `baseURL`。本地构建使用配置文件或环境变量 `HUGO_BASEURL`。

## 初始化仓库

使用 `main` 作为默认分支。将源码目录内的全部文件复制到仓库根目录，包含 `.github/` 和 `.gitignore`。根目录应直接包含 `package.json`、`config/`、`content/`、`data/` 和 `layouts/`。

```bash
git init -b main
git add .
git commit -m "Initialize academic website"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

替换 `USERNAME / REPOSITORY`。不提交 `public/`、根目录 `resources/`、`node_modules/`、测试输出或日志。以斜杠开头的 `/resources/` 忽略规则只排除 Hugo 缓存，不排除 `data/resources/` 中的正式记录。

## GitHub Pages

将仓库的 Pages 发布来源设为 GitHub Actions，再运行 **Validate and deploy Hugo**。如果首次执行发生在 Pages 启用之前，启用后重新运行工作流。仓库需要允许 GitHub Actions 执行。

- 推送到 `main`：检查、构建并部署。
- Pull request：检查和构建。
- 手动执行工作流：检查、构建并部署。

使用成功部署的网址检查语言切换、搜索、图片、附件和响应式布局。第三方服务是否可用不由本地检查决定。

## 自定义域名

在 Pages 中配置域名和 HTTPS，设置所需 DNS 记录，更新 `baseURL` 后重新构建。具体操作以托管服务提供方的当前说明为准。

## 参考资料

- [创建 GitHub Pages 站点](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [配置发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [自定义域名](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
