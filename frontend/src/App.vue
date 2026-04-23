<template>
  <el-container class="layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">API Test Platform</div>
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/projects">项目管理</el-menu-item>
        <el-menu-item index="/environments">环境管理</el-menu-item>
        <el-menu-item index="/apis">API 管理</el-menu-item>
        <el-menu-item index="/testcases">测试用例</el-menu-item>
        <el-menu-item index="/executions">执行记录</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">Vue3 + Django API 测试平台</el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>
