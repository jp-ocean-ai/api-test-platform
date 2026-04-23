# API Test Platform Architecture

## 1. Core Positioning

这是一个面向测试工程师和开发团队的 API 测试平台，用于统一管理项目、环境、接口定义、测试场景、执行任务和测试报告。

平台的核心目标不是“单接口调试”，而是“项目级接口测试编排”。

也就是说，它必须支持：
- 一个项目下维护多个接口
- 一个项目下维护多个环境
- 一个测试场景由多个步骤组成
- 后续步骤引用前序步骤的返回数据
- 多个项目之间严格隔离

## 2. Product Boundaries

### 当前适合做的事情
- 手工维护项目、环境、接口、用例
- 运行单个项目下的接口测试
- 查看 pytest-html / Allure 报告
- 逐步扩展到接口依赖与编排

### 当前不建议一开始做得太重的事情
- 分布式执行
- 多租户 SaaS
- 复杂审批流
- 大规模调度中心

## 3. Core Workflow

### V1 Workflow
1. 创建项目
2. 为项目配置环境
3. 在项目下维护接口定义
4. 在项目下维护测试场景
5. 选择环境执行单个场景或整个项目
6. 生成并查看 HTML / Allure 报告
7. 查看执行历史

### V1.5 Workflow
1. 创建项目
2. 为项目配置环境变量
3. 维护接口定义模板
4. 为测试场景添加多个步骤
5. 在步骤中定义请求覆盖、变量提取、断言规则
6. 执行时动态解析变量并串联上下文
7. 查看步骤级执行结果与最终报告

## 4. Backend Modules

- `users`: 用户、登录、权限
- `projects`: 项目管理
- `environments`: 环境配置与变量管理
- `apis`: 接口定义管理
- `testcases`: 测试场景管理
- `teststeps`: 测试步骤管理（建议新增）
- `executions`: 执行记录管理
- `reports`: 测试报告管理

## 5. Frontend Pages

### 必须有
- 登录页
- 项目管理页
- 环境管理页
- 接口管理页
- 用例管理页
- 执行历史页
- 报告详情页

### 建议补充
- 场景步骤编辑页
- 步骤执行结果详情页
- 项目概览页

## 6. Core Design Principles

### 6.1 项目隔离优先
所有核心资源都必须属于某个项目：
- Environment
- ApiDefinition
- TestCase
- TestStep
- TestExecution
- TestReport

后端所有查询默认按 `project_id` 过滤，前端切换项目后只展示当前项目数据。

### 6.2 接口定义和测试场景分离
- `ApiDefinition` 负责维护可复用的接口模板
- `TestCase` 负责表达测试意图和场景
- `TestStep` 负责描述一个场景中的某一步如何调用哪个接口

### 6.3 环境变量与运行时变量分层
- 环境变量来自 `Environment.variables`
- 场景运行时变量来自前置步骤的提取结果
- 执行时统一进入一个上下文容器进行模板渲染

### 6.4 报告不只看最终结果，也要能看到步骤结果
最终报告要保留，但平台内部还要能看到每一步的：
- 请求快照
- 响应快照
- 提取变量
- 断言结果
- 失败原因

## 7. Suggested Backend Stack

- Django
- Django REST Framework
- mysqlclient / PyMySQL
- pytest
- pytest-html
- Allure
- drf-spectacular or drf-yasg

## 8. Recommended Data Model

### 8.1 Project
- id
- name
- description
- owner
- is_active
- created_at
- updated_at

说明：项目是顶层隔离单位。

### 8.2 Environment
- id
- project
- name
- base_url
- variables_json
- is_active
- created_at
- updated_at

说明：环境仅在所属项目内有效，不允许跨项目复用。

### 8.3 ApiDefinition
- id
- project
- name
- method
- path
- headers_json
- query_params_json
- body_template_json
- expected_result_json
- is_active
- created_at
- updated_at

说明：接口定义只描述“模板”，不要承载场景级依赖逻辑。

### 8.4 TestCase
- id
- project
- name
- description
- default_environment（可选）
- enabled
- created_at
- updated_at

说明：`TestCase` 不再直接绑定单个 `api_definition`，而是作为“测试场景”容器。

