/**
 * English Translation Dictionary
 */
const translations_en = {
    // ===== Common =====
    common: {
        appName: "Detective Study Helper",
        appSlogan: "AI-Powered Learning Platform",
        login: "Login",
        register: "Sign Up",
        logout: "Logout",
        submit: "Submit",
        cancel: "Cancel",
        confirm: "Confirm",
        loading: "Loading...",
        error: "Error",
        success: "Success",
        back: "Back",
        backToHome: "Back to Home",
        user: "User",
        or: "or",
        profile: "Profile",
        qaApp: "Smart Q&A"
    },

    // ===== Home Page home.html =====
    home: {
        // Navigation
        nav: {
            features: "Features",
            qa: "Smart Q&A",
            diary: "Growth Diary",
            forum: "Study Forum"
        },
        // Hero Section
        hero: {
            title1: "There's Only One Truth",
            title2: "So Is Learning",
            subtitle: "Based on Agent AI technology, achieving accuracy rate on International Olympiad finals of",
            accuracy: "90%",
            tag1: "DeepSeek + Doubao Dual Engine",
            tag2: "Real-time Streaming Response",
            tag3: "Cross-validation Accuracy",
            ctaPrimary: "Start Learning Journey",
            ctaSecondary: "Learn More",
            scrollHint: "Scroll down to explore more"
        },
        // Features Section
        features: {
            sectionTitle: "Three Core Features",
            sectionSubtitle: "Empowering your learning journey",
            qaCard: {
                title: "Physics & Chemistry Q&A",
                desc: "Focused on physics and chemistry, using deep thinking mode to reason step by step like a detective and provide accurate answers.",
                item1: "90% accuracy on Olympiad finals",
                item2: "DeepSeek + Doubao cross-validation",
                item3: "Image recognition auto-solving",
                item4: "Real-time thinking process display",
                btn: "Try Now"
            },
            diaryCard: {
                title: "Growth Diary",
                desc: "Record your learning journey, AI analyzes your emotions and study status, becoming your personal learning advisor.",
                item1: "AI Emotion Analysis",
                item2: "Study Status Tracking",
                item3: "Personalized Suggestions",
                item4: "Growth Visualization Report",
                btn: "Start Recording",
                comingSoon: "Coming Soon"
            },
            forumCard: {
                title: "Study Forum",
                desc: "Connect with like-minded learners, share problem-solving tips, and help each other grow together.",
                item1: "Subject-based Discussions",
                item2: "Expert Q&A Sessions",
                item3: "Quality Content Recommendations",
                item4: "Points & Achievement System",
                btn: "Enter Forum",
                comingSoon: "Coming Soon"
            }
        },
        // Statistics
        stats: {
            accuracy: "Olympiad Accuracy",
            engines: "AI Engines",
            service: "24/7 Service",
            free: "Free to Use",
            accuracyValue: "90%",
            enginesValue: "2",
            serviceValue: "24h",
            freeValue: "100%"
        },
        // Workflow
        workflow: {
            sectionTitle: "How It Works",
            sectionSubtitle: "Like a detective, reasoning step by step, verifying every detail",
            step1: { title: "Input Problem", desc: "Text input or image upload" },
            step2: { title: "Deep Analysis", desc: "AI shows complete thinking process" },
            step3: { title: "Cross Validation", desc: "Dual AI verifies the answer" },
            step4: { title: "Precise Solution", desc: "Output complete solution steps" }
        },
        // Footer
        footer: {
            slogan: "There's only one truth, so is learning",
            copyright: "© 2025 Detective Study Helper. All rights reserved."
        },
        // Login Modal
        loginModal: {
            title: "Login Required",
            desc: "Login to access all features and start your learning journey",
            loginBtn: "Login Now",
            registerBtn: "Sign Up"
        },
        // Alert Messages
        alerts: {
            diaryComingSoon: "Diary feature coming soon, stay tuned!",
            forumComingSoon: "Forum feature coming soon, stay tuned!"
        }
    },

    // ===== App Page index.html =====
    app: {
        title: "Detective Study Helper | Smart Problem Solving",
        welcome: "What problem did you encounter today?",
        welcomeSubtitle: "Like a detective solving a case, let's solve it with clear logic",
        // Subject Tabs
        tabs: {
            physics: "Physics",
            chemistry: "Chemistry"
        },
        // Input Area
        input: {
            label: "Problem Description",
            hint: "Supports formulas and text",
            placeholder: "Enter your problem here... The detective is waiting for your case"
        },
        // Image Upload
        upload: {
            label: "Upload Problem Image",
            hint: "Click or paste",
            hintText: "Complex circuit diagrams or chemical equations?",
            hintSubtext: "Take a photo and upload, or",
            pasteHint: "Ctrl+V to paste screenshot"
        },
        // Deep Think
        deepThink: {
            label: "Deep Thinking Mode",
            desc: "AI will perform deeper analysis when enabled, but takes longer",
            on: "ON",
            off: "OFF"
        },
        // Submit Button
        submitBtn: "Start Solving",
        // Status Bar
        status: {
            normal: "System running normally"
        },
        // Footer
        footer: {
            slogan: "There's always only one truth"
        },
        // Loading States
        loading: {
            title: "AI is thinking...",
            subtitle: "The detective is analyzing your problem, please wait",
            deepTitle: "AI is deep thinking...",
            deepSubtitle: "Deep analysis mode enabled, this may take longer, please be patient"
        },
        // Error Messages
        errors: {
            noInput: "Please enter a question or upload an image!",
            serverError: "Server response error"
        },
        // Toast
        toast: {
            imagePasted: "Image pasted"
        }
    },

    // ===== Result Page result.html =====
    result: {
        title: "AI Solution | Detective Study Helper",
        navTitle: "Detective Study Helper - AI Solution",
        continueBtn: "Ask Another Question",
        // Question Card
        question: {
            title: "Your Question",
            physics: "Physics",
            chemistry: "Chemistry",
            timestamp: "Asked at: "
        },
        // AI Thinking
        thinking: {
            title: "AI Thinking Process",
            hint: "(Click to expand/collapse)"
        },
        // AI Answer
        answer: {
            title: "AI Solution",
            loading: "AI is thinking..."
        },
        // Deep Think Verification
        verification: {
            thinkingTitle: "Verification Thinking Process",
            resultTitle: "Verification Result",
            loading: "Verifying answer...",
            stage1: "Solving",
            stage2: "Pending Verification",
            stage1Done: "Completed",
            deepThinkLabel: "Deep Thinking Mode",
            analyzing: "Performing deep analysis..."
        },
        // Action Buttons
        actions: {
            copy: "Copy Answer",
            print: "Print",
            share: "Share"
        },
        // Toast
        toast: {
            copied: "Answer copied to clipboard",
            linkCopied: "Link copied to clipboard"
        },
        // Share
        share: {
            title: "Detective Study Helper - AI Solution",
            text: "Check out this problem solution!"
        },
        // Error
        error: {
            title: "Error",
            connectionFailed: "Failed to connect to server, please refresh and try again"
        }
    },

    // ===== Login Page login.html =====
    login: {
        title: "Login | Detective Study Helper",
        heading: "Login to Your Account",
        // Form
        form: {
            accountLabel: "Username / Email / Phone",
            accountPlaceholder: "Enter username, email or phone number",
            passwordLabel: "Password",
            passwordPlaceholder: "Enter your password",
            submitBtn: "Login",
            submitting: "Logging in..."
        },
        // Links
        links: {
            register: "Sign Up",
            forgotPassword: "Forgot Password?",
            backToHome: "Back to Home"
        },
        // Reset Modal
        resetModal: {
            title: "Forgot Password",
            desc: "Enter your email or phone number to verify your account.",
            placeholder: "Enter email or phone number",
            cancelBtn: "Cancel",
            nextBtn: "Next"
        },
        // Messages
        messages: {
            success: "Login successful, redirecting...",
            networkError: "Network error, please try again later",
            enterAccount: "Please enter email or phone number",
            accountNotExist: "Account does not exist, please check and try again"
        }
    },

    // ===== Register Page register.html =====
    register: {
        title: "Sign Up | Detective Study Helper",
        heading: "Join Detective",
        subheading: "Create your account",
        // Form
        form: {
            nameLabel: "Name",
            namePlaceholder: "Enter your name",
            accountLabel: "Email or Phone",
            accountPlaceholder: "Enter email or phone number",
            accountHint: "Used for login and password recovery",
            passwordLabel: "Password",
            passwordPlaceholder: "Set password (at least 6 characters)",
            confirmPasswordLabel: "Confirm Password",
            confirmPasswordPlaceholder: "Enter password again",
            submitBtn: "Sign Up",
            submitting: "Signing up..."
        },
        // Optional Section
        optional: {
            title: "Personalization (Optional)",
            hint: "After filling in scores, AI will customize explanations based on your level",
            physicsLabel: "Physics Score",
            chemistryLabel: "Chemistry Score",
            scorePlaceholder: "0-100",
            scoreUnit: "pts"
        },
        // Links
        links: {
            hasAccount: "Already have an account?",
            login: "Login Now",
            backToHome: "Back to Home"
        },
        // Messages
        messages: {
            passwordMismatch: "Passwords do not match",
            success: "Registration successful! Redirecting to login page...",
            networkError: "Network error, please try again later"
        }
    },

    // ===== Reset Password Page reset_password.html =====
    resetPassword: {
        title: "Reset Password | Detective Study Helper",
        heading: "Reset Password",
        subheading: "Set your new password",
        // Account Info
        accountInfo: {
            label: "Resetting password for account",
            loading: "Loading..."
        },
        // Form
        form: {
            newPasswordLabel: "New Password",
            newPasswordPlaceholder: "Enter new password (at least 6 characters)",
            confirmPasswordLabel: "Confirm New Password",
            confirmPasswordPlaceholder: "Enter new password again",
            submitBtn: "Reset Password",
            submitting: "Resetting...",
            securityHint: "We recommend using a combination of letters and numbers for better security"
        },
        // Links
        links: {
            backToLogin: "Back to Login"
        },
        // Messages
        messages: {
            passwordMismatch: "Passwords do not match",
            success: "Password reset successful! Redirecting to login page...",
            networkError: "Network error, please try again later"
        }
    },

    // ===== Diary =====
    diary: {
        pageTitle: "Write Diary | Detective Study Helper",
        listPageTitle: "My Diaries | Detective Study Helper",
        detailPageTitle: "Diary Details | Detective Study Helper",
        title: "Today's Growth Record",
        subtitle: "Record your feelings, Xiao Ke will accompany you",
        moodLabel: "How do you feel today?",
        contentLabel: "Write today's story",
        placeholder: "What happened today? Anything you want to share...",
        characters: "characters",
        save: "Save Diary",
        saving: "Saving...",
        saved: "Saved",
        history: "History",
        days: "days",
        myDiaries: "My Diaries",
        empty: "No diary yet. Start recording your first one!",
        startWriting: "Start Writing",
        writeNew: "New Diary",
        writeAnother: "Write Another",
        viewHistory: "View History",
        loadMore: "Load More",
        emptyError: "Please write something before saving~",
        aiError: "Xiao Ke is temporarily unavailable, but your diary has been saved~",
        todayWritten: "Today recorded",
        // Diary detail page
        backToList: "Back to List",
        delete: "Delete",
        deleteConfirmTitle: "Confirm Delete",
        deleteConfirmMessage: "This action cannot be undone. Are you sure you want to delete this diary?",
        confirmDelete: "Confirm Delete",
        notFound: "Diary not found or has been deleted",
        createdAt: "Created at",
        contentTitle: "Diary Content",
        aiResponseTitle: "Xiao Ke's Response",
        noAiResponse: "Xiao Ke hasn't responded to this diary yet",
        mood: {
            1: "Very Bad",
            2: "Not Good",
            3: "Okay",
            4: "Good",
            5: "Great"
        }
    },

    // ===== Profile =====
    profile: {
        pageTitle: "Profile | Detective Study Helper",
        memberSince: "Member since",
        totalDiaries: "Total Diaries",
        streakDays: "Day Streak",
        todayDiary: "Today's Check-in",
        quickAccess: "Quick Access",
        writeDiary: "Write Diary",
        writeDiaryDesc: "Record today's mood and story",
        diaryHistory: "Diary History",
        diaryHistoryDesc: "View all diary entries",
        qaApp: "Smart Q&A",
        qaAppDesc: "AI helps solve your study problems",
        recentDiaries: "Recent Diaries",
        viewAll: "View All",
        noDiaries: "No diary yet. Start recording!",
        startWriting: "Write First"
    }
};

// Export for other modules
if (typeof window !== 'undefined') {
    window.translations_en = translations_en;
}
