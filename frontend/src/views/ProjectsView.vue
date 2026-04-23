<template>
  <div>
    <div class="page-title">项目管理</div>
    <el-card class="mb16">
      <el-form :inline="true" :model="form">
        <el-form-item label="项目名">
          <el-input v-model="form.name" placeholder="请输入项目名" />
        </el-form-item>
        <el-form-item label="Owner">
          <el-input v-model="form.owner" placeholder="请输入 owner" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="请输入描述" style="width: 280px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="createProject">新增项目</el-button>
          <el-button @click="loadProjects">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="projects" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名" />
        <el-table-column prop="owner" label="Owner" />
        <el-table-column prop="description" label="描述" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const projects = ref([])
const form = ref({
  name: '',
  owner: '',
  description: '',
  is_active: true,
})

const loadProjects = async () => {
  try {
    const { data } = await client.get('projects/')
    projects.value = data
  } catch (error) {
    ElMessage.error('加载项目失败，请先确认后端已启动')
  }
}

const createProject = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请先输入项目名')
    return
  }
  try {
    await client.post('projects/', form.value)
    ElMessage.success('项目创建成功')
    form.value = { name: '', owner: '', description: '', is_active: true }
    await loadProjects()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || '项目创建失败')
  }
}

onMounted(loadProjects)
</script>
