<template>
  <div>
    <div class="page-title">测试场景</div>
    <el-card class="mb16">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="项目">
              <el-select v-model="form.project" placeholder="选择项目" style="width: 100%" @change="onProjectChange">
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="默认环境">
              <el-select v-model="form.default_environment" placeholder="选择默认环境" clearable style="width: 100%">
                <el-option v-for="env in filteredEnvs" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="兼容单接口">
              <el-select v-model="form.api" placeholder="可选" clearable style="width: 100%">
                <el-option v-for="api in filteredApis" :key="api.id" :label="api.name" :value="api.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场景名称">
              <el-input v-model="form.name" placeholder="例如 用户登录后查询资料" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="描述">
              <el-input v-model="form.description" placeholder="描述这个测试场景要验证什么" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="saveCase">{{ form.id ? '保存测试场景' : '新增测试场景' }}</el-button>
          <el-button @click="resetCaseForm">清空</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="mb16">
      <template #header>场景列表</template>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column prop="default_environment" label="默认环境" width="100" />
        <el-table-column label="步骤数" width="100">
          <template #default="scope">
            {{ scope.row.steps?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="启用" width="80">
          <template #default="scope">
            {{ scope.row.enabled ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editCase(scope.row)">编辑场景</el-button>
            <el-button size="small" @click="selectCase(scope.row)">编辑步骤</el-button>
            <el-button size="small" type="danger" plain @click="removeCase(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-if="selectedCase" class="mb16">
      <template #header>
        <div class="panel-header">
          <span>步骤管理, {{ selectedCase.name }}</span>
          <el-button size="small" @click="resetStepForm">清空步骤表单</el-button>
        </div>
      </template>

      <el-form :model="stepForm" label-width="110px">
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="顺序">
              <el-input-number v-model="stepForm.order" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="步骤名称">
              <el-input v-model="stepForm.name" placeholder="例如 登录获取 token" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="接口">
              <el-select v-model="stepForm.api" placeholder="选择接口" style="width: 100%">
                <el-option v-for="api in selectedCaseApis" :key="api.id" :label="api.name" :value="api.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="环境覆盖">
              <el-select v-model="stepForm.environment" placeholder="可选" clearable style="width: 100%">
                <el-option v-for="env in selectedCaseEnvs" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="失败继续">
              <el-switch v-model="stepForm.continue_on_failure" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用">
              <el-switch v-model="stepForm.enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="请求覆盖 JSON">
              <el-input v-model="stepRequestOverridesText" type="textarea" :rows="4" placeholder='例如 {"headers":{"Authorization":"Bearer {{token}}"},"body":{"user_id":"{{user_id}}"}}' />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="提取规则 JSON">
              <el-input v-model="stepExtractRulesText" type="textarea" :rows="4" placeholder='例如 [{"name":"token","from":"body","expression":"$.data.token"}]' />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="断言规则 JSON">
              <el-input v-model="stepAssertionRulesText" type="textarea" :rows="4" placeholder='例如 [{"type":"status_code","expected":200}]' />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="saveStep">{{ stepForm.id ? '保存步骤' : '新增步骤' }}</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="selectedCase.steps || []" style="width: 100%">
        <el-table-column prop="order" label="顺序" width="80" />
        <el-table-column prop="name" label="步骤名称" min-width="160" />
        <el-table-column prop="api" label="API ID" width="100" />
        <el-table-column prop="environment" label="环境ID" width="100" />
        <el-table-column label="失败继续" width="100">
          <template #default="scope">
            {{ scope.row.continue_on_failure ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editStep(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="removeStep(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const items = ref([])
const projects = ref([])
const apis = ref([])
const environments = ref([])
const selectedCase = ref(null)

const form = ref({
  project: null,
  environment: null,
  default_environment: null,
  api: null,
  name: '',
  description: '',
  request_data: {},
  assertions: { status_code: 200 },
  enabled: true,
})

const stepForm = ref({
  id: null,
  testcase: null,
  project: null,
  order: 1,
  name: '',
  api: null,
  environment: null,
  request_overrides: {},
  extract_rules: [],
  assertion_rules: [{ type: 'status_code', expected: 200 }],
  continue_on_failure: false,
  enabled: true,
})

const stepRequestOverridesText = ref('{}')
const stepExtractRulesText = ref('[]')
const stepAssertionRulesText = ref('[{"type":"status_code","expected":200}]')

const filteredApis = computed(() => apis.value.filter((item) => item.project === form.value.project))
const filteredEnvs = computed(() => environments.value.filter((item) => item.project === form.value.project))
const selectedCaseApis = computed(() => apis.value.filter((item) => item.project === selectedCase.value?.project))
const selectedCaseEnvs = computed(() => environments.value.filter((item) => item.project === selectedCase.value?.project))

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
  if (selectedCase.value) {
    selectedCase.value = items.value.find((item) => item.id === selectedCase.value.id) || null
  }
}

const onProjectChange = () => {
  form.value.environment = null
  form.value.default_environment = null
  form.value.api = null
}

const resetCaseForm = () => {
  form.value = {
    id: null,
    project: form.value.project,
    environment: null,
    default_environment: null,
    api: null,
    name: '',
    description: '',
    request_data: {},
    assertions: { status_code: 200 },
    enabled: true,
  }
}

const saveCase = async () => {
  if (!form.value.project || !form.value.name.trim()) {
    ElMessage.warning('请先填写项目和场景名称')
    return
  }
  try {
    if (form.value.id) {
      await client.put(`testcases/${form.value.id}/`, form.value)
      ElMessage.success('测试场景已更新')
    } else {
      await client.post('testcases/', form.value)
      ElMessage.success('测试场景创建成功')
    }
    resetCaseForm()
    await loadAll()
  } catch (error) {
    ElMessage.error(error?.response?.data?.name?.[0] || error?.response?.data?.detail || '测试场景保存失败')
  }
}

const selectCase = (row) => {
  selectedCase.value = row
  resetStepForm()
}

const editCase = (row) => {
  form.value = {
    ...row,
    steps: undefined,
  }
  selectCase(row)
}

const resetStepForm = () => {
  stepForm.value = {
    id: null,
    testcase: selectedCase.value?.id || null,
    project: selectedCase.value?.project || null,
    order: (selectedCase.value?.steps?.length || 0) + 1,
    name: '',
    api: null,
    environment: null,
    request_overrides: {},
    extract_rules: [],
    assertion_rules: [{ type: 'status_code', expected: 200 }],
    continue_on_failure: false,
    enabled: true,
  }
  stepRequestOverridesText.value = '{}'
  stepExtractRulesText.value = '[]'
  stepAssertionRulesText.value = '[{"type":"status_code","expected":200}]'
}

const parseJsonText = (text, fallback, label) => {
  try {
    return text ? JSON.parse(text) : fallback
  } catch {
    throw new Error(`${label} 格式不正确`)
  }
}

const saveStep = async () => {
  if (!selectedCase.value) {
    ElMessage.warning('请先选择一个测试场景')
    return
  }
  if (!stepForm.value.name.trim() || !stepForm.value.api) {
    ElMessage.warning('请先填写步骤名称并选择接口')
    return
  }

  try {
    stepForm.value.request_overrides = parseJsonText(stepRequestOverridesText.value, {}, '请求覆盖 JSON')
    stepForm.value.extract_rules = parseJsonText(stepExtractRulesText.value, [], '提取规则 JSON')
    stepForm.value.assertion_rules = parseJsonText(stepAssertionRulesText.value, [], '断言规则 JSON')
  } catch (error) {
    ElMessage.error(error.message)
    return
  }

  try {
    const payload = { ...stepForm.value, testcase: selectedCase.value.id, project: selectedCase.value.project }
    if (payload.id) {
      await client.put(`teststeps/${payload.id}/`, payload)
      ElMessage.success('步骤已更新')
    } else {
      await client.post('teststeps/', payload)
      ElMessage.success('步骤创建成功')
    }
    await loadAll()
    selectedCase.value = items.value.find((item) => item.id === selectedCase.value.id) || selectedCase.value
    resetStepForm()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '步骤保存失败')
  }
}

const editStep = (row) => {
  stepForm.value = {
    ...row,
  }
  stepRequestOverridesText.value = JSON.stringify(row.request_overrides || {}, null, 2)
  stepExtractRulesText.value = JSON.stringify(row.extract_rules || [], null, 2)
  stepAssertionRulesText.value = JSON.stringify(row.assertion_rules || [], null, 2)
}

const removeStep = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除步骤「${row.name}」吗？`, '提示', { type: 'warning' })
    await client.delete(`teststeps/${row.id}/`)
    ElMessage.success('步骤已删除')
    await loadAll()
    selectedCase.value = items.value.find((item) => item.id === selectedCase.value.id) || selectedCase.value
    resetStepForm()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除步骤失败')
    }
  }
}

const removeCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除场景「${row.name}」吗？`, '提示', { type: 'warning' })
    await client.delete(`testcases/${row.id}/`)
    if (selectedCase.value?.id === row.id) {
      selectedCase.value = null
    }
    ElMessage.success('场景已删除')
    await loadAll()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除场景失败')
    }
  }
}

onMounted(loadAll)
</script>
