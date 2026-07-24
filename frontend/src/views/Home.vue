<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <nav class="home-nav">
      <div class="nav-brand">
        <el-icon :size="24"><Monitor /></el-icon>
        <span>C++ 课程智能体</span>
      </div>
      <div class="nav-actions">
        <el-button text @click="$router.push('/login')">登录</el-button>
        <el-button type="primary" @click="$router.push('/register')">免费注册</el-button>
      </div>
    </nav>

    <!-- 主视觉区 -->
    <section class="hero">
      <div class="hero-content">
        <h1>掌握 C++<br/>用 AI 驱动的方式</h1>
        <p>智能体辅助学习，个性化考核评估，RAG 知识库精准答疑<br/>从入门到精通，让每一行代码都有反馈</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/register')">立即开始</el-button>
          <el-button size="large" round @click="$router.push('/login')">已有账号</el-button>
        </div>
        <div class="hero-stats">
          <div class="stat"><strong>10+</strong><span>课程章节</span></div>
          <div class="stat"><strong>5</strong><span>考核题型</span></div>
          <div class="stat"><strong>AI</strong><span>智能答疑</span></div>
          <div class="stat"><strong>RAG</strong><span>知识检索</span></div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="code-preview">
          <div class="code-bar"><span></span><span></span><span></span></div>
          <pre><code><span class="kw">#include</span> <span class="str">&lt;iostream&gt;</span>
<span class="kw">int</span> <span class="fn">main</span>() {
  std::cout &lt;&lt; <span class="str">"Hello, C++ World!"</span>;
  <span class="kw">return</span> <span class="num">0</span>;
}</code></pre>
        </div>
      </div>
    </section>

    <!-- 功能介绍 -->
    <section class="features">
      <h2>平台核心功能</h2>
      <p class="features-sub">为 C++ 教学量身打造的智能学习系统</p>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon" style="background:#eef2ff;color:#6366f1;">
            <el-icon :size="28"><ChatDotRound /></el-icon>
          </div>
          <h3>AI 智能对话</h3>
          <p>基于课程资料的 RAG 增强问答，流式回复，追问提示，让学习无障碍</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon" style="background:#f0fdf4;color:#10b981;">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <h3>资料管理</h3>
          <p>支持 PDF、PPT、Word、Markdown 等多种格式上传，自动构建知识库</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon" style="background:#fff7ed;color:#f59e0b;">
            <el-icon :size="28"><Edit /></el-icon>
          </div>
          <h3>章节考核</h3>
          <p>选择题、判断题、简答题、编程题等多种题型，AI 自动批改并生成多维评价报告</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon" style="background:#fef2f2;color:#ef4444;">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <h3>学习分析</h3>
          <p>能力维度雷达图、学习进度追踪、错题本整理，全面掌握学习状态</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon" style="background:#f5f3ff;color:#8b5cf6;">
            <el-icon :size="28"><Monitor /></el-icon>
          </div>
          <h3>在线编程</h3>
          <p>内置 C++ 在线编译器，即写即运行，支持 C++17 标准</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon" style="background:#ecfdf5;color:#06b6d4;">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <h3>师生双系统</h3>
          <p>教师上传资料配置考核，学生学习答题看报告，角色分明</p>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="home-footer">
      <p>C++ 课程智能体系统 &copy; 2026</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.home-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px;
  background: rgba(255,255,255,.8);
  backdrop-filter: blur(10px);
  position: sticky; top: 0; z-index: 100;
  border-bottom: 1px solid #f1f5f9;
}
.nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-size: 18px; font-weight: 700; color: #1e293b;
}
.nav-actions { display: flex; gap: 12px; }

.hero {
  display: flex; align-items: center; justify-content: space-between;
  max-width: 1100px; margin: 0 auto; padding: 80px 40px;
  gap: 60px;
}
.hero-content h1 {
  font-size: 48px; font-weight: 800; color: #0f172a;
  line-height: 1.2; margin-bottom: 16px;
}
.hero-content p {
  font-size: 16px; color: #64748b; line-height: 1.8; margin-bottom: 32px;
}
.hero-actions { display: flex; gap: 12px; margin-bottom: 40px; }
.hero-stats { display: flex; gap: 32px; }
.hero-stats .stat strong {
  display: block; font-size: 24px; font-weight: 700; color: #1e293b;
}
.hero-stats .stat span {
  font-size: 12px; color: #94a3b8;
}

.code-preview {
  background: #1e293b; border-radius: 12px; overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.15);
  min-width: 380px;
}
.code-bar {
  display: flex; gap: 6px; padding: 12px 16px;
  background: #0f172a;
}
.code-bar span {
  width: 10px; height: 10px; border-radius: 50%;
}
.code-bar span:nth-child(1) { background: #ef4444; }
.code-bar span:nth-child(2) { background: #f59e0b; }
.code-bar span:nth-child(3) { background: #10b981; }
.code-preview pre {
  margin: 0; padding: 16px 20px 20px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 14px; line-height: 1.8; color: #e2e8f0;
}
.code-preview .kw { color: #c084fc; }
.code-preview .str { color: #34d399; }
.code-preview .fn { color: #60a5fa; }
.code-preview .num { color: #fbbf24; }

.features {
  max-width: 1100px; margin: 0 auto; padding: 80px 40px;
  text-align: center;
}
.features h2 {
  font-size: 32px; font-weight: 700; color: #0f172a; margin-bottom: 8px;
}
.features-sub { font-size: 16px; color: #94a3b8; margin-bottom: 48px; }
.feature-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}
.feature-card {
  background: #fff; border-radius: 12px; padding: 28px 24px;
  text-align: left; box-shadow: 0 1px 3px rgba(0,0,0,.04);
  transition: box-shadow .2s, transform .2s;
  border: 1px solid #f1f5f9;
}
.feature-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,.08); transform: translateY(-2px); }
.feature-icon {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
}
.feature-card h3 { font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
.feature-card p { font-size: 13px; color: #94a3b8; line-height: 1.7; margin: 0; }

.home-footer {
  text-align: center; padding: 32px;
  font-size: 13px; color: #94a3b8;
  border-top: 1px solid #f1f5f9;
}

@media (max-width: 768px) {
  .hero { flex-direction: column; text-align: center; padding: 40px 20px; }
  .hero-content h1 { font-size: 32px; }
  .hero-stats { justify-content: center; }
  .feature-grid { grid-template-columns: 1fr; }
  .code-preview { min-width: auto; width: 100%; }
}
</style>
