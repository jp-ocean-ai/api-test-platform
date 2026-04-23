<template>
  <div>
    <div class="page-title">执行记录</div>
    <el-card class="mb16">
      <el-form :inline="true">
        <el-form-item label="项目">
          <el-select v-model="selectedProject" placeholder="选择项目" style="width: 220px" @change="onProjectChange">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="场景">
          <el-select v-model="selectedTestcase" placeholder="全部场景" clearable style="width: 280px">
            <el-option v-for="testcase in filteredTestcases" :key="testcase.id" :label="testcase.name" :value="testcase.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runExecution">执行</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column prop="testcase" label="场景ID" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <span>{{ formatStatus(scope.row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="汇总" min-width="220">
          <template #default="scope">
            <span>总数 {{ scope.row.summary?.total || 0 }} / 通过 {{ scope.row.summary?.passed || 0 }} / 失败 {{ scope.row.summary?.failed || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_user" label="触发人" width="120" />
        <el-table-column label="报告" min-width="320">
          <template #default="scope">
            <div class="report-links">
              <a v-if="scope.row.report_path" :href="`http://127.0.0.1:8001/api/executions/${scope.row.id}/html/`" target="_blank">HTML 报告</a>
              <a v-if="scope.row.summary?.allure_html_path" :href="`http://127.0.0.1:8001/api/executions/${scope.row.id}/allure/`" target="_blank">Allure</a>
              <span v-if="!scope.row.summary?.allure_html_path" class="muted">{{ scope.row.summary?.allure_note || 'Allure 未生成' }}</span>
            </div>
          </template>
        </el-table-column>
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
const testcases = ref([])
const selectedProject = ref(null)
const selectedTestcase = ref(null)

const filteredTestcases = computed(() => testcases.value.filter((item) => item.project === selectedProject.value))

const loadAll = async () => {
  const [execRes, projectsRes, testcasesRes] = await Promise.all([
    client.get('executions/').catch(() => ({ data: [] })),
    client.get('projects/').catch(() => ({ data: [] })),
    client.get('testcases/').catch(() => ({ data: [] })),
  ])
  items.value = execRes.data
  projects.value = projectsRes.data
  testcases.value = testcasesRes.data
  if (!selectedProject.value && projects.value.length) {
    selectedProject.value = projects.value[0].id
  }
}

const onProjectChange = () => {
  selectedTestcase.value = null
}

const runExecution = async () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  try {
    const payload = {
      project: selectedProject.value,
      trigger_user: 'web-ui',
    }
    if (selectedTestcase.value) {
      payload.testcase = selectedTestcase.value
    }
    await client.post('executions/run/', payload)
    ElMessage.success(selectedTestcase.value ? '场景执行已生成' : '项目执行已生成')
    await loadAll()
  } catch {
    ElMessage.error('执行失败')
  }
}

const formatStatus = (status) => {
  const normalized = String(status || '').toUpperCase()
  const statusMap = {
    PENDING: '待执行',
    RUNNING: '执行中',
    PASSED: '通过',
    FAILED: '已完成',
  }
  return statusMap[normalized] || status || '-'
}

onMounted(loadAll)
</script>
