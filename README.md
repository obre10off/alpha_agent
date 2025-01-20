# AI Alpha Agent

An autonomous system that monitors Reddit and HackerNews for innovative AI agent ideas, generating detailed PRDs and delivering insights via email.

## 🌟 Features

- 🤖 Autonomous monitoring of Reddit and HackerNews
- 🔍 Smart filtering and analysis of AI agent opportunities
- 📄 Automatic PRD generation for promising concepts
- 📧 Email delivery of insights
- 🐳 Easy deployment via Docker

## 🚀 Quick Start

### Prerequisites

- Docker installed on your system
- Gmail account for email delivery
- API keys for:
  - OpenAI
  - Reddit
  - HackerNews
  - Gmail (via Composio)

### Deployment

1. Pull and run with Docker:
```bash
docker pull ghcr.io/yourusername/ai-alpha-agent:latest
docker run -d \
  --name ai-alpha-agent \
  -e OPENAI_API_KEY=your_key \
  -e REDDIT_CLIENT_ID=your_id \
  -e REDDIT_CLIENT_SECRET=your_secret \
  -e REDDIT_USER_AGENT=your_agent \
  -e COMPOSIO_API_KEY=your_key \
  -e EMAIL_RECIPIENT=your_email@example.com \
  ghcr.io/yourusername/ai-alpha-agent:latest
```

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-alpha-agent.git
cd ai-alpha-agent
```

2. Create and configure your `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

## 📝 Configuration

Configure the agent by editing the following files:
- `config/sources.yaml`: Configure monitoring sources and intervals
- `config/templates.yaml`: Customize PRD and email templates
- `.env`: Set up your environment variables and API keys

## 🛠️ Development

1. Set up local development environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

## 📊 Monitoring

- Access logs via `docker logs ai-alpha-agent`
- Monitor container health via Docker health checks
- View email delivery status in the application logs

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](./docs/)
- [Issue Tracker](https://github.com/yourusername/ai-alpha-agent/issues)
- [Project Requirements](./documentation/instructions.md) 