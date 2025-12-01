## ⚔️ 冲突解决指南 (Merge Conflict)

当你发起 PR 时，如果 GitHub 提示 <span style="color:red">**"Can't automatically merge"**</span>，说明你的分支落后了，且与主干有冲突。

**原则：谁开发，谁解决。** 管理员不负责修复冲突，请在本地解决后重新提交。

### 解决步骤

1. **切换回你的分支**：
   ```bash
   git checkout cky
   ```

2. **拉取远程 main 并尝试合并**：
   ```bash
   git fetch origin main
   git merge origin/main
   ```
   *(此时终端会报错 CONFLICT，提示自动合并失败)*

3. **手动修复**：
   打开报错的文件（编辑器通常会标红），找到冲突区域：
   ```python
   <<<<<<< HEAD
   # 这是你写的代码
   =======
   # 这是 main 分支里别人改过的代码
   >>>>>>> origin/main
   ```
   **操作**：决定保留哪段代码，并务必**删除** `<<<<<<<`, `=======`, `>>>>>>>` 这三行标记符号，然后保存文件。

4. **提交修复**：
   ```bash
   # 1.哪怕只是删了标记，也要 add 一下
   git add .

   # 2. 提交 (Git 会自动识别这是一个合并提交)
   git commit -m "解决与 main 分支的冲突"
   
   # 3. 推送回远程
   git push origin cky
   ```
   *(此时 PR 状态会自动变为绿色 Able to merge)*