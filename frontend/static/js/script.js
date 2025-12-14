/* ============================================
   名侦探作业帮 - JavaScript 脚本
   ============================================ */

// ========== 创建星星 ==========
function createStars() {
    const starsContainer = document.getElementById('stars');
    if (!starsContainer) return;

    const starCount = 100;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 3 + 's';
        star.style.animationDuration = (Math.random() * 2 + 2) + 's';

        // 随机大小
        const size = Math.random() * 3 + 1;
        star.style.width = size + 'px';
        star.style.height = size + 'px';

        starsContainer.appendChild(star);
    }
}

// ========== 创建粒子 ==========
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;

    const symbols = ['🔍', '❓', '💡', '⚛️', '🧪', '📐', '✨', '🎯'];
    const particleCount = 15;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.textContent = symbols[Math.floor(Math.random() * symbols.length)];
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.fontSize = (Math.random() * 15 + 15) + 'px';

        particlesContainer.appendChild(particle);
    }
}

// ========== 切换学科 ==========
let currentSubject = 'physics';

function switchTab(subject) {
    if (currentSubject === subject) return;
    currentSubject = subject;

    const btnPhy = document.getElementById('btnPhysics');
    const btnChem = document.getElementById('btnChemistry');
    const submitBtn = document.getElementById('submitBtn');
    const inputArea = document.getElementById('problemInput');
    const mainCard = document.getElementById('mainCard');

    if (subject === 'physics') {
        // 物理模式
        btnPhy.className = 'tab-btn flex-1 py-5 text-center font-bold transition-all duration-300 flex items-center justify-center gap-3 tab-active-phy';
        btnChem.className = 'tab-btn flex-1 py-5 text-center font-bold transition-all duration-300 flex items-center justify-center gap-3 tab-inactive';

        submitBtn.classList.remove('chem-mode');
        inputArea.classList.remove('chem-mode');
        mainCard.classList.remove('glow-border-red');
        mainCard.classList.add('glow-border-blue');

        // 更新粒子颜色主题
        updateParticleTheme('physics');

    } else {
        // 化学模式
        btnChem.className = 'tab-btn flex-1 py-5 text-center font-bold transition-all duration-300 flex items-center justify-center gap-3 tab-active-chem';
        btnPhy.className = 'tab-btn flex-1 py-5 text-center font-bold transition-all duration-300 flex items-center justify-center gap-3 tab-inactive';

        submitBtn.classList.add('chem-mode');
        inputArea.classList.add('chem-mode');
        mainCard.classList.remove('glow-border-blue');
        mainCard.classList.add('glow-border-red');

        // 更新粒子颜色主题
        updateParticleTheme('chemistry');
    }

    // 添加切换动画效果
    mainCard.style.animation = 'none';
    mainCard.offsetHeight; // 触发重排
    mainCard.style.animation = 'glow-pulse 4s ease-in-out infinite';

    // 更新推荐讲解层级显示
    updateRecommendedLevelText(currentSubject);
}

// ========== 更新粒子主题 ==========
function updateParticleTheme(theme) {
    const particles = document.querySelectorAll('.particle');
    const physicsSymbols = ['🔍', '❓', '💡', '⚛️', '📐', '🎯', '⚡', '🌟'];
    const chemistrySymbols = ['🧪', '⚗️', '🔬', '💊', '🧬', '💥', '🌡️', '✨'];

    particles.forEach(particle => {
        const symbols = theme === 'physics' ? physicsSymbols : chemistrySymbols;
        particle.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    });
}

// ========== 图片预览 ==========
// 存储粘贴的图片文件
let pastedImageFile = null;

function previewImage(input) {
    if (input.files && input.files[0]) {
        showImagePreview(input.files[0]);
        // 清除粘贴的图片（因为用户选择了文件上传）
        pastedImageFile = null;
    }
}

// 通用的图片预览函数
function showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('imgPreview').src = e.target.result;
        document.getElementById('previewContainer').classList.remove('hidden');
        document.getElementById('uploadHint').classList.add('hidden');
    }
    reader.readAsDataURL(file);
}

// ========== 粘贴图片功能 ==========
function handlePaste(e) {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            e.preventDefault();
            const blob = items[i].getAsFile();
            if (blob) {
                // 创建一个带有正确文件名的File对象
                const timestamp = new Date().getTime();
                pastedImageFile = new File([blob], `pasted_image_${timestamp}.png`, { type: blob.type });
                showImagePreview(pastedImageFile);

                // 显示粘贴成功提示
                showPasteSuccess();
            }
            break;
        }
    }
}

