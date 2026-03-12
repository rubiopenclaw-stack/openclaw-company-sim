# 🦞 OpenClaw Pixel Company Simulator

A pixel-style company management game that links with your real OpenClaw agents and skills!

## 🎮 Features

- **Pixel Character Creation** - Choose from 8 pixel avatars
- **Real Agent Integration** - Links to your actual OpenClaw agents
- **Skills Display** - View skills for each agent
- **Cron Jobs Monitor** - See scheduled tasks
- **Dashboard** - Token usage, skills count, cron jobs

## 🚀 Quick Start

```bash
# Clone the project
git clone https://github.com/rubiopenclaw-stack/openclaw-company-sim.git
cd openclaw-company-sim

# Run with HTTP server
npx -y http-server -p 8080
```

Then open: **http://localhost:8080**

## 📊 Data Sources

This simulator reads real data from your OpenClaw installation:

- `~/.openclaw/agents/` - Agent list
- `~/.openclaw/skills/` - Skills directory
- `~/.openclaw/openclaw.json` - Configuration

## 🎯 How to Play

1. **Create Your Character** - Choose a pixel avatar
2. **View Your Team** - See your OpenClaw agents
3. **Explore Skills** - Click on agents to see their skills
4. **Monitor Tasks** - Check scheduled cron jobs
5. **Track Resources** - View token usage and statistics

## 🛠️ Tech Stack

- HTML/CSS/JavaScript (Vanilla)
- OpenClaw Data Integration

## 📝 License

MIT

---

Built with ❤️ using OpenClaw
