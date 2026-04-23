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
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveProject">{{ form.id ? '保存项目' : '新增项目' }}</el-button>
          <el-button @click="resetForm">清空</el-button>
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
        <el-table-column label="启用" width="80">
          <template #default="scope">{{ scope.row.is_active ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editProject(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="removeProject(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const projects = ref([])
const form = ref({ id: null, name: '', owner: '', description: '', is_active: true })

const resetForm = () => {
  form.value = { id: null, name: '', owner: '', description: '', is_active: true }
}

const loadProjects = async () => {
  try {
    const { data } = await client.get('projects/')
    projects.value = data
  } catch {
    ElMessage.error('加载项目失败，请先确认后端已启动')
  }
}

const saveProject = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请先输入项目名')
    return
  }
  try {
    if (form.value.id) {
      await client.put(`projects/${form.value.id}/`, form.value)
      ElMessage.success('项目已更新')
    } else {
      await client.post('projects/', form.value)
      ElMessage.success('项目创建成功')
    }
    resetForm()
    await loadProjects()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || '项目保存失败')
  }
}

const editProject = (row) => {
  form.value = { ...row }
}

const removeProject = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除项目「${row.name}」吗？`, '提示', { type: 'warning' })
    await client.delete(`projects/${row.id}/`)
    if (form.value.id === row.id) resetForm()
    ElMessage.success('项目已删除')
    await loadProjects()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除项目失败')
  }
}

onMounted(loadProjects)
</script>
