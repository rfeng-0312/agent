/**
 * 中文翻译字典
 * Chinese Translation Dictionary
 */
const translations_zh = {
    // ===== 通用 =====
    common: {
        appName: "名侦探作业帮",
        appSlogan: "AI智能学习平台",
        login: "登录",
        register: "注册",
        logout: "退出登录",
        submit: "提交",
        cancel: "取消",
        confirm: "确认",
        loading: "加载中...",
        error: "错误",
        success: "成功",
        back: "返回",
        backToHome: "返回首页",
        user: "用户",
        or: "或",
        profile: "个人主页",
        qaApp: "智能问答"
    },

    // ===== 首页 home.html =====
    home: {
        // 导航
        nav: {
            features: "功能特色",
            qa: "智能问答",
            diary: "成长日记",
            forum: "学习论坛"
        },
        // Hero 区域
        hero: {
            title1: "真相只有一个",
            title2: "学习亦是如此",
            subtitle: "基于 Agent 智能体技术，奥林匹克国际竞赛决赛题目准确率高达",
            accuracy: "90%",
            tag1: "DeepSeek + 豆包双引擎",
            tag2: "实时流式响应",
            tag3: "交叉验证准确性",
            ctaPrimary: "开始学习之旅",
            ctaSecondary: "了解更多",
            scrollHint: "向下滚动探索更多"
        },
        // 功能特色
        features: {
            sectionTitle: "三大核心功能",
            sectionSubtitle: "为你的学习之路保驾护航",
            qaCard: {
                title: "物理化学问答",
                desc: "专注于物理和化学学科，采用深度思考模式，像柯南破案一样层层推理，给出准确答案。",
                item1: "奥赛决赛级题目90%准确率",
                item2: "DeepSeek + 豆包交叉验证",
                item3: "图片识别自动解题",
                item4: "实时展示思考过程",
                btn: "立即体验"
            },
            diaryCard: {
                title: "成长日记",
                desc: "记录学习心路历程，AI智能分析你的情绪变化和学习状态，做你的专属学习顾问。",
                item1: "AI情感分析",
                item2: "学习状态追踪",
                item3: "个性化建议",
                item4: "成长可视化报告",
                btn: "开始记录",
                comingSoon: "即将上线"
            },
            forumCard: {
                title: "学习论坛",
                desc: "与志同道合的学习者交流讨论，分享解题技巧，互帮互助共同进步。",
                item1: "学科分类讨论",
                item2: "学霸答疑解惑",
                item3: "优质内容推荐",
                item4: "积分成就系统",
                btn: "进入论坛",
                comingSoon: "即将上线"
            }
        },
        // 统计数据
        stats: {
            accuracy: "奥赛题准确率",
            engines: "AI引擎协同",
            service: "全天候服务",
            free: "免费使用",
            accuracyValue: "90%",
            enginesValue: "2款",
            serviceValue: "24h",
            freeValue: "100%"
        },
        // 工作原理
        workflow: {
            sectionTitle: "智能解题原理",
            sectionSubtitle: "像名侦探一样，层层推理，步步验证",
            step1: { title: "题目输入", desc: "文字输入或图片上传" },
            step2: { title: "深度分析", desc: "AI展示完整思考过程" },
            step3: { title: "交叉验证", desc: "双AI互相检验答案" },
            step4: { title: "精准解答", desc: "输出完整解题步骤" }
        },
        // 页脚
        footer: {
            slogan: "真相只有一个，学习亦是如此",
            copyright: "© 2025 名侦探作业帮. All rights reserved."
        },
        // 登录弹窗
        loginModal: {
            title: "需要登录",
            desc: "登录后即可使用全部功能，开启你的学习之旅",
            loginBtn: "立即登录",
            registerBtn: "注册账号"
        },
        // 提示消息
        alerts: {
            diaryComingSoon: "日记功能即将上线，敬请期待！",
            forumComingSoon: "论坛功能即将上线，敬请期待！"
        }
    },

    // ===== 问答页 index.html =====
    app: {
        title: "名侦探作业帮 | 智慧解题",
        welcome: "今天遇到了什么难题？",
        welcomeSubtitle: "像侦探处理案件一样，逻辑清晰地解决它吧",
        // 学科切换
        tabs: {
            physics: "物理 Physics",
            chemistry: "化学 Chemistry"
        },
        // 输入区
        input: {
            label: "题目描述",
            hint: "支持输入公式和文本",
            placeholder: "在这里输入题目内容... 侦探正在等待你的案件"
        },
        // 图片上传
        upload: {
            label: "上传题目图片",
            hint: "点击或粘贴",
            hintText: "复杂的电路图或化学方程式？",
            hintSubtext: "直接拍下来上传，或",
            pasteHint: "Ctrl+V 粘贴截图"
        },
        // 深度思考
        deepThink: {
            label: "深度思考模式",
            desc: "启用后AI会进行更深入的分析，但耗时更长",
            on: "开启",
            off: "关闭"
        },
        // 提交按钮
        submitBtn: "开始解题",
        // 状态栏
        status: {
            normal: "系统运行正常"
        },
        // 页脚
        footer: {
            slogan: "真相永远只有一个"
        },
        // 加载状态
        loading: {
            title: "AI正在思考中...",
            subtitle: "名侦探正在分析你的问题，请稍候",
            deepTitle: "AI正在深度思考中...",
            deepSubtitle: "深度分析模式已启用，这可能需要更长时间，请耐心等待"
        },
        // 错误提示
        errors: {
            noInput: "请输入问题或上传图片！",
            serverError: "服务器响应异常"
        },
        // Toast
        toast: {
            imagePasted: "图片已粘贴"
        }
    },

    // ===== 结果页 result.html =====
    result: {
        title: "AI解答结果 | 名侦探作业帮",
        navTitle: "名侦探作业帮 - AI解答结果",
        continueBtn: "继续提问",
        // 问题卡片
        question: {
            title: "你的问题",
            physics: "物理",
            chemistry: "化学",
            timestamp: "提问时间："
        },
        // AI思考
        thinking: {
            title: "AI思考过程",
            hint: "(点击展开/收起)"
        },
        // AI解答
        answer: {
            title: "AI解答",
            loading: "AI正在思考中..."
        },
        // 深度思考验证
        verification: {
            thinkingTitle: "验证思考过程",
            resultTitle: "验证结果",
            loading: "正在验证答案...",
            stage1: "解答中",
            stage2: "待验证",
            stage1Done: "已完成",
            deepThinkLabel: "深度思考模式",
            analyzing: "正在深度分析问题..."
        },
        // 操作按钮
        actions: {
            copy: "复制答案",
            print: "打印",
            share: "分享"
        },
        // Toast
        toast: {
            copied: "答案已复制到剪贴板",
            linkCopied: "链接已复制到剪贴板"
        },
        // 分享
        share: {
            title: "名侦探作业帮 - AI解答",
            text: "来看看这道题的解答吧！"
        },
        // 错误
        error: {
            title: "错误",
            connectionFailed: "连接服务器失败，请刷新页面重试"
        }
    },

    // ===== 登录页 login.html =====
    login: {
        title: "登录 | 名侦探作业帮",
        heading: "登录你的账户",
        // 表单
        form: {
            accountLabel: "用户名 / 邮箱 / 手机号",
            accountPlaceholder: "请输入用户名、邮箱或手机号",
            passwordLabel: "密码",
            passwordPlaceholder: "请输入密码",
            submitBtn: "登 录",
            submitting: "登录中..."
        },
        // 链接
        links: {
            register: "注册账号",
            forgotPassword: "忘记密码？",
            backToHome: "返回首页"
        },
        // 找回密码弹窗
        resetModal: {
            title: "找回密码",
            desc: "请输入你的邮箱或手机号，我们将验证账号是否存在。",
            placeholder: "请输入邮箱或手机号",
            cancelBtn: "取消",
            nextBtn: "下一步"
        },
        // 消息
        messages: {
            success: "登录成功，正在跳转...",
            networkError: "网络错误，请稍后重试",
            enterAccount: "请输入邮箱或手机号",
            accountNotExist: "该账号不存在，请检查后重试"
        }
    },

    // ===== 注册页 register.html =====
    register: {
        title: "注册 | 名侦探作业帮",
        heading: "加入名侦探",
        subheading: "创建你的专属账户",
        // 表单
        form: {
            nameLabel: "姓名",
            namePlaceholder: "请输入你的姓名",
            accountLabel: "邮箱或手机号",
            accountPlaceholder: "请输入邮箱或手机号",
            accountHint: "用于登录和找回密码",
            passwordLabel: "密码",
            passwordPlaceholder: "请设置密码（至少6位）",
            confirmPasswordLabel: "确认密码",
            confirmPasswordPlaceholder: "请再次输入密码",
            submitBtn: "注 册",
            submitting: "注册中..."
        },
        // 可选部分
        optional: {
            title: "个性化设置（选填）",
            hint: "填写成绩后，AI将根据你的水平定制更适合的解答方式",
            physicsLabel: "物理成绩",
            chemistryLabel: "化学成绩",
            scorePlaceholder: "0-100",
            scoreUnit: "分"
        },
        // 链接
        links: {
            hasAccount: "已有账号？",
            login: "立即登录",
            backToHome: "返回首页"
        },
        // 消息
        messages: {
            passwordMismatch: "两次输入的密码不一致",
            success: "注册成功！正在跳转到登录页面...",
            networkError: "网络错误，请稍后重试"
        }
    },

    // ===== 重置密码页 reset_password.html =====
    resetPassword: {
        title: "重置密码 | 名侦探作业帮",
        heading: "重置密码",
        subheading: "设置你的新密码",
        // 账号信息
        accountInfo: {
            label: "正在为以下账号重置密码",
            loading: "加载中..."
        },
        // 表单
        form: {
            newPasswordLabel: "新密码",
            newPasswordPlaceholder: "请输入新密码（至少6位）",
            confirmPasswordLabel: "确认新密码",
            confirmPasswordPlaceholder: "请再次输入新密码",
            submitBtn: "重置密码",
            submitting: "重置中...",
            securityHint: "建议使用包含字母、数字的组合密码，以提高账户安全性"
        },
        // 链接
        links: {
            backToLogin: "返回登录页面"
        },
        // 消息
        messages: {
            passwordMismatch: "两次输入的密码不一致",
            success: "密码重置成功！正在跳转到登录页面...",
            networkError: "网络错误，请稍后重试"
        }
    },

    // ===== 日记页 =====
    diary: {
        pageTitle: "写日记 | 名侦探作业帮",
        listPageTitle: "我的日记 | 名侦探作业帮",
        detailPageTitle: "日记详情 | 名侦探作业帮",
        title: "今日成长记录",
        subtitle: "记录你的心情，小柯会陪伴你",
        moodLabel: "今天心情怎么样？",
        contentLabel: "写下今天的故事",
        placeholder: "今天发生了什么？有什么想说的吗...",
        characters: "字",
        save: "保存日记",
        saving: "保存中...",
        saved: "已保存",
        history: "历史记录",
        days: "天",
        myDiaries: "我的日记",
        empty: "还没有日记，开始记录你的第一篇吧！",
        startWriting: "开始写日记",
        writeNew: "写新日记",
        writeAnother: "再写一篇",
        viewHistory: "查看历史",
        loadMore: "加载更多",
        emptyError: "请写点什么再保存哦~",
        aiError: "小柯暂时无法回复，但你的日记已保存~",
        todayWritten: "今日已记录",
        // 日记详情页
        backToList: "返回列表",
        delete: "删除",
        deleteConfirmTitle: "确认删除",
        deleteConfirmMessage: "删除后无法恢复，确定要删除这篇日记吗？",
        confirmDelete: "确认删除",
        notFound: "日记不存在或已被删除",
        createdAt: "创建时间",
        contentTitle: "日记内容",
        aiResponseTitle: "小柯的回复",
        noAiResponse: "小柯还没有回复这篇日记",
        mood: {
            1: "很差",
            2: "不太好",
            3: "一般",
            4: "不错",
            5: "很棒"
        }
    },

    // ===== 个人主页 =====
    profile: {
        pageTitle: "个人主页 | 名侦探作业帮",
        memberSince: "加入时间",
        totalDiaries: "日记总数",
        streakDays: "连续天数",
        todayDiary: "今日打卡",
        quickAccess: "快捷入口",
        writeDiary: "写日记",
        writeDiaryDesc: "记录今天的心情和故事",
        diaryHistory: "日记历史",
        diaryHistoryDesc: "查看所有日记记录",
        qaApp: "智能问答",
        qaAppDesc: "AI帮你解答学习问题",
        recentDiaries: "最近日记",
        viewAll: "查看全部",
        noDiaries: "还没有日记，开始记录吧！",
        startWriting: "写第一篇"
    }
};

// 导出供其他模块使用
if (typeof window !== 'undefined') {
    window.translations_zh = translations_zh;
}
