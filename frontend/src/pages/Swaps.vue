<template>
  <div>
    <h1 class="brand">对调</h1>
    <p class="muted">先生成周表，再填写两格对调（day + task_id）</p>
    <div class="week-card" style="margin-bottom:12px">
      <p class="muted" style="margin:0 0 6px">
        填存储 day（0–6）；括号为该周钉锚（{{ anchor }}）下的星期，仅作对照，提交不做换算。
      </p>
      <p class="muted" style="margin:0 0 8px;font-size:12px">
        <span v-for="d in days" :key="d" class="chip">day {{ d }} → {{ labelFor(d, anchor) }}</span>
      </p>
      <label>A day <input type="number" v-model.number="form.a_day" /></label>
      <label>A task_id <input type="number" v-model.number="form.a_task" /></label>
      <label>B day <input type="number" v-model.number="form.b_day" /></label>
      <label>B task_id <input type="number" v-model.number="form.b_task" /></label>
      <button @click="request">申请对调</button>
    </div>
    <p v-if="err" class="err">{{ err }}</p>
    <ul class="list">
      <li v-for="s in rows" :key="s.id">
        #{{ s.id }} D{{ s.a_day }}/T{{ s.a_task }} ↔ D{{ s.b_day }}/T{{ s.b_task }}
        <span class="chip" :class="{ coral: s.status==='pending' }">{{ s.status }}</span>
        <button v-if="s.status==='pending'" style="margin-left:8px" @click="confirm(s.id)">确认改表</button>
      </li>
    </ul>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import { labelFor } from '../lib/anchor'
const rows = ref([])
const err = ref('')
const anchor = ref(0)
const days = [0,1,2,3,4,5,6]
const form = ref({ a_day: 0, a_task: 1, b_day: 1, b_task: 1 })
async function load() {
  rows.value = await api('/swaps')
  const b = await api('/weeks/1/board')
  anchor.value = b.week.week_anchor ?? 0
}
async function request() {
  err.value = ''
  try {
    await api('/weeks/1/swaps', { method: 'POST', body: JSON.stringify(form.value) })
    await load()
  } catch (e) { err.value = e.message }
}
async function confirm(id) {
  err.value = ''
  try { await api('/swaps/' + id + '/confirm', { method: 'POST', body: '{}' }); await load() }
  catch (e) { err.value = e.message }
}
onMounted(load)
</script>