// 显示粘贴成功提示
function showPasteSuccess() {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-green-500/90 text-white rounded-lg shadow-lg z-50 flex items-center gap-2';
    toast.innerHTML = '<i class="fa-solid fa-check-circle"></i> 图片已粘贴';
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// ========== 清除图片 ==========
function clearImage() {
    document.getElementById('previewContainer').classList.add('hidden');
    document.getElementById('uploadHint').classList.remove('hidden');
    // 清除input的值
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) fileInput.value = '';
    // 清除粘贴的图片
    pastedImageFile = null;
}

// ========== 深度思考模式 ==========
let deepThinkEnabled = false;

// ========== 个性化讲解（分层 + 画像）==========
let explainLevelOverride = 'auto'; // auto|basic|standard|advanced
let useProfileEnabled = true;
let personalizationEnabled = true;
let userRecommendations = null; // { physics: { recommended_level }, chemistry: { recommended_level } }

function setActiveExplainLevel(level) {
    explainLevelOverride = level || 'auto';
    const buttons = document.querySelectorAll('.dp-level-btn');
    buttons.forEach(btn => {
        const isActive = btn.dataset.level === explainLevelOverride;
        btn.classList.toggle('bg-neonCyan/20', isActive);
        btn.classList.toggle('border-neonCyan/50', isActive);
        btn.classList.toggle('text-white', isActive);
        btn.classList.toggle('bg-white/5', !isActive);
        btn.classList.toggle('border-white/10', !isActive);
        btn.classList.toggle('text-white/70', !isActive);
    });
}

function updateRecommendedLevelText(subject) {
    const el = document.getElementById('recommendedLevelText');
    if (!el) return;
    const rec = userRecommendations?.[subject]?.recommended_level;
    el.textContent = rec || 'auto';
}

async function fetchPersonalizationSummary() {
    try {
        const resp = await fetch('/api/user/personalization');
        if (!resp.ok) return;
        const data = await resp.json();
        if (!data.success) return;

        personalizationEnabled = !!data.settings?.personalization_enabled;
        userRecommendations = {
            physics: { recommended_level: data.recommendations?.physics?.recommended_level },
            chemistry: { recommended_level: data.recommendations?.chemistry?.recommended_level }
        };

        const useProfileToggle = document.getElementById('useProfileToggle');
        if (useProfileToggle) {
            if (!personalizationEnabled) {
                useProfileToggle.checked = false;
                useProfileToggle.disabled = true;
                useProfileEnabled = false;
            } else {
                useProfileToggle.disabled = false;
                useProfileEnabled = !!useProfileToggle.checked;
            }
        }

        const currentSubject = document.querySelector('.tab-btn.tab-active-phy') ? 'physics' : 'chemistry';
        updateRecommendedLevelText(currentSubject);
    } catch (e) {
        console.error('Fetch personalization error:', e);
    }
}

function initPersonalizationControls() {
    setActiveExplainLevel('auto');

    document.querySelectorAll('.dp-level-btn').forEach(btn => {
        btn.addEventListener('click', () => setActiveExplainLevel(btn.dataset.level));
    });

    const useProfileToggle = document.getElementById('useProfileToggle');
    if (useProfileToggle) {
        useProfileToggle.addEventListener('change', () => {
            useProfileEnabled = !!useProfileToggle.checked;
        });
    }
}

function initDeepThinkToggle() {
    const toggle = document.getElementById('deepThinkToggle');
    const label = document.getElementById('deepThinkLabel');

    if (toggle && label) {
        toggle.addEventListener('change', function() {
            deepThinkEnabled = this.checked;
            label.textContent = deepThinkEnabled ? '开启' : '关闭';

            // 添加视觉反馈
            const brainIcon = document.querySelector('.fa-brain');
            if (brainIcon) {
                if (deepThinkEnabled) {
                    brainIcon.classList.add('animate-pulse');
                    brainIcon.classList.remove('text-purple-400');
                    brainIcon.classList.add('text-purple-300');
                } else {
                    brainIcon.classList.remove('animate-pulse');
                    brainIcon.classList.remove('text-purple-300');
                    brainIcon.classList.add('text-purple-400');
                }
            }
        });
    }
}

// ========== 后端通信函数 ==========

// 发送纯文本问题到DeepSeek API (通过Flask后端)
async function sendTextQuery(question, subject = 'physics', deepThink = false, levelOverride = 'auto', useProfile = true) {
    try {
        const response = await fetch('/api/query/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                subject: subject,
                deep_think: deepThink,
                level_override: levelOverride,
                use_profile: useProfile
            })
        });

        const result = await response.json();

        if (response.ok) {
            return result;
        } else {
            throw new Error(result.error || '请求失败');
        }
    } catch (error) {
        console.error('发送文本查询失败:', error);
        throw error;
    }
}

