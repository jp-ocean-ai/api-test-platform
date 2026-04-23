# API Test Platform

一个基于 Python 的 API 测试平台，前端使用 Vue 3，后端使用 Django，数据库使用 MySQL，测试执行与报告基于 pytest。

## 目标

这个项目面向接口测试场景，提供：

- 测试用例管理
- 环境管理（dev / test / prod）
- 接口定义与请求参数管理
- pytest 执行入口
- 测试报告展示
- 执行历史记录
- 用户登录与权限控制

## 技术栈

- Frontend: Vue 3 + Vite + Element Plus
- Backend: Django + Django REST Framework
- Database: MySQL
- Testing: pytest + pytest-html
- Task Queue: Celery（后续可加）
- Cache / Broker: Redis（后续可加）

## Monorepo Structure

```text
api-test-platform/
├── backend/        # Django backend
├── frontend/       # Vue3 frontend
├── docs/           # Design docs
└── README.md
```

## First Version Modules

- 用户模块
- 项目模块
- 环境模块
- 接口模块
- 测试用例模块
- 测试执行模块
- 测试报告模块

## Next

先完成第一版骨架，再逐步实现：

1. Django 后端项目初始化
2. Vue3 前端项目初始化
3. MySQL 配置与数据模型设计
4. pytest 执行器与报告解析
5. 平台页面联调
