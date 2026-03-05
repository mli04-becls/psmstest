
# 产品管理（PSMS）

在此页面通过 **Issue 表单** 新建或修改产品信息。提交后会自动发起 PR，合并后仪表盘自动刷新。

<div class="cards">
  <a class="md-button" id="btn-add" href="#">新增产品</a>
  <a class="md-button" id="btn-update" href="#">修改产品信息</a>
</div>

<script>
(function(){
  // 动态推断 GitHub 仓库（适配 https://<owner>.github.io/<repo>/ 结构）
  const owner = location.hostname.split('.')[0];
  const repo = location.pathname.split('/').filter(Boolean)[0] || '';
  const add = document.getElementById('btn-add');
  const upd = document.getElementById('btn-update');
  const base = `https://github.com/${owner}/${repo}/issues/new?`
  if (add) add.href = base + 'template=product_add.yml';
  if (upd) upd.href = base + 'template=product_update.yml';
})();
</script>
