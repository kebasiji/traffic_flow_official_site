# Carflow Puzzle 官方网站

「小车通通／小車通通／Carflow Puzzle」的三语静态官网，包含游戏介绍、支持与隐私政策。

- 官网域名：<https://carflowpuzzle.funvalvar.com>
- 开发者：Funvalvar
- 支持邮箱：<funvalvar@proton.me>

## 目录

- `src/`：三语正文、视觉样式和公开站点配置。
- `scripts/build.py`：生成静态页面，无需第三方Python依赖。
- `scripts/check.py`：检查九页结构、语言链接、本地资源及本地文件路径。
- `dist/`：完整可部署网站，包含HTML、图标、游戏截图和CSS。请一并保留；图片资源也保存在此目录中。

本仓库仅包含官网，不包含游戏工程、关卡定义、应用构建包或审核资料。

## 本地预览

使用Python 3.9或更高版本，在仓库根目录运行：

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8796 --bind 127.0.0.1 --directory dist
```

访问 <http://127.0.0.1:8796/>。也可直接双击`dist/index.html`打开英文首页，或`dist/zh-Hans/index.html`打开简体首页。

网站无需后端、数据库、npm或JavaScript。内部资源和页面跳转使用相对路径及显式`index.html`，支持本地文件、HTTP和子目录部署。canonical、语言SEO及分享URL使用配置的官网域名。

## 编辑与发布准备

- 修改`src/content.json`维护三语内容，修改`src/style.css`调整样式。
- `src/config.json`保存公开域名、App Store链接、支持邮箱、开发者名称及上架状态，不存放凭据。
- 当前上架状态为`released: false`，页面显示“即将上架”。确认App Store页面公开后，再将其改为`true`并重新构建。
- 发布目录为`dist/`。保留其中的目录结构，并配置服务器支持目录默认`index.html`。
- 部署后核对HTTPS、三语首页／支持／隐私九页、404页、邮件链接与图片加载。上传本仓库不会自动部署网站；本仓库未配置自动发布工作流。

英文页面位于根路径，简体和繁体分别位于`/zh-Hans/`、`/zh-Hant/`；各语言下的支持与隐私页面分别为`support/`和`privacy/`。

## 公开内容与权利

图标、游戏截图、文案和支持邮箱属于官网预期公开的内容。截图展示真实iOS游戏画面；公开仓库不附带游戏源码或购买验证实现。

© 2026 Funvalvar。仓库未附带开源许可证，未额外授予图标、截图、品牌或源码的复用许可。

`.gitignore`排除了Finder元数据、Python缓存、虚拟环境、编辑器配置、日志和常见凭据文件。新增文件在提交前仍应检查；忽略规则不会清除既有Git历史中的文件。
