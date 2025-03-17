#!/usr/bin/env node

/**
 * Simple HuggingFace MCP
 * A minimal MCP for interacting with the HuggingFace API
 */

const axios = require('axios');
const readline = require('readline');

// Define HuggingFace MCP tools
const tools = [
  {
    name: 'search_models',
    description: 'Search HuggingFace models',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        limit: {
          type: 'integer',
          description: 'Maximum number of results (default: 10)'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'generate_text',
    description: 'Generate text using a HuggingFace model',
    parameters: {
      type: 'object',
      properties: {
        model: {
          type: 'string',
          description: 'HuggingFace model ID'
        },
        prompt: {
          type: 'string',
          description: 'Input prompt for text generation'
        },
        max_length: {
          type: 'integer',
          description: 'Maximum length of generated text (default: 100)'
        }
      },
      required: ['model', 'prompt']
    }
  }
];

// Simple HuggingFace client
class HuggingFaceClient {
  constructor(token) {
    this.apiUrl = 'https://huggingface.co/api';
    this.inferenceUrl = 'https://api-inference.huggingface.co/models';
    this.token = token;
  }

  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async searchModels(query, limit = 10) {
    const response = await axios.get(`${this.apiUrl}/models`, {
      params: { search: query, limit },
      headers: this.getHeaders()
    });
    return response.data;
  }

  async generateText(model, prompt, max_length = 100) {
    const response = await axios.post(`${this.inferenceUrl}/${model}`, 
      { inputs: prompt, parameters: { max_length } },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

// Handle tool execution
async function executeFunction(name, args) {
  try {
    // Get token from environment variable
    const token = process.env.HUGGINGFACE_TOKEN;
    
    if (!token) {
      return { error: 'HuggingFace token not set. Set HUGGINGFACE_TOKEN environment variable.' };
    }
    
    const client = new HuggingFaceClient(token);
    
    switch (name) {
      case 'search_models':
        const models = await client.searchModels(args.query, args.limit || 10);
        return { 
          models: models.map(m => ({
            id: m.id,
            name: m.modelId,
            downloads: m.downloads,
            likes: m.likes
          }))
        };
      
      case 'generate_text':
        const result = await client.generateText(
          args.model, 
          args.prompt, 
          args.max_length || 100
        );
        return { generated_text: result[0].generated_text };
      
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
  name: "simple-huggingface-mcp",
  description: "Simple HuggingFace API integration",
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
    console.error('Error:', error);
  }
});