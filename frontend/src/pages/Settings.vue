<template>
  <div>
    <h1 class="brand">设置</h1>
    <label>家庭名 <input v-model="household" /></label>
    <label>
      周起始锚日（0–6）
      <select v-model.number="weekAnchor">
        <option v-for="(w, i) in labels" :key="i" :value="i">{{ i }} · {{ w }}</option>
      </select>
    </label>
    <p class="muted">锚日只投影列标题，不改格位归属；改动只影响此后新生成的周，历史周标题保持不变。</p>
    <button @click="save">保存</button>
    <p v-if="err" class="err">{{ err }}</p>
    <p class="muted" style="margin-top:16px">健康检查：{{ health }}</p>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import { WEEKDAY_LABELS as labels } from '../lib/anchor'
const household = ref('')
const weekAnchor = ref(0)
const health = ref('')
const err = ref('')
async function load() {
  const s = await api('/settings')
  household.value = s.household || ''
  const n = parseInt(s.week_anchor, 10)
  weekAnchor.value = Number.isInteger(n) && n >= 0 && n <= 6 ? n : 0
  const h = await api('/health'); health.value = JSON.stringify(h)
}
async function save() {
  err.value = ''
  if (!Number.isInteger(weekAnchor.value) || weekAnchor.value < 0 || weekAnchor.value > 6) {
    err.value = '锚日越界：只接受 0–6'
    return
  }
  try {
    await api('/settings', {
      method: 'PUT',
      body: JSON.stringify({ household: household.value, week_anchor: weekAnchor.value }),
    })
  } catch (e) { err.value = e.message }
}
onMounted(load)
</script>
