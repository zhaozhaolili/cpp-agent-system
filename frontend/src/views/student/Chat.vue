<template>
  <el-container style="height:100vh;">
    <el-aside width="220px"><AppSidebar /></el-aside>
    <el-container>
      <AppHeader />
      <div style="display:flex;flex:1;overflow:hidden;">
        <!-- 对话列表侧栏 -->
        <div class="conv-sidebar">
          <div style="padding:8px;border-bottom:1px solid #eee;">
            <el-button type="primary" size="small" style="width:100%;" @click="chatStore.newChat()">
              新对话
            </el-button>
          </div>
          <div class="conv-list">
            <div
              v-for="conv in chatStore.conversations"
              :key="conv.id"
              class="conv-item"
              @click="loadConversation(conv.id)"
            >
              <div class="conv-main">
                <div class="conv-title">{{ conv.title }}</div>
                <div class="conv-time">{{ formatDate(conv.created_at) }}</div>
              </div>
              <el-button
                class="conv-delete"
                text
                size="small"
                @click.stop="handleDeleteChat(conv.id)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-empty v-if="!chatStore.conversations.length" description="暂无对话" :image-size="40" />
          </div>
          <div v-if="chatStore.conversations.length" style="padding:6px 8px;border-top:1px solid #eee;">
            <el-button text size="small" type="danger" style="width:100%;" @click="handleClearAll">
              清空全部对话
            </el-button>
          </div>
        </div>

        <!-- 主聊天区 -->
        <div style="flex:1;display:flex;flex-direction:column;background:#f5f5f5;">
          <!-- 教师信息栏 -->
          <div style="padding:6px 16px;background:#fff;border-bottom:1px solid #eee;display:flex;align-items:center;gap:8px;">
            <el-icon><User /></el-icon>
            <span v-if="myTeacher" style="font-size:13px;">教师: <strong>{{ myTeacher.full_name || myTeacher.username }}</strong></span>
            <span v-else style="font-size:13px;color:#999;">未选择教师</span>
            <el-button size="small" text type="primary" @click="showTeacherDialog = true">
              {{ myTeacher ? '更换' : '选择教师' }}
            </el-button>
          </div>

          <div class="chat-area" ref="chatArea">
            <ChatMessage
              v-for="msg in chatStore.messages"
              :key="msg.id"
              :role="msg.role"
              :content="msg.content"
              :sources="msg.sources"
              :followups="msg.followups"
              @followup="chatStore.sendMessage"
            />
            <div v-if="chatStore.isGenerating" style="text-align:center;padding:8px;">
              <el-icon class="is-loading"><Loading /></el-icon>
            </div>
          </div>
          <ChatInput
            :disabled="chatStore.isGenerating"
            @send="handleSend"
            @stop="chatStore.stopGeneration"
          />
        </div>
      </div>
    </el-container>

    <!-- 教师选择弹窗 -->
    <el-dialog v-model="showTeacherDialog" title="选择教师" width="400px">
      <el-select v-model="selectedTeacherId" placeholder="请选择教师" style="width:100%;">
        <el-option v-for="t in teachers" :key="t.id"
          :label="(t.full_name || t.username) + ' (' + t.username + ')'" :value="t.id" />
      </el-select>
      <template #footer>
        <el-button @click="showTeacherDialog = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedTeacherId" @click="chooseTeacher">确认</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import AppHeader from '../../components/common/AppHeader.vue'
import AppSidebar from '../../components/common/AppSidebar.vue'
import ChatMessage from '../../components/chat/ChatMessage.vue'
import ChatInput from '../../components/chat/ChatInput.vue'
import { useChatStore } from '../../stores/chat'
import { getTeachers, getMyTeacher, selectTeacher } from '../../api/student'
import { getChatDetail, deleteChat, deleteAllChats } from '../../api/chat'
import { formatDate } from '../../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const chatStore = useChatStore()
const chatArea = ref(null)
const showTeacherDialog = ref(false)
const teachers = ref([])
const myTeacher = ref(null)
const selectedTeacherId = ref(null)

onMounted(async () => {
  chatStore.loadConversations()
  chatStore.loadHistory()

  try { const res = await getMyTeacher(); myTeacher.value = res.data } catch { myTeacher.value = null }
  try { const res = await getTeachers(); teachers.value = res.data } catch { /* */ }
})

async function handleSend(question) {
  await chatStore.sendMessage(question)
  // Reload conversation list after new message
  chatStore.loadConversations()
  scrollToBottom()
}

async function loadConversation(id) {
  try {
    const item = await getChatDetail(id)
    if (item) {
      chatStore.messages = [
        { role: 'user', content: item.question, id: item.id },
        { role: 'assistant', content: item.answer, id: item.id + '_a', sources: item.sources },
      ]
    }
    scrollToBottom()
  } catch (e) {
    ElMessage.error('加载对话失败')
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, () => scrollToBottom())

async function chooseTeacher() {
  try {
    await selectTeacher(selectedTeacherId.value)
    const res = await getMyTeacher()
    myTeacher.value = res.data
    showTeacherDialog.value = false
    ElMessage.success('教师选择成功')
  } catch { ElMessage.error('选择失败') }
}

async function handleDeleteChat(id) {
  try {
    await deleteChat(id)
    // 如果正在查看被删除的对话，清空消息
    const currentMsg = chatStore.messages[0]
    if (currentMsg && currentMsg.id === id) {
      chatStore.newChat()
    }
    chatStore.loadConversations()
    ElMessage.success('已删除')
  } catch { ElMessage.error('删除失败') }
}

async function handleClearAll() {
  try {
    await ElMessageBox.confirm('确定要清空所有对话历史吗？此操作不可恢复。', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteAllChats()
    chatStore.newChat()
    chatStore.loadConversations()
    ElMessage.success('已清空全部对话')
  } catch { /* 取消或失败 */ }
}
</script>

<style scoped>
.conv-sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.conv-list {
  flex: 1; overflow-y: auto;
}
.conv-item {
  display: flex; align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  transition: background .15s;
}
.conv-item:hover { background: #ecf5ff; }
.conv-item:hover .conv-delete { opacity: 1; }
.conv-main { flex: 1; overflow: hidden; min-width: 0; }
.conv-title {
  font-size: 13px; color: #333;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.conv-time {
  font-size: 11px; color: #999; margin-top: 2px;
}
.conv-delete {
  opacity: 0; flex-shrink: 0; color: #c0c4cc; transition: opacity .15s, color .15s;
}
.conv-delete:hover { color: #ef4444; }
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}
</style>
