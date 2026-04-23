<template>
  <div>
    <div class="page-title">执行记录</div>
    <el-card class="mb16">
      <el-form :inline="true">
        <el-form-item label="项目">
          <el-select v-model="selectedProject" placeholder="选择项目" style="width: 260px">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runExecution">执行测试</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="project" label="项目ID" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <span>{{ formatStatus(scope.row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_user" label="触发人" />
        <el-table-column label="报告" min-width="320">
          <template #default="scope">
            <div class="report-links">
              <a v-if="scope.row.report_path" :href="`http://127.0.0.1:8001/api/executions/${scope.row.id}/html/`" target="_blank">pytest-html</a>
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
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const items = ref([])
const projects = ref([])
const selectedProject = ref(null)

const loadAll = async () => {
  const [execRes, projectsRes] = await Promise.all([
    client.get('executions/').catch(() => ({ data: [] })),
    client.get('projects/').catch(() => ({ data: [] })),
  ])
  items.value = execRes.data
  projects.value = projectsRes.data
  if (!selectedProject.value && projects.value.length) {
    selectedProject.value = projects.value[0].id
  }
}

const runExecution = async () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  try {
    await client.post('executions/run/', {
      project: selectedProject.value,
      trigger_user: 'web-ui',
    })
    ElMessage.success('执行记录已生成')
    await loadAll()
  } catch {
    ElMessage.error('执行失败')
  }
}

const formatStatus = (status) => {
  const statusMap = {
    pending: '待执行',
    running: '执行中',
    passed: '通过',
    failed: '已完成',
  }
  return statusMap[status] || status || '-'
}

onMounted(loadAll)
</script>
