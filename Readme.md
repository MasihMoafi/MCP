# Advanced MCP Integration Guide

This guide covers creating, implementing, and integrating advanced Model Context Protocol (MCP) servers for specialized integrations with various services including GitHub, Kaggle, HuggingFace, and browser automation tools like Puppeteer and Playwright.

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI tools like Windsurf to interact with external services through well-defined API interfaces. MCPs serve as bridges between AI tools and the services they need to access, providing a consistent interface for complex operations.

## MCP Architecture

A typical MCP includes:

1. **Schema Definition**: JSON Schema that defines available tools and parameters
2. **Server Implementation**: Node.js (or other language) program that handles requests and executes operations
3. **I/O Protocol**: Standard JSON-based communication protocol between client and server
4. **Authentication**: Methods for securely authenticating with external services

## Included MCPs

This repository includes several advanced MCP implementations:

- **Kaggle MCP**: Access Kaggle datasets, competitions, and notebooks
- **HuggingFace MCP**: Interact with HuggingFace models, datasets, and inference APIs
- **GitHub MCP**: Create repositories, manage issues, and more
- **Safe Terminal MCP**: Execute terminal commands with confirmation

## Setting Up MCPs in Windsurf

To configure these MCPs in your Windsurf installation:

1. Make the MCP files executable: `chmod +x /path/to/mcp-file.js`
2. Edit your MCP configuration at `~/.codeium/windsurf/mcp_config.json`
3. Add entries for each MCP you want to enable

Example configuration:

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "/path/to/kaggle-mcp/kaggle-mcp.js",
      "env": {
        "KAGGLE_USERNAME": "your-username",
        "KAGGLE_KEY": "your-api-key"
      }
    },
    "huggingface": {
      "command": "/path/to/huggingface-mcp/huggingface-mcp.js",
      "env": {
        "HUGGINGFACE_TOKEN": "your-hf-token"
      }
    }
  }
}
```

## Creating Your Own MCP

### Step 1: Plan Your MCP

Define the functionality you want to expose:

1. What service are you integrating with?
2. What operations should be available?
3. What parameters are needed for each operation?
4. What authentication is required?

### Step 2: Create the Schema

Define your tools and their parameters using JSON Schema:

```javascript
const tools = [
  {
    name: 'operation_name',
    description: 'Description of what this operation does',
    parameters: {
      type: 'object',
      properties: {
        param1: {
          type: 'string',
          description: 'Description of parameter 1'
        },
        param2: {
          type: 'integer',
          description: 'Description of parameter 2'
        }
      },
      required: ['param1']
    }
  }
];
```

### Step 3: Implement the Server

Create a Node.js script that handles the MCP protocol:

```javascript
#!/usr/bin/env node

const readline = require('readline');

// Initialize your service client here

// Define MCP tools (as shown above)

// Handle tool execution
async function executeFunction(name, args) {
  try {
    switch (name) {
      case 'operation_name':
        // Implement the operation
        const result = await yourServiceClient.doSomething(args.param1, args.param2);
        return { success: true, data: result };
      
      default:
        throw new Error(`Unknown function: ${name}`);
    }
  } catch (error) {
    return { error: error.message };
  }
}

// Initialize readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Send MCP server info
console.log(JSON.stringify({
  schema_version: "v1",
  name: "your-mcp-name",
  description: "Description of your MCP",
  tools: tools
}));

// Handle input requests
rl.on('line', async (line) => {
  try {
    const request = JSON.parse(line);
    if (request.type === 'function') {
      const result = await executeFunction(request.name, request.arguments);
      console.log(JSON.stringify({
        id: request.id,
        result: result
      }));
    }
  } catch (error) {
    console.error('Error processing request:', error);
  }
});
```

### Step 4: Test Your MCP

Test your MCP implementation directly:

1. Make it executable: `chmod +x your-mcp.js`
2. Run it: `./your-mcp.js`
3. Send test input in the expected format

### Step 5: Configure in Windsurf

Add your MCP to the Windsurf configuration as shown above.

## Advanced MCP Techniques

### User Confirmation

For sensitive operations, implement a confirmation mechanism:

```javascript
// In executeFunction
if (name === 'sensitive_operation') {
  return {
    requires_confirmation: true,
    message: "This operation will delete data. Are you sure?",
    operation: { name, args },
    requestId: requestId
  };
}
```

### Streaming Responses

For long-running operations, implement streaming:

```javascript
// Send multiple responses for a single request
function streamProgress(requestId, progress) {
  console.log(JSON.stringify({
    id: requestId,
    partial: true,
    result: { progress }
  }));
}

// Final response
console.log(JSON.stringify({
  id: requestId,
  result: finalResult
}));
```

### Persistent Configuration

Implement secure configuration storage:

```javascript
const CONFIG_DIR = path.join(process.env.HOME, '.config', 'your-mcp');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

// Load config
let config = {};
if (fs.existsSync(CONFIG_FILE)) {
  config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
}

// Save config
function saveConfig() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}
```

## Security Best Practices

1. **Never hardcode credentials** in your MCP
2. **Use environment variables** for sensitive information
3. **Implement password protection** for destructive operations
4. **Store tokens securely** in the user's config directory
5. **Validate all inputs** before passing to external services
6. **Implement user confirmation** for sensitive operations

## Troubleshooting

Common issues:

1. **Communication errors**: Check that your MCP correctly reads from stdin and writes to stdout
2. **Authentication errors**: Verify that your tokens/credentials are correctly set
3. **Permissions errors**: Ensure your MCP files are executable
4. **Configuration errors**: Validate your `mcp_config.json` format

## Resources

- [Official MCP Documentation](https://docs.codeium.com/mcp)
- [JSON Schema Documentation](https://json-schema.org/)
- [Node.js Documentation](https://nodejs.org/en/docs/)