### 8.5 TestStep（建议新增，核心模型）
- id
- project
- testcase
- order
- name
- api_definition
- environment（可选，默认继承 testcase 或运行参数）
- request_overrides_json
- extract_rules_json
- assertion_rules_json
- continue_on_failure
- enabled
- created_at
- updated_at

说明：
- 一个 `TestCase` 可以包含多个 `TestStep`
- `order` 用于确定执行顺序
- `request_overrides_json` 用于覆盖接口模板中的 headers/query/body/path 参数
- `extract_rules_json` 用于从响应中提取变量
- `assertion_rules_json` 用于定义状态码、JSONPath、文本等断言

### 8.6 TestExecution
- id
- project
- testcase（可选）
- environment（可选）
- trigger_user
- status
- started_at
- finished_at
- report_path
- summary_json
- created_at
- updated_at

说明：
- 可支持“执行整个项目”或“执行某个 testcase”
- `summary_json` 保留总数、成功数、失败数、耗时等聚合信息

### 8.7 ExecutionStepResult（建议新增）
- id
- execution
- testcase
- teststep
- order
- status
- request_snapshot_json
- response_snapshot_json
- extracted_variables_json
- assertion_result_json
- error_message
- started_at
- finished_at
- created_at
- updated_at

说明：这是平台内查看细粒度调试信息的关键模型。

## 9. Variable Resolution Design

执行时建议维护一个统一上下文，例如：

```json
{
  "env": {
    "base_url": "https://test.example.com",
    "token": "xxxx"
  },
  "runtime": {
    "user_id": 1001,
    "order_id": "OD20260424001"
  }
}
```

### 支持的变量来源
- 环境变量：`{{ base_url }}`、`{{ token }}`
- 前序步骤提取变量：`{{ user_id }}`、`{{ order_id }}`
- 系统变量：`{{ timestamp }}`、`{{ uuid }}`（后续可扩展）

### 支持的替换位置
- URL path
- Query params
- Headers
- Body

## 10. Extraction and Assertion Design

### 10.1 提取规则示例
```json
[
  {
    "name": "token",
    "from": "body",
    "expression": "$.data.token"
  },
  {
    "name": "user_id",
    "from": "body",
    "expression": "$.data.id"
  }
]
```

### 10.2 断言规则示例
```json
[
  {
    "type": "status_code",
    "expected": 200
  },
  {
    "type": "jsonpath_equals",
    "expression": "$.code",
    "expected": 0
  },
  {
    "type": "jsonpath_exists",
    "expression": "$.data.id"
  }
]
```

## 11. Execution Modes

### V1 必须支持
- 执行单个 TestCase
- 执行某个项目下全部启用 TestCase

### V1.5 建议支持
- 从某个 TestStep 开始执行
- 失败后继续/终止
- 重跑失败场景

## 12. Current Gap Assessment

### 已经有的
- 基础前后端骨架
- Project / Environment / ApiDefinition / TestCase / Execution 基础模型
- pytest-html / Allure 报告展示入口

### 当前缺口
- 项目、环境、接口、用例 CRUD 不完整
- `TestCase` 仍然是单接口结构
- 缺少 `TestStep`
- 缺少变量提取和依赖传递
- 缺少步骤级执行结果模型
- 缺少严格的项目内联动校验

## 13. Recommended Roadmap

### P0，先补齐可用性
- 项目 CRUD
- 环境 CRUD
- 接口 CRUD
- 用例 CRUD
- 项目隔离校验
- 按项目执行
- 基础环境变量替换

### P1，补齐平台核心能力
- 新增 `TestStep`
- 将 `TestCase` 从“单接口”升级为“测试场景”
- 响应变量提取
- 步骤间变量传递
- 步骤级执行结果展示

### P2，增强能力
- OpenAPI 导入
- 定时任务
- 通知集成
- 失败重跑
- 图表统计
- CI 集成

## 14. Implementation Recommendation

建议不要继续在现有 `TestCase.api` 单接口结构上硬堆功能。

更稳妥的路线是：
1. 保留现有 V1 能力可运行
2. 新增 `TestStep` 模型与 API
3. 逐步把执行器迁移到“场景 -> 步骤”模型
4. 最后再清理旧的单接口耦合字段

这样改造成本更低，也更不容易把现有功能全部打断。
