# 🚀 Starship Commander (星际指挥官)

一个基于Pygame的太空射击游戏，灵感来源于经典游戏Galaga。

## 🌟 游戏特色

- 🎮 经典的竖版射击游戏玩法
- 👾 多种敌人类型和强大的Boss战
- 💎 道具系统（生命、护盾、散弹）
- 🎯 多种难度模式（简单、普通、困难）
- 🏆 高分榜系统
- 🖥️ 支持全屏和窗口模式切换
- 📺 支持多种分辨率（720p, 1080p, 2K, 4K）
- 🎵 优美的背景音乐和音效

## 📦 安装要求

- 🐍 Python 3.7 或更高版本
- 🎮 Pygame 2.0 或更高版本

安装Pygame:
```bash
pip install pygame
```

## ▶️ 运行游戏

通过run.py运行（支持异步模式）:
```bash
python run.py
```

## 🌐 Web模式运行

游戏支持在浏览器中运行，通过Pyodide实现。要部署到Web上，需要以下步骤：

### 方法一：使用Pyodide（推荐）

1. 创建一个HTML文件，包含Pyodide运行时：
```html
<!DOCTYPE html>
<html>
<head>
    <title>Starship Commander</title>
</head>
<body>
    <script type="text/javascript">
        async function main(){
            let pyodide = await loadPyodide();
            await pyodide.loadPackage("micropip");
            const micropip = pyodide.pyimport("micropip");
            await micropip.install("pygame");
            
            // 加载游戏代码
            pyodide.runPython(`
                # 你的游戏代码
            `);
        }
        main();
    </script>
</body>
</html>
```

2. 由于Pygame在Pyodide中有一些限制，需要使用特定的Pygame Web分发版本。

### 方法二：使用Emscripten编译

1. 安装Emscripten SDK
2. 使用Emscripten编译Python代码为WebAssembly
3. 部署生成的文件到Web服务器

### 方法三：使用专门的Pygame-to-Web工具

目前有一些实验性工具可以将Pygame游戏转换为Web版本：
- pygbag: 专门为将Pygame游戏转换为Web应用而设计
- pygame-web: 为Web优化的Pygame版本

使用pygbag的示例：
```bash
pip install pygbag
python -m pygbag --ume_block=0 your_main_file.py
```

## 🎮 游戏操作

### 基本操作
- ⬆️⬇️⬅️➡️ **方向键**: 移动飞船
- 🔫 **空格键**: 射击
- ⏸️ **ESC键**: 暂停游戏
- 🖥️ **F11键**: 切换全屏/窗口模式

### 道具使用
- 🔢 **数字键1**: 激活护盾道具
- 🔢 **数字键2**: 激活散弹道具

### 鼠标操作
- 🖱️ 在菜单界面可以使用鼠标点击按钮
- 🖱️ 在游戏中点击鼠标左键可以射击

## 🎯 游戏机制

### 难度系统
- 🟢 **简单模式**: 敌人较弱，移动速度较慢
- 🟡 **普通模式**: 标准难度
- 🔴 **困难模式**: 敌人更强，移动速度更快

### 道具系统
- 🟢 **生命道具** (绿色): 增加一条生命
- 🔵 **护盾道具** (蓝色): 获得一个临时护盾
- 🔴 **散弹道具** (红色): 一段时间内发射散弹

### 得分系统
- 👾 消灭普通敌人: 50分
- 💀 消灭Boss敌人: 500分
- ✨ 完成关卡: 额外奖励分

## ⚙️ 技术特点

### 多平台支持
游戏副本支持两种运行模式：
- 🔄 **同步模式**: 传统的Pygame事件循环
- ⚡ **异步模式**: 基于asyncio的事件循环，支持Web平台运行

### 自适应分辨率
- 📐 支持多种分辨率（720p, 1080p, 2K, 4K）
- 📏 自动适应屏幕比例，保持16:9宽高比
- 🖼️ 支持全屏和窗口模式切换

### 配置系统
游戏副本会保存以下配置：
- ⚙️ 移动速度设置
- ⚙️ 射击速度设置
- ⚙️ 子弹速度设置
- 🔊 音乐开关状态
- 🏆 高分榜记录

## 📁 项目结构

```
Galaga/
├── assets/           # 游戏资源文件夹
│   ├── images/       # 图像资源
│   ├── sounds/       # 音效资源
│   └── fonts/        # 字体资源
├── src/              # 源代码文件夹
│   ├── main.py       # 异步版本主程序
│   ├── sprites.py    # 游戏精灵类
│   ├── level.py      # 关卡系统
│   ├── score.py      # 得分系统
│   ├── ui.py         # 用户界面组件
│   ├── config.py     # 配置管理
│   └── constants.py  # 常量定义
├── run.py            # 运行入口
└── README.md         # 说明文档
```

## 🛠️ 开发说明


### 性能优化

- ⚡ 图像资源预加载
- ⚡ 精灵组管理优化
- ⚡ 内存使用优化

## 📄 许可证

本项目仅供学习和娱乐使用。

## 📝 更新日志

### 最近更新
- ✨ 添加了异步模式支持
- ⚡ 优化了着陆页面性能
- 📐 改进了分辨率自适应功能
- 🐛 修复了FPS显示问题
- ⚡ 优化了资源加载机制