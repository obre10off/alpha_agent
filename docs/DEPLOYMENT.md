# Deployment Guide

This guide covers deploying the AI Alpha Agent using Docker.

## Docker Deployment

### Quick Deployment

The fastest way to get started is using our pre-built Docker image:

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

### Local Development Deployment

If you want to modify the code or contribute:

1. Clone the repository
2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
3. Build and run:
   ```bash
   docker-compose up --build
   ```

## Environment Variables

Required variables:
```
OPENAI_API_KEY=your_openai_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=your_user_agent
COMPOSIO_API_KEY=your_composio_key
EMAIL_RECIPIENT=your_email@example.com
```

## Health Monitoring

The container exposes a basic health check endpoint:
- `/health`: Basic health check

Monitor the container using standard Docker commands:
```bash
# View logs
docker logs ai-alpha-agent

# Check container status
docker ps

# View container stats
docker stats ai-alpha-agent
```

## Troubleshooting

Common issues and solutions:

1. Container fails to start:
   - Check logs: `docker logs ai-alpha-agent`
   - Verify environment variables
   - Ensure API keys are valid

2. Email delivery issues:
   - Check Gmail API permissions
   - Verify email configuration
   - Check spam folder

3. Resource constraints:
   - Monitor container resources with `docker stats`
   - Adjust container resources if needed

## Updating

To update to the latest version:

```bash
# Using pre-built image
docker pull ghcr.io/yourusername/ai-alpha-agent:latest
docker stop ai-alpha-agent
docker rm ai-alpha-agent
# Run the docker run command again with your environment variables

# For local development
git pull origin main
docker-compose down
docker-compose up --build -d
``` 