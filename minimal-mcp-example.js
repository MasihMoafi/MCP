#!/usr/bin/env node

/**
 * Minimal MCP Example
 * This demonstrates the core components of an MCP with minimal code
 */

const readline = require('readline');

// Define just two simple tools
const tools = [
  {
    name: 'greet',
    description: 'Say hello to someone',
    parameters: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Name to greet'
        }
      },
      required: ['name']
    }
  },
  {
    name: 'calculate',
    description: 'Perform a simple calculation',
    parameters: {
      type: 'object',
      properties: {
        a: { type: 'number', description: 'First number' },
        b: { type: 'number', description: 'Second number' },
        operation: { 
          type: 'string', 
          description: 'Operation to perform',
          enum: ['add', 'subtract', 'multiply', 'divide'] 
        }
      },
      required: ['a', 'b', 'operation']
    }
  }
];

// Handle tool execution
async function executeFunction(name, args) {
  switch (name) {
    case 'greet':
      return { message: `Hello, ${args.name}!` };
    
    case 'calculate':
      let result;
      switch(args.operation) {
        case 'add': result = args.a + args.b; break;
        case 'subtract': result = args.a - args.b; break;
        case 'multiply': result = args.a * args.b; break;
        case 'divide': 
          if (args.b === 0) throw new Error('Cannot divide by zero');
          result = args.a / args.b; 
          break;
        default:
          throw new Error(`Unknown operation: ${args.operation}`);
      }
      return { result };
    
    default:
      throw new Error(`Unknown function: ${name}`);
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
  name: "minimal-mcp",
  description: "A minimal MCP example with basic functions",
  tools: tools
}));

// Handle input requests
rl.on('line', async (line) => {
  try {
    const request = JSON.parse(line);
    if (request.type === 'function') {
      try {
        const result = await executeFunction(request.name, request.arguments);
        console.log(JSON.stringify({ id: request.id, result }));
      } catch (error) {
        console.log(JSON.stringify({ 
          id: request.id, 
          error: error.message 
        }));
      }
    }
  } catch (error) {
    console.error('Error parsing request:', error.message);
  }
});