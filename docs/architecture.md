# API Test Platform Architecture

## 1. Core Positioning

这是一个面向测试工程师和开发团队的 API 测试平台，用于统一管理接口、测试用例、环境配置、执行任务和测试报告。

## 2. Core Workflow

1. 创建项目
2. 配置环境
3. 维护接口定义
4. 编写测试用例
5. 触发 pytest 执行
6. 生成并展示测试报告
7. 查看历史执行结果

## 3. Backend Modules

- `users`: 用户、登录、权限
- `projects`: 项目管理
- `environments`: 环境变量管理
- `apis`: 接口定义
- `testcases`: 测试用例管理
- `executions`: 测试执行记录
- `reports`: 测试报告管理

## 4. Frontend Pages

- 登录页
- 仪表盘
- 项目管理页
- 环境管理页
- 接口管理页
- 用例管理页
- 执行历史页
- 报告详情页

## 5. Suggested Backend Stack

- Django
- Django REST Framework
- mysqlclient / PyMySQL
- pytest
- pytest-html
- drf-spectacular or drf-yasg

## 6. Suggested Data Models

### Project
- id
- name
- description
- owner
- created_at

### Environment
- id
- project
- name
- base_url
- variables_json

### ApiDefinition
- id
- project
- name
- method
- path
- headers_json
- body_template
- expected_schema

### TestCase
- id
- project
- api_definition
- name
- request_data_json
- assertions_json
- enabled

### TestExecution
- id
- project
- trigger_user
- status
- started_at
- finished_at
- report_path
- summary_json

## 7. Phase Plan

### Phase 1
- 完成后端基础模型
- 完成前端基础页面框架
- 支持手工新增接口和测试用例
- 支持单次 pytest 执行
- 支持 html 报告查看

### Phase 2
- 支持定时执行
- 支持环境变量替换
- 支持批量执行
- 支持失败重跑
- 支持图表统计

### Phase 3
- 支持 CI 集成
- 支持 OpenAPI 导入
- 支持权限细分
- 支持通知（企业微信 / 邮件 / Telegram）
