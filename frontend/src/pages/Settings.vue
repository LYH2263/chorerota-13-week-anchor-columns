<template>
  <div>
    <h1 class="brand">设置</h1>
    <label>家庭名 <input v-model="household" /></label>
    <label>周锚日
      <select v-model.number="weekAnchor">
        <option v-for="(w, i) in weekdays" :key="i" :value="i">{{ i }} · {{ w }}</option>
      </select>
    </label>
    <button @click="save">保存</button>
    <p v-if="err" class="err">{{ err }}</p>
    <p class="muted" style="margin-top:8px">
      锚日 = 存储 day 0 对应的星期（0–6，越界拒写）。已生成周吃生成时钉入的锚，改这里不回溯旧周列标题。
    </p>
    <p class="muted" style="margin-top:16px">健康检查：{{ health }}</p>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const household = ref('')
const weekAnchor = ref(0)
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const health = ref('')
const err = ref('')
async function load() {
  const s = await api('/settings'); household.value = s.household || ''
  weekAnchor.value = Number(s.week_anchor ?? 0)
  const h = await api('/health'); health.value = JSON.stringify(h)
}
async function save() {
  err.value = ''
  try {
    await api('/settings', { method: 'PUT', body: JSON.stringify({ household: household.value, week_anchor: weekAnchor.value }) })
  } catch (e) { err.value = e.message }
}
onMounted(load)
</script>
