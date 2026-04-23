<template>
  <div>
    <div class="page-title">API 管理</div>
    <el-card class="mb16">
      <el-form :model="form" label-width="88px">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="项目">
              <el-select v-model="form.project" placeholder="选择项目" style="width: 100%">
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="名称">
              <el-input v-model="form.name" placeholder="例如 登录接口" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Method">
              <el-select v-model="form.method" style="width: 100%">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="PATCH" value="PATCH" />
                <el-option label="DELETE" value="DELETE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Path">
              <el-input v-model="form.path" placeholder="例如 /api/login" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Expected">
              <el-input v-model="expectedText" placeholder='例如 {"code":200}' />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="saveApi">{{ form.id ? '保存 API' : '新增 API' }}</el-button>
          <el-button @click="resetForm">清空</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="method" label="Method" width="100" />
        <el-table-column prop="path" label="Path" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editApi(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="removeApi(scope.row)">删除</el-button>
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
const expectedText = ref('{"code":200}')
const form = ref({
  id: null,
  project: null,
  name: '',
  method: 'GET',
  path: '',
  headers: {},
  query_params: {},
  body_template: {},
  expected_result: { code: 200 },
  is_active: true,
})

const resetForm = () => {
  form.value = {
    id: null,
    project: null,
    name: '',
    method: 'GET',
    path: '',
    headers: {},
    query_params: {},
    body_template: {},
    expected_result: { code: 200 },
    is_active: true,
  }
  expectedText.value = '{"code":200}'
}

const loadAll = async () => {
  const [apisRes, projectsRes] = await Promise.all([
    client.get('apis/').catch(() => ({ data: [] })),
    client.get('projects/').catch(() => ({ data: [] })),
  ])
  items.value = apisRes.data
  projects.value = projectsRes.data
}

const saveApi = async () => {
  if (!form.value.project || !form.value.name.trim() || !form.value.path.trim()) {
    ElMessage.warning('请先填写项目、名称和 Path')
    return
  }
  try {
    form.value.expected_result = expectedText.value ? JSON.parse(expectedText.value) : {}
  } catch {
    ElMessage.error('Expected Result 必须是合法 JSON')
    return
  }
  try {
    if (form.value.id) {
      await client.put(`apis/${form.value.id}/`, form.value)
      ElMessage.success('API 已更新')
    } else {
      await client.post('apis/', form.value)
      ElMessage.success('API 创建成功')
    }
    resetForm()
    await loadAll()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || 'API 保存失败')
  }
}

const editApi = (row) => {
  form.value = { ...row }
  expectedText.value = JSON.stringify(row.expected_result || {}, null, 2)
}

const removeApi = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 API「${row.name}」吗？`, '提示', { type: 'warning' })
    await client.delete(`apis/${row.id}/`)
    if (form.value.id === row.id) resetForm()
    ElMessage.success('API 已删除')
    await loadAll()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除 API 失败')
  }
}

onMounted(loadAll)
</script>