// 发送图片问题到豆包API (通过Flask后端)
async function sendImageQuery(imageFile, question = '', subject = 'physics', deepThink = false, levelOverride = 'auto', useProfile = true) {
    try {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('question', question);
        formData.append('subject', subject);
        formData.append('deep_think', deepThink ? 'true' : 'false');
        formData.append('level_override', levelOverride);
        formData.append('use_profile', useProfile ? 'true' : 'false');

        const response = await fetch('/api/query/image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            return result;
        } else {
            throw new Error(result.error || '请求失败');
        }
    } catch (error) {
        console.error('发送图片查询失败:', error);
        throw error;
    }
}

// 发送base64图片问题到ChatGLM API (通过Flask后端)
async function sendBase64ImageQuery(base64Data, question = '', subject = 'physics') {
    try {
        const response = await fetch('/api/query/base64', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: base64Data,
                question: question,
                subject: subject
            })
        });

        const result = await response.json();

        if (response.ok) {
            return result;
        } else {
            throw new Error(result.error || '请求失败');
        }
    } catch (error) {
        console.error('发送Base64图片查询失败:', error);
        throw error;
    }
}

// ========== 处理问题提交 ==========

async function handleQuestionSubmit() {
    const questionText = document.getElementById('problemInput')?.value?.trim();
    const fileInput = document.querySelector('input[type="file"]');
    const currentSubject = document.querySelector('.tab-btn.tab-active-phy') ? 'physics' : 'chemistry';

    // 获取图片文件：优先使用文件上传，其次使用粘贴的图片
    const imageFile = fileInput?.files?.[0] || pastedImageFile;

    if (!questionText && !imageFile) {
        alert('请输入问题或上传图片！');
        return;
    }

    // 显示加载状态（根据深度思考模式显示不同提示）
    showLoadingState(deepThinkEnabled);

    try {
        if (imageFile) {
            // 有图片，使用豆包API
            const response = await sendImageQuery(
                imageFile,
                questionText,
                currentSubject,
                deepThinkEnabled,
                explainLevelOverride,
                useProfileEnabled
            );

            // 跳转到结果页面
            if (response.status === 'success' && response.session_id && response.redirect_url) {
                window.location.href = response.redirect_url;
            } else {
                showError(response.error || '服务器响应异常');
                hideLoadingState();
            }
        } else if (questionText) {
            // 纯文本，使用DeepSeek API - 跳转到结果页面
            const response = await sendTextQuery(
                questionText,
                currentSubject,
                deepThinkEnabled,
                explainLevelOverride,
                useProfileEnabled
            );

            // 跳转到结果页面
            if (response.session_id && response.redirect_url) {
                window.location.href = response.redirect_url;
            } else {
                showError('服务器响应异常');
                hideLoadingState();
            }
        }

    } catch (error) {
        showError(error.message);
        hideLoadingState();
    }
}

// ========== UI 状态管理 ==========

