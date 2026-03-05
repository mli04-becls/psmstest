
# PSMS 方案A（Issue Form + Actions）一键包

## 包含内容
- `.github/ISSUE_TEMPLATE/product_add.yml` / `product_update.yml`：Issue 表单
- `.github/workflows/issue-product-sync.yml`：解析 Issue → 写入 YAML → 发 PR
- `scripts/issue_to_yaml.py`：解析脚本
- `.github/workflows/generate-dashboard-data.yml`：从 YAML 汇总生成 `dashboards/data/*.json`
- `scripts/generate_dashboard_data.py`：数据汇总脚本
- `dashboards/site/docs/manage.md`：Pages 管理入口（“新增/修改”按钮）

## 使用步骤
1. 将本包内容合入你的 **中心仓库**（包含 `products/`、`baseline/`、`dashboards/` 结构）。
2. 仓库 Settings → Actions → General：**Workflow permissions** 设为 *Read and write permissions*，允许创建 PR。  
3. 打开 Pages 站点（你已配置），访问 `/manage/` 页面，点击 “新增产品/修改产品”。
4. 提交 Issue 后会自动发起 PR → 合并后触发：
   - `generate-dashboard-data.yml` 生成最新 JSON
   - 你的 `publish-dashboards.yml` 构建并发布站点

> 注：Issue Forms 的语法与位置要求见 GitHub 文档（`/.github/ISSUE_TEMPLATE`）。PR 自动创建使用 `peter-evans/create-pull-request`。详见：
> - Issue Forms 语法与路径：GitHub Docs  
> - 自动创建 PR 的 Action：peter-evans/create-pull-request

