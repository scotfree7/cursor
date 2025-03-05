# Claude CLI

A simple command-line interface for chatting with Claude AI using the Anthropic API.

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```
   npm install
   ```
4. Add your Anthropic API key to the `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
5. Make the CLI executable:
   ```
   chmod +x index.js
   ```
6. Create a global symlink (optional):
   ```
   npm link
   ```

## Usage

### Start an interactive chat session:

```
node index.js chat
```

Or if you used `npm link`:

```
claude-cli chat
```

### Ask a single question:

```
node index.js ask "What is the capital of France?"
```

Or if you used `npm link`:

```
claude-cli ask "What is the capital of France?"
```

### Change the Claude model:

You can specify which Claude model to use with the `-m` or `--model` option:

```
node index.js chat -m claude-3-opus-20240229
```

Available models include:
- claude-3-5-sonnet-20240620 (default)
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307

## Commands

- `chat`: Start an interactive chat session with Claude
- `ask <question>`: Ask Claude a single question
- `--help`: Display help information
- `--version`: Display version number

## Exit the Chat

In chat mode, type 'exit' or 'quit' to end the session, or press Ctrl+C. 