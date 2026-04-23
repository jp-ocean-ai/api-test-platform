<template>
  <div>
    <div class="page-title">环境管理</div>
    <el-card>
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="环境名" />
        <el-table-column prop="base_url" label="Base URL" />
        <el-table-column prop="project" label="项目ID" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import client from '../api/client'

const items = ref([])

onMounted(async () => {
  const { data } = await client.get('environments/').catch(() => ({ data: [] }))
  items.value = data
})
</script>
