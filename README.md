# Blueee

blue 的 opencode skill 合集。

## 目录结构

```
skills/
├─ jev/                      # Jev (TypeSafe System One) 判断模型调用
│  ├─ SKILL.md
│  └─ jev.py
└─ ex-girlfriend-simulator/  # 前女友角色扮演
   └─ SKILL.md
```

## 什么是 skill

opencode 的 skill 是按需加载的指令文件（`SKILL.md`）。把某个 skill 目录放到
`.opencode/skills/<名字>/`，重启 opencode 后即可在匹配场景自动触发。

## 安装某个 skill

把对应目录整个复制到你的 `.opencode/skills/` 下即可，例如：

```powershell
Copy-Item -Recurse .\skills\jev "你的项目\.opencode\skills\jev"
```
