# Deployment

[简体中文](../zh/deployment.md)

## Configure the site

Set `baseURL` in `config/_default/hugo.yaml` to the final address, including a trailing slash.

| Site | Repository | URL example |
|---|---|---|
| User/organization site | `USERNAME.github.io` | `https://USERNAME.github.io/` |
| Project site | `academic-site` | `https://USERNAME.github.io/academic-site/` |

Replace profile, content and assets through the locations listed in [README](../../README.en.md). Maintain material credits as described in [Credits](credits.md). Keep the code license with reused code.

For a project-path check:

```bash
HUGO_BASEURL=https://example.org/academic-site/ npm run build
npm run check
```

The workflow obtains the actual Pages address from `actions/configure-pages` and overrides `baseURL` for production. Local builds use the configuration or `HUGO_BASEURL`.

## Initialize a repository

Use `main` as the default branch. Copy the source directory contents into the repository root, including `.github/` and `.gitignore`. The root should directly contain `package.json`, `config/`, `content/`, `data/` and `layouts/`.

```bash
git init -b main
git add .
git commit -m "Initialize academic website"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Replace `USERNAME / REPOSITORY`. Do not commit `public/`, root `resources/`, `node_modules/`, test outputs or logs. The anchored `/resources/` ignore rule excludes Hugo cache, not `data/resources/` records.

## GitHub Pages

Set the repository's Pages deployment source to GitHub Actions, then run **Validate and deploy Hugo**. If an initial run occurs before Pages is enabled, enable Pages and rerun the workflow. The repository must permit GitHub Actions.

- Push to `main`: validate, build and deploy.
- Pull request: validate and build.
- Manual workflow: validate, build and deploy.

Use the successful deployment's URL to review language switching, search, images, attachments and responsive layouts. Third-party service availability is independent of local checks.

## Custom domains

Configure the domain and HTTPS in Pages, set the required DNS records, update `baseURL`, and rebuild. Follow the hosting provider's current instructions.

## References

- [Create a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Configure publishing](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
