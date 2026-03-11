<template>
  <div class="container">
    <h1>Obsidian 知识库助手</h1>

    <!-- 聊天记录显示区域 -->
    <div class="chat-box">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="msg.role === 'user' ? 'msg-user' : 'msg-bot'"
      >
        <span>{{ msg.content }}</span>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-box">
      <input
        v-model="question"
        @keyup.enter="sendQuestion"
        placeholder="输入问题，按回车发送"
      />
      <button @click="sendQuestion" :disabled="loading">
        {{ loading ? '思考中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// ref是Vue3的响应式变量，变量变化时页面自动更新
const question = ref('')        // 输入框里的内容
const messages = ref([])        // 聊天记录列表
const loading = ref(false)      // 是否正在等待回答

async function sendQuestion() {
  // 如果输入框是空的，不发送
  if (!question.value.trim()) return

  // 把用户的问题加入聊天记录
  messages.value.push({ role: 'user', content: question.value })

  const userQuestion = question.value
  question.value = ''           // 清空输入框
  loading.value = true          // 显示"思考中"

  // 发送POST请求到FastAPI后端
  const response = await fetch('http://192.168.26.128:8000/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: userQuestion })
  })

  const data = await response.json()

  // 把AI的回答加入聊天记录
  messages.value.push({ role: 'bot', content: data.answer })
  loading.value = false
}
</script>

<style>
body { margin: 0; font-family: sans-serif; background: #f5f5f5; }

.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}

h1 { text-align: center; color: #333; }

.chat-box {
  background: white;
  border-radius: 8px;
  padding: 20px;
  height: 400px;
  overflow-y: auto;
  margin-bottom: 16px;
  border: 1px solid #ddd;
}

.msg-user {
  text-align: right;
  margin: 8px 0;
}

.msg-user span {
  background: #4a9eff;
  color: white;
  padding: 8px 14px;
  border-radius: 16px;
  display: inline-block;
  max-width: 70%;
}

.msg-bot {
  text-align: left;
  margin: 8px 0;
}

.msg-bot span {
  background: #e8e8e8;
  color: #333;
  padding: 8px 14px;
  border-radius: 16px;
  display: inline-block;
  max-width: 70%;
}

.input-box {
  display: flex;
  gap: 8px;
}

.input-box input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.input-box button {
  padding: 10px 20px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.input-box button:disabled {
  background: #aaa;
  cursor: not-allowed;
}
</style>