function showLoadingState(isDeepThink = false) {
    // 创建加载遮罩
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loadingOverlay';
    loadingOverlay.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50';

    const borderColor = isDeepThink ? 'border-purple-500' : 'border-neonCyan';
    const spinnerColor = isDeepThink ? 'border-t-purple-500' : 'border-t-neonCyan';
    const title = isDeepThink
        ? (window.i18n ? i18n.t('app.loading.deepTitle') : 'AI正在深度思考中...')
        : (window.i18n ? i18n.t('app.loading.title') : 'AI正在思考中...');
    const subtitle = isDeepThink
        ? (window.i18n ? i18n.t('app.loading.deepSubtitle') : '深度分析模式已启用，这可能需要更长时间，请耐心等待')
        : (window.i18n ? i18n.t('app.loading.subtitle') : '名侦探正在分析你的问题，请稍候');
    const icon = isDeepThink
        ? '<i class="fa-solid fa-brain text-4xl text-purple-400 animate-pulse"></i>'
        : '';

    loadingOverlay.innerHTML = `
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center max-w-md">
            ${icon ? `<div class="mb-4">${icon}</div>` : ''}
            <div class="relative w-20 h-20 mx-auto mb-4">
                <div class="w-20 h-20 border-4 ${borderColor}/20 rounded-full animate-spin"></div>
                <div class="absolute top-0 left-0 w-20 h-20 border-4 border-transparent ${spinnerColor} rounded-full animate-spin"></div>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">${title}</h3>
            <p class="text-white/70">${subtitle}</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);

    // 禁用提交按钮
    const submitButton = document.getElementById('submitBtn');
    if (submitButton) {
        submitButton.disabled = true;
    }
}

function hideLoadingState() {
    // 移除加载遮罩
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }

    // 恢复按钮状态
    const submitButton = document.getElementById('submitBtn');
    if (submitButton && submitButton.disabled) {
        submitButton.disabled = false;
    }
}

function displayResult(result) {
    // 创建或更新结果显示区域
    let resultContainer = document.getElementById('ai-response');
    if (!resultContainer) {
        resultContainer = document.createElement('div');
        resultContainer.id = 'ai-response';
        resultContainer.className = 'mt-6 p-4 bg-white/10 backdrop-blur-md rounded-lg border border-white/20';

        // 插入到提交按钮后面
        const submitButton = document.getElementById('submitBtn');
        if (submitButton) {
            submitButton.parentNode.insertBefore(resultContainer, submitButton.nextSibling);
        }
    }

    resultContainer.innerHTML = `
        <h3 class="text-lg font-bold mb-2 text-white">
            <i class="fa-solid fa-robot mr-2"></i>AI助教解答
        </h3>
        <div class="text-white/90">
            <p class="mb-2"><strong>问题类型:</strong> ${result.type === 'text' ? '文本问题' : '图片问题'}</p>
            <p class="mb-2"><strong>学科:</strong> ${result.subject === 'physics' ? '物理' : '化学'}</p>
            ${result.question ? `<p class="mb-2"><strong>你的问题:</strong> ${result.question}</p>` : ''}
            <div class="mt-3 p-3 bg-white/5 rounded border-l-4 border-cyan-400">
                <strong>解答:</strong> ${result.answer}
            </div>
            <p class="text-xs text-white/50 mt-2">时间: ${result.timestamp}</p>
        </div>
    `;

    // 添加出现动画
    resultContainer.style.animation = 'fade-in-up 0.5s ease-out';
}

function showError(message) {
    // 显示错误信息
    let resultContainer = document.getElementById('ai-response');
    if (!resultContainer) {
        resultContainer = document.createElement('div');
        resultContainer.id = 'ai-response';
        resultContainer.className = 'mt-6 p-4 bg-red-500/20 backdrop-blur-md rounded-lg border border-red-400/30';

        const submitButton = document.getElementById('submitBtn');
        if (submitButton) {
            submitButton.parentNode.insertBefore(resultContainer, submitButton.nextSibling);
        }
    }

    resultContainer.innerHTML = `
        <h3 class="text-lg font-bold mb-2 text-red-300">
            <i class="fa-solid fa-exclamation-triangle mr-2"></i>错误
        </h3>
        <p class="text-red-200">${message}</p>
    `;

    resultContainer.style.animation = 'fade-in-up 0.5s ease-out';
}

// ========== 用户相关功能 ==========

// 获取当前用户信息
async function fetchCurrentUser() {
    try {
        const response = await fetch('/api/auth/user');
        const data = await response.json();
        if (data.logged_in && data.user) {
            const userNameEl = document.getElementById('navUserName');
            if (userNameEl) {
                userNameEl.textContent = data.user.name;
            }
        }
    } catch (err) {
        console.error('获取用户信息失败:', err);
    }
}

// 登出功能
async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (err) {
        console.error('登出失败:', err);
        window.location.href = '/';
    }
}

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', function() {
    createStars();
    createParticles();

    // 获取用户信息
    fetchCurrentUser();

    // 初始化深度思考开关
    initDeepThinkToggle();

    // 初始化个性化讲解（层级 + 画像开关）
    initPersonalizationControls();
    fetchPersonalizationSummary();

    // 为提交按钮添加事件监听器
    const submitButton = document.getElementById('submitBtn');
    if (submitButton) {
        submitButton.addEventListener('click', handleQuestionSubmit);
    }

    // 添加Enter键提交支持（Ctrl+Enter）
    const textarea = document.querySelector('textarea');
    if (textarea) {
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                handleQuestionSubmit();
            }
        });
    }

    // 添加全局粘贴事件监听（支持 Ctrl+V 粘贴图片）
    document.addEventListener('paste', handlePaste);

    // 为上传区域添加拖放支持的视觉反馈
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('border-neonCyan', 'bg-neonCyan/10');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('border-neonCyan', 'bg-neonCyan/10');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('border-neonCyan', 'bg-neonCyan/10');

            const files = e.dataTransfer?.files;
            if (files && files[0] && files[0].type.startsWith('image/')) {
                showImagePreview(files[0]);
                pastedImageFile = files[0];
            }
        });
    }
});
