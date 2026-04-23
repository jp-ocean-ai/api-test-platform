<template>
  <div>
    <div class="page-title">测试用例</div>
    <el-card class="mb16">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="项目">
              <el-select v-model="form.project" placeholder="选择项目" style="width: 100%" @change="onProjectChange">
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="环境">
              <el-select v-model="form.environment" placeholder="选择环境" clearable style="width: 100%">
                <el-option v-for="env in filteredEnvs" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="API">
              <el-select v-model="form.api" placeholder="选择 API" style="width: 100%">
                <el-option v-for="api in filteredApis" :key="api.id" :label="api.name" :value="api.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用例名称">
              <el-input v-model="form.name" placeholder="例如 登录成功用例" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="断言 JSON">
              <el-input v-model="assertionsText" placeholder='例如 {"status_code":200}' />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="createCase">新增测试用例</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column prop="environment" label="环境ID" width="100" />
        <el-table-column prop="api" label="API ID" width="100" />
        <el-table-column prop="enabled" label="启用" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const items = ref([])
const projects = ref([])
const apis = ref([])
const environments = ref([])
const assertionsText = ref('{"status_code":200}')
const form = ref({
  project: null,
  environment: null,
  api: null,
  name: '',
  request_data: {},
  assertions: { status_code: 200 },
  enabled: true,
})

const filteredApis = computed(() => apis.value.filter((item) => item.project === form.value.project))
const filteredEnvs = computed(() => environments.value.filter((item) => item.project === form.value.project))

const loadAll = async () => {
  const [casesRes, projectsRes, apisRes, envsRes] = await Promise.all([
    client.get('testcases/').catch(() => ({ data: [] })),
    client.get('projects/').catch(() => ({ data: [] })),
    client.get('apis/').catch(() => ({ data: [] })),
    client.get('environments/').catch(() => ({ data: [] })),
  ])
  items.value = casesRes.data
  projects.value = projectsRes.data
  apis.value = apisRes.data
  environments.value = envsRes.data
}

const onProjectChange = () => {
  form.value.environment = null
  form.value.api = null
}

const createCase = async () => {
  if (!form.value.project || !form.value.api || !form.value.name.trim()) {
    ElMessage.warning('请先填写项目、API 和用例名称')
    return
  }
  try {
    form.value.assertions = assertionsText.value ? JSON.parse(assertionsText.value) : {}
  } catch {
    ElMessage.error('断言 JSON 格式不正确')
    return
  }
  try {
    await client.post('testcases/', form.value)
    ElMessage.success('测试用例创建成功')
    form.value = {
      project: form.value.project,
      environment: null,
      api: null,
      name: '',
      request_data: {},
      assertions: { status_code: 200 },
      enabled: true,
    }
    assertionsText.value = '{"status_code":200}'
    await loadAll()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || '测试用例创建失败')
  }
}

onMounted(loadAll)
</script>
