---
name: auto-skill
description: 解决问题后自动将方案沉淀为可复用 SKILL.md，越用越聪明
---
# auto-skill — 自动技能沉淀

## 触发条件
当你完成任何一个**非平凡任务**（涉及多步推理、跨文件操作、特定领域知识）后，主动执行以下步骤。

## 执行步骤

### 1. 判断是否需要沉淀
符合以下任一条件就应该沉淀为 Skill：
- 你用了 3+ 次工具调用才完成 → 说明流程不简单
- 涉及特定领域的操作流程（OCR/训练/部署/数据处理）
- 用户明确说"这个流程值得记住"
- 你说"如果下次遇到类似问题..."时

### 2. 设计 skill 结构
```
name: 简短英文标识（字母数字 _ - .）
description: ≤120 字中文一句话
body: 包含 # 技能名 + ## 背景 + ## 步骤 + ## 检查清单 + ## 常见问题
allowed_tools: 根据任务需要列出
runAs: subagent（复杂多步）或 inline（简单单步）
scope: project（推荐）
```

### 3. 调用 install_skill 注册
```js
// 伪代码
install_skill({
  name: "my-new-skill",
  description: "...",
  body: "...",
  scope: "project",
  runAs: "subagent" // 或 "inline"
})
```

### 4. 通知用户
- "已将 X 流程沉淀为 skill my-new-skill，下次通过 `/skill my-new-skill` 调用"
- 如果 scope=project，仅当前项目可见

## 编写 Skill 的最佳实践
- 步骤要可重演：别人或未来的你能照着做
- 包含验收标准：怎样算做完了
- 参数化：用 `{{variable}}` 标注需要用户提供的信息
- 举一反三：同类场景的变体

## 示例
```markdown
# baidu-ocr-fix — 百度 OCR 结果增强清洗

## 背景
百度 OCR 返回的结果有时候带多余空格、换行符错位、中英文混排等问题。

## 步骤
1. 读 OCR 结果文件
2. 用正则去除行内多余空格（保留段落间空行）
3. 修复中英文之间缺失的空格
4. 输出清理后的文本

## 验收
- 中文段落正常分词
- 数字和单位之间有空格
- 无连续 3+ 个空格
```
