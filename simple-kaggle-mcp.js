#!/usr/bin/env node

/**
 * Simple Kaggle MCP
 * A minimal MCP for interacting with the Kaggle API
 */

const axios = require('axios');
const readline = require('readline');

// Define Kaggle MCP tools
const tools = [
  {
    name: 'search_datasets',
    description: 'Search Kaggle datasets',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        page: {
          type: 'integer',
          description: 'Page number (default: 1)'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'search_competitions',
    description: 'Search Kaggle competitions',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        page: {
          type: 'integer',
          description: 'Page number (default: 1)'
        }
      },
      required: ['query']
    }
  }
];

// Simple Kaggle client
class KaggleClient {
  constructor(username, key) {
    this.baseUrl = 'https://www.kaggle.com/api/v1';
    this.username = username;
    this.key = key;
  }

  getAxiosClient() {
    return axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Authorization': `Basic ${Buffer.from(`${this.username}:${this.key}`).toString('base64')}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async searchDatasets(query, page = 1) {
    const client = this.getAxiosClient();
    const response = await client.get('/datasets/list', { 
      params: { search: query, page, pageSize: 10 } 
    });
    return response.data;
  }

  async searchCompetitions(query, page = 1) {
    const client = this.getAxiosClient();
    const response = await client.get('/competitions/list', { 
      params: { search: query, page, pageSize: 10 } 
    });
    return response.data;
  }
}

// Handle tool execution
async function executeFunction(name, args) {
  try {
    // Get credentials from environment variables
    const username = process.env.KAGGLE_USERNAME;
    const key = process.env.KAGGLE_KEY;
    
    if (!username || !key) {
      return { error: 'Kaggle credentials not set. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables.' };
    }
    
    const client = new KaggleClient(username, key);
    
    switch (name) {
      case 'search_datasets':
        const datasets = await client.searchDatasets(args.query, args.page || 1);
        return { 
          datasets: datasets.map(d => ({
            ref: `${d.ownerName}/${d.datasetSlug}`,
            title: d.title,
            size: d.size
          }))
        };
      
      case 'search_competitions':
        const competitions = await client.searchCompetitions(args.query, args.page || 1);
        return { 
          competitions: competitions.map(c => ({
            ref: c.ref,
            title: c.title,
            deadline: c.deadline
          }))
        };
      
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
  name: "simple-kaggle-mcp",
  description: "Simple Kaggle API integration",
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