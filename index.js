#!/usr/bin/env node

// Import required dependencies
require('dotenv').config();
const { program } = require('commander');
const inquirer = require('inquirer');
const chalk = require('chalk');
const Anthropic = require('@anthropic-ai/sdk');

// Check if API key is available
if (!process.env.ANTHROPIC_API_KEY) {
  console.error(chalk.red('Error: ANTHROPIC_API_KEY not found in environment variables.'));
  console.log(chalk.yellow('Please add your API key to the .env file:'));
  console.log(chalk.yellow('ANTHROPIC_API_KEY=your_api_key_here'));
  process.exit(1);
}

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Define CLI version and commands
program
  .version('1.0.0')
  .description('Claude CLI - Chat with Claude AI in your terminal');

program
  .command('chat')
  .description('Start an interactive chat session with Claude')
  .option('-m, --model <model>', 'Claude model to use', 'claude-3-5-sonnet-20240620')
  .action(async (options) => {
    console.log(chalk.cyan('Starting chat with Claude...'));
    console.log(chalk.yellow('Type "exit", "quit", or press Ctrl+C to end the session.\n'));
    
    // Initialize conversation history
    const messages = [];
    
    try {
      while (true) {
        // Prompt user for input
        const { userInput } = await inquirer.prompt([{
          type: 'input',
          name: 'userInput',
          message: chalk.green('You:'),
        }]);
        
        // Check for exit commands
        if (['exit', 'quit'].includes(userInput.toLowerCase())) {
          console.log(chalk.cyan('Ending chat session. Goodbye!'));
          break;
        }
        
        // Add user message to history
        messages.push({ role: 'user', content: userInput });
        
        try {
          console.log(chalk.yellow('Claude is thinking...'));
          
          // Call Anthropic API
          const response = await anthropic.messages.create({
            model: options.model,
            max_tokens: 4096,
            messages: messages,
          });
          
          // Extract and display Claude's response
          const assistantMessage = response.content[0].text;
          console.log(chalk.blue('Claude:'), assistantMessage);
          
          // Add assistant response to history
          messages.push({ role: 'assistant', content: assistantMessage });
        } catch (error) {
          console.error(chalk.red('Error communicating with Claude:'), error.message);
        }
      }
    } catch (error) {
      console.error(chalk.red('An unexpected error occurred:'), error.message);
    }
  });

program
  .command('ask <question>')
  .description('Ask Claude a single question')
  .option('-m, --model <model>', 'Claude model to use', 'claude-3-5-sonnet-20240620')
  .action(async (question, options) => {
    try {
      console.log(chalk.yellow('Asking Claude...'));
      
      // Call Anthropic API
      const response = await anthropic.messages.create({
        model: options.model,
        max_tokens: 4096,
        messages: [
          { role: 'user', content: question }
        ],
      });
      
      // Extract and display Claude's response
      const assistantMessage = response.content[0].text;
      console.log(chalk.blue('Claude:'), assistantMessage);
    } catch (error) {
      console.error(chalk.red('Error communicating with Claude:'), error.message);
    }
  });

// Parse command line arguments
program.parse(process.argv);

// Show help if no command is provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
} 