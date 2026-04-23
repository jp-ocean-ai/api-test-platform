# API Test Platform Gap Analysis

## 1. Current State

当前项目已经具备基础骨架：
- Django + DRF 后端
- Vue3 + Element Plus 前端
- 项目、环境、接口、用例、执行、报告等基础模块
- pytest-html / Allure 报告查看入口

但从真实 API 测试平台角度看，当前仍属于“可演示原型”，还不是“可持续使用的平台”。

## 2. Main Gaps

### 2.1 CRUD 不完整
以下模块必须具备新增、修改、删除、列表、详情：
- Project
- Environment
- ApiDefinition
- TestCase

### 2.2 TestCase 结构过于单薄
当前 `TestCase` 直接绑定单个 `ApiDefinition`，这意味着：
- 一个用例只能测一个接口
- 无法表达登录 -> 创建 -> 查询 -> 删除这一类完整场景
- 无法优雅支持接口依赖

### 2.3 缺少接口关联能力
真实项目中，经常出现：
- A 接口返回 token
- B 接口使用 token
- C 接口使用 B 接口返回的业务 id

目前项目缺少：
- 返回值提取
- 运行时变量上下文
- 后续步骤引用前序结果

### 2.4 项目隔离还不够体系化
虽然模型中已有 project 外键，但仍需进一步保证：
- 所有查询默认按项目过滤
- 所有关联选择器只允许选择同一项目下的数据
- 不允许跨项目引用环境、接口、用例、步骤

### 2.5 执行结果粒度不够
当前更偏向“最终报告展示”，缺少步骤级调试信息：
- 请求快照
- 响应快照
- 提取变量
- 断言细节
- 失败原因

## 3. Must-Have Features

## V1
- 完整 CRUD
- 项目隔离
- 环境变量替换
- 单场景执行
- 项目级批量执行
- HTML / Allure 报告查看

## V1.5
- TestStep
- 多步骤场景执行
- 变量提取
- 变量传递
- 步骤级执行结果

## V2
- OpenAPI 导入
- 定时任务
- 通知集成
- 失败重跑
- CI 集成

## 4. Recommended Refactor Direction

建议以“测试场景 + 测试步骤”的模型替换当前“用例直接绑接口”的结构：

- TestCase: 场景
- TestStep: 步骤
- ApiDefinition: 可复用接口模板
- ExecutionStepResult: 每一步执行结果

## 5. Immediate Next Development Order

1. 补齐项目、环境、接口、用例 CRUD
2. 增加项目内数据联动校验
3. 为 TestCase 增加 description / default_environment
4. 新增 TestStep 模型
5. 新增 TestStep CRUD
6. 执行器支持按步骤串行执行
7. 增加 extract / assert 机制
8. 增加步骤结果查看页
