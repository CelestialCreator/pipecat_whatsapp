# WhatsApp WebRTC Bot

A real-time voice bot that integrates with WhatsApp Business API to handle voice calls using WebRTC technology. Users can call your WhatsApp Business number and have natural conversations with an AI-powered bot.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [MCP Integration](#mcp-integration)
- [Development](#development)
- [License](#license)

## Overview

This project enables real-time voice conversations with WhatsApp users through WebRTC technology. The bot handles incoming WhatsApp calls, processes user speech using STT, processes queries with an LLM, and responds using TTS. The system is built on the Pipecat framework for real-time voice and multimodal AI agents.

### Key Features

- Real-time voice conversations with WhatsApp users
- WebRTC technology for voice communication
- Integration with AI services for conversation handling
- Support for STT (Speech-to-Text), LLM (Large Language Model), and TTS (Text-to-Speech)
- MCP (Model Context Protocol) integration for extended tool access
- Automatic greeting and order-taking capabilities
- Stock checking and order placement functionality

## Architecture

The application follows a modular architecture:

- **Server Layer**: FastAPI application that handles WhatsApp webhook events and manages WebRTC connections
- **Transport Layer**: SmallWebRTCTransport handles WebRTC connection establishment and management
- **AI Layer**: Uses OpenAI-compatible LLM for conversation processing and MCP for tool integration
- **Audio Processing**: Uses Deepgram STT, Cartesia TTS, and Silero VAD for voice activity detection

### Components

- `server.py`: Handles WhatsApp webhook events and manages WebRTC connections
- `bot.py`: Implements the conversation pipeline using Pipecat
- `prompt.py`: Contains the system and session instructions for the AI agent
- `env.example`: Example environment variables file

## Prerequisites

### WhatsApp Business API Setup

1. **Facebook Account**: Create an account at [facebook.com](https://facebook.com)
2. **Facebook Developer Account**: Create an account at [developers.facebook.com](https://developers.facebook.com)
3. **WhatsApp Business App**: Create a new [WhatsApp Business API application](https://developers.facebook.com/apps)
4. **Phone Number**: Add and verify a WhatsApp Business phone number
5. **Business Verification**: Complete business verification process (required for production only)
6. **Webhook Configuration**: Set up webhook endpoint for your application

> **Important Note**: For production, make sure your WhatsApp Business account has access to this feature.

> Find more details here:
> - [Getting Started Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/)
> - [Voice Calling Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/calling/)
> - [Webhooks Setup](https://developers.facebook.com/docs/whatsapp/webhooks/)

### WhatsApp Business API Configuration

#### Enable Voice Calls
Your WhatsApp Business phone number must be configured to accept voice calls[[2]](https://developers.facebook.com/docs/whatsapp/cloud-api/calling/):

> For development, you'll be provided with a free test phone number valid for 90 days.

1. Go to your WhatsApp Business API dashboard in Meta Developer Console
2. Navigate to **Configuration** → **Phone Numbers** → **Manage phone numbers**
3. Select your phone number
4. In the **Calls** tab, enable "Allow voice calls" capability
5. Save the configuration

#### Configure Webhook
Set up your webhook endpoint in the Meta Developer Console[[3]](https://developers.facebook.com/docs/whatsapp/webhooks/):

1. Go to **WhatsApp** → **Configuration** → **Webhooks**
2. Set callback URL: `https://your-domain.com/`
3. Set verify token: `your_webhook_verification_token`
   - This token should match your `WHATSAPP_WEBHOOK_VERIFICATION_TOKEN` environment variable
4. Click "Verify and save"
5. In the webhook fields below, select: `calls` (required for voice call events)

#### Configure Access Token
1. Go to **WhatsApp** → **API Setup**
2. Click "Generate access token"
   - Use this token for your `WHATSAPP_TOKEN` environment variable
3. Note your Phone Number ID - you'll need this for `PHONE_NUMBER_ID` configuration

## Installation

### Requirements

- Python 3.10 or newer
- `uv` package manager (https://docs.astral.sh/uv/)

### Setup Commands

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd whatsapp
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

## Configuration

### Environment Variables

1. **Copy the example environment file**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file and add your API keys and configuration values**.

### Required API Keys

- **OpenRouter API Key**: Required for LLM service. Get it from [OpenRouter](https://openrouter.ai/).
  - Used as `OPENROUTER_API_KEY` in environment
  - Used with the google/gemini-2.0-flash-lite-001 model by default
- **Deepgram API Key**: Required for Speech-to-Text service. Get it from [Deepgram](https://deepgram.com/).
  - Used as `DEEPGRAM_API_KEY` in environment
- **Cartesia API Key**: Required for Text-to-Speech service. Get it from [Cartesia](https://cartesia.ai/).
  - Used as `CARTESIA_API_KEY` in environment
- **WhatsApp Business API Token**: Required for WhatsApp integration.
  - Used as `WHATSAPP_TOKEN` in environment
- **WhatsApp Webhook Verification Token**: Required for webhook verification.
  - Used as `WHATSAPP_WEBHOOK_VERIFICATION_TOKEN` in environment
- **WhatsApp Phone Number ID**: Your WhatsApp Business phone number ID.
  - Used as `WHATSAPP_PHONE_NUMBER_ID` in environment

### Optional: MCP (Model Context Protocol) Integration

To use MCP for extended tool access:

- **MCP HTTP URL**: Optional. Provide an HTTP URL for your MCP server. The `MCP_HTTP_URL` environment variable should be set to your MCP server URL.

## Running the Server

### Start the Server

```bash
python server.py
```

> The server will start and listen for incoming WhatsApp webhook events.

By default, the server will run on `localhost:7860`. You can specify a different host and port:

```bash
python server.py --host 0.0.0.0 --port 8080
```

Add `-v` flag for verbose logging:

```bash
python server.py -v
```

### Connect Using WhatsApp

1. Find your WhatsApp test number in the Meta Developer Console
2. Call the number from your WhatsApp app
3. The bot should answer and engage in conversation

## API Endpoints

### GET `/`

Handles WhatsApp webhook verification requests from Meta.

- **Description**: Used during webhook setup to verify the endpoint
- **Parameters**: Verification token and challenge as query parameters
- **Response**: Challenge string for verification

### POST `/`

Handles incoming WhatsApp webhook events.

- **Description**: Processes incoming WhatsApp messages and call events
- **Body**: WhatsApp webhook request payload
- **Response**: Success confirmation with processing status

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | API key for OpenRouter |
| `DEEPGRAM_API_KEY` | Yes | API key for Deepgram STT service |
| `CARTESIA_API_KEY` | Yes | API key for Cartesia TTS service |
| `WHATSAPP_TOKEN` | Yes | WhatsApp Business API access token |
| `WHATSAPP_WEBHOOK_VERIFICATION_TOKEN` | Yes | Token for webhook verification |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes | WhatsApp Business phone number ID |
| `MCP_HTTP_URL` | No | Optional HTTP URL for MCP server to add tools to the AI agent |

## Troubleshooting

### Common Issues

   - Verify the `WHATSAPP_WEBHOOK_VERIFICATION_TOKEN` matches the one in Meta Developer Console
   - Ensure your webhook URL is publicly accessible (consider using ngrok for local development)

2. **Bot Not Responding**
   - Check that all API keys are correctly configured in the `.env` file
   - Verify that voice calling is enabled for your WhatsApp Business number
   - Ensure your business account is verified for production use

3. **Dependency Installation Issues**
   - Ensure you have `uv` package manager installed
   - Run `uv sync` to install all dependencies
   - Activate the virtual environment with `source .venv/bin/activate`

4. **WebRTC Connection Issues**
   - Check that your server can handle WebSocket connections
   - Verify that your domain is accessible via HTTPS (required for WebRTC)

### Debugging

Add the `-v` flag when running the server for more detailed logs:

```bash
python server.py -v
```

This will enable TRACE-level logging which helps identify issues with the connection flow.

## MCP Integration

This bot supports MCP (Model Context Protocol) for extended tool access. If the `MCP_HTTP_URL` environment variable is set, the bot will use the MCP server to access custom tools.

MCP allows the bot to access custom tools and services that extend its capabilities. The current implementation includes:

- **doolally_knowledge_base**: For answering questions about menu items, timings, location, or FAQs
- **check_menu_stock**: For verifying if a specific item is in stock and confirming the latest price
- **place_order**: For recording a confirmed order in the Orders tab

## Development

### Project Structure

```
whatsapp/
├── bot.py              # Conversation pipeline implementation
├── server.py           # FastAPI server for handling webhooks
├── prompt.py           # System and session instructions for the AI agent
├── env.example         # Example environment variables
├── pyproject.toml      # Project dependencies and configuration
├── README.md           # This file
└── ...
```

### Making Changes

1. Make sure you're in the project directory
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Make your changes
4. Test the changes by running:
   ```bash
   python server.py
   ```

### Pipecat Framework

This project uses the Pipecat framework for building real-time voice agents. The pipeline includes:

- Input transport (WebRTC connection)
- STT (Speech-to-Text)
- LLM (Large Language Model)
- TTS (Text-to-Speech)
- Output transport (WebRTC connection)

## Documentation References

- [WhatsApp Cloud API Getting Started](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/)
- [Voice Calling API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/calling/)
- [Webhook Configuration Guide](https://developers.facebook.com/docs/whatsapp/webhooks/)
- [SDP Overview and Samples](https://developers.facebook.com/docs/whatsapp/cloud-api/calling/reference#sdp-overview-and-sample-sdp-structures)
- [Pipecat Framework Documentation](https://github.com/pipecat-ai/pipecat)

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.

## Notes

- Voice calling feature requires WhatsApp Business API access
- Test numbers are valid for 90 days in development mode
- Production deployment requires business verification
- The bot is configured as "Reva" for Doolally Taproom with specific conversation flows and prompts