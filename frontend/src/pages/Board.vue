<template>
  <div>
    <h1 class="brand">本周看板</h1>
    <p class="muted">周卡片网格 · round-robin 落位后可去「对调」申请交换</p>
    <p class="muted">锚日 {{ anchorLabel }} · {{ pinned ? '生成时钉入' : '预览（本周未生成，吃现行设置）' }}</p>
    <div style="display:flex;gap:8px;margin:12px 0">
      <button @click="generate">生成周表</button>
      <button class="ghost" @click="load">刷新</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <div class="week-grid">
      <article v-for="col in columns" :key="col.day" class="week-card">
        <header>Day {{ col.day }} · {{ col.label }}</header>
        <div v-for="a in byDay(col.day)" :key="a.id">
          <span class="chip">{{ a.task_title }}</span>
          <span class="chip coral">{{ a.member_name }}</span>
        </div>
        <p v-if="!byDay(col.day).length" class="muted">空</p>
      </article>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
const assigns = ref([])
const columns = ref([...Array(7)].map((_, day) => ({ day, label: '' })))
const pinned = ref(false)
const err = ref('')
const weekId = 1
const anchorLabel = computed(() => columns.value[0]?.label || '—')
function byDay(d) { return assigns.value.filter(a => a.day === d) }
async function load() {
  err.value = ''
  try {
    const b = await api('/weeks/' + weekId + '/board')
    assigns.value = b.assignments || []
    if (b.columns) columns.value = b.columns
    pinned.value = !!b.anchor_pinned
  } catch (e) { err.value = e.message }
}
async function generate() {
  err.value = ''
  try { await api('/weeks/' + weekId + '/generate', { method: 'POST', body: '{}' }); await load() }
  catch (e) { err.value = e.message }
}
onMounted(load)
</script>
