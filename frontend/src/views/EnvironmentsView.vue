<template>
  <div>
    <div class="page-title">环境管理</div>
    <el-card class="mb16">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="项目">
              <el-select v-model="form.project" placeholder="选择项目" style="width: 100%">
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="环境名">
              <el-input v-model="form.name" placeholder="例如 dev / test / prod" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Base URL">
              <el-input v-model="form.base_url" placeholder="https://api.example.com" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="变量 JSON">
              <el-input v-model="variablesText" type="textarea" :rows="4" placeholder='例如 {"token":"demo","tenant":"test"}' />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-switch v-model="form.is_active" />
          <span style="margin-left: 8px">启用</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveEnvironment">{{ form.id ? '保存环境' : '新增环境' }}</el-button>
          <el-button @click="resetForm">清空</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="环境名" />
        <el-table-column prop="base_url" label="Base URL" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editEnvironment(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="removeEnvironment(scope.row)">删除</el-button>
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

const items = ref([])
const projects = ref([])
const variablesText = ref('{}')
const form = ref({ id: null, project: null, name: '', base_url: '', variables: {}, is_active: true })

const resetForm = () => {
  form.value = { id: null, project: null, name: '', base_url: '', variables: {}, is_active: true }
  variablesText.value = '{}'
}

const loadAll = async () => {
  const [envRes, projectRes] = await Promise.all([
    client.get('environments/').catch(() => ({ data: [] })),
    client.get('projects/').catch(() => ({ data: [] })),
  ])
  items.value = envRes.data
  projects.value = projectRes.data
}

const saveEnvironment = async () => {
  if (!form.value.project || !form.value.name.trim() || !form.value.base_url.trim()) {
    ElMessage.warning('请先填写项目、环境名和 Base URL')
    return
  }
  try {
    form.value.variables = variablesText.value ? JSON.parse(variablesText.value) : {}
  } catch {
    ElMessage.error('变量 JSON 格式不正确')
    return
  }
  try {
    if (form.value.id) {
      await client.put(`environments/${form.value.id}/`, form.value)
      ElMessage.success('环境已更新')
    } else {
      await client.post('environments/', form.value)
      ElMessage.success('环境创建成功')
    }
    resetForm()
    await loadAll()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || '环境保存失败')
  }
}

const editEnvironment = (row) => {
  form.value = { ...row }
  variablesText.value = JSON.stringify(row.variables || {}, null, 2)
}

const removeEnvironment = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除环境「${row.name}」吗？`, '提示', { type: 'warning' })
    await client.delete(`environments/${row.id}/`)
    if (form.value.id === row.id) resetForm()
    ElMessage.success('环境已删除')
    await loadAll()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除环境失败')
  }
}

onMounted(loadAll)
</script>
