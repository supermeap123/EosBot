# cogs/eos_cog.py
import discord
from discord.ext import commands, tasks
import threading
import time
import shutil
import os
import json
import random
import asyncio
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import logger
from helpers import (
    contains_trigger_word,
    is_bot_mentioned,
    random_chance,
)
from openrouter_api import get_openrouter_response
from openpipe_api import get_openpipe_response
from database import (
    load_probabilities,
    save_probabilities,
)
from agents import AgentManager

class EosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.analyzer = SentimentIntensityAnalyzer()
        self.agent_manager = AgentManager()
        self.jsonl_lock = threading.Lock()
        self.cleanup_conversation_histories.start()
        self.update_presence.start()

    @tasks.loop(hours=1)
    async def cleanup_conversation_histories(self):
        # Implement cleanup logic if needed
        pass

    @tasks.loop(minutes=30)
    async def update_presence(self):
        # Implement presence update logic if needed
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Process commands
        await self.bot.process_commands(message)

        # Determine if the message is a DM
        is_dm = isinstance(message.channel, discord.DMChannel)

        # Get guild_id and channel_id
        guild_id = message.guild.id if message.guild else 'DM'
        channel_id = message.channel.id

        content = message.content

        # Check if the message starts with an agent name
        agent_name = self.extract_agent_name(content)
        agent = self.agent_manager.get_agent(agent_name)

        if agent:
            # Remove agent name from content
            content = content[len(agent_name):].strip()

            # Handle the message with the agent
            await self.handle_agent_response(agent, message, content)

    def extract_agent_name(self, content):
        # Extract agent name from the start of the message
        words = content.strip().split()
        if words:
            potential_name = words[0]
            if self.agent_manager.get_agent(potential_name):
                return potential_name
        return None

    async def handle_agent_response(self, agent, message, content):
        async with message.channel.typing():
            # Build the conversation history
            messages = []
            # Add system prompt
            system_prompt = f"You are {agent.name}."
            messages.append({"role": "system", "content": system_prompt})

            # Get conversation history
            history = agent.conversation_histories.get(message.channel.id, [])
            messages.extend(history)

            # Add the user's message
            user_message = {
                "role": "user",
                "content": content
            }
            messages.append(user_message)

            # Get response based on backend
            if agent.backend.lower() == 'openpipe':
                response = await get_openpipe_response(
                    messages, agent.model_string, agent.temperature
                )
            else:
                response = await get_openrouter_response(
                    messages, agent.model_string, agent.temperature
                )

            if response:
                # Change bot nickname to agent's name if in a guild
                if message.guild:
                    try:
                        await message.guild.me.edit(nick=agent.name)
                    except discord.Forbidden:
                        logger.warning("Missing permissions to change nickname.")

                # Send the response
                await message.reply(response, mention_author=False)

                # Update conversation history
                history.append(user_message)
                history.append({"role": "assistant", "content": response})
                agent.conversation_histories[message.channel.id] = history[-50:]  # Keep last 50 messages

                # Save conversation
                guild_id = message.guild.id if message.guild else 'DM'
                channel_id = message.channel.id
                self.save_conversation_to_jsonl(agent, system_prompt, history, guild_id, channel_id)
            else:
                logger.error("Failed to get response from API.")

    def save_conversation_to_jsonl(self, agent, system_prompt, history, guild_id, channel_id):
        with self.jsonl_lock:
            if not os.path.exists('conversations'):
                os.makedirs('conversations')
            agent_folder = os.path.join('conversations', agent.name)
            if not os.path.exists(agent_folder):
                os.makedirs(agent_folder)
            if guild_id == 'DM':
                file_path = os.path.join(agent_folder, f'DM_{channel_id}.jsonl')
            else:
                file_path = os.path.join(agent_folder, f'{guild_id}_{channel_id}.jsonl')

            file_exists = os.path.exists(file_path)
            with open(file_path, 'a', encoding='utf-8') as f:
                if not file_exists:
                    # Save the system prompt as the first message
                    system_message = {"role": "system", "content": system_prompt}
                    f.write(f"{json.dumps(system_message)}\n")

                # Save the conversation history
                for msg in history:
                    f.write(f"{json.dumps(msg)}\n")

    # Commands for managing agents
    @commands.command(name='init')
    async def init_agent(self, ctx, agent_name: str, *, model_string: str):
        """Initialize a new agent."""
        backend = 'openpipe' if model_string.startswith('openpipe:') else 'openrouter'
        if backend == 'openpipe':
            model_string = model_string.replace('openpipe:', '', 1)

        success = self.agent_manager.add_agent(agent_name, model_string, backend)
        if success:
            await ctx.send(f"Agent '{agent_name}' initialized with model '{model_string}' using backend '{backend}'.")
        else:
            await ctx.send(f"Agent '{agent_name}' already exists.")

    @commands.command(name='backend')
    async def set_agent_backend(self, ctx, agent_name: str, backend: str):
        """Set the backend for an agent."""
        if backend.lower() not in ['openrouter', 'openpipe']:
            await ctx.send("Invalid backend. Please choose 'openrouter' or 'openpipe'.")
            return

        success = self.agent_manager.set_backend(agent_name, backend.lower())
        if success:
            await ctx.send(f"Agent '{agent_name}' backend set to '{backend}'.")
        else:
            await ctx.send(f"Agent '{agent_name}' does not exist.")

    @commands.command(name='temp')
    async def set_agent_temperature(self, ctx, agent_name: str, temperature: float):
        """Set the temperature for an agent."""
        if not 0 <= temperature <= 1:
            await ctx.send("Temperature must be between 0 and 1.")
            return

        success = self.agent_manager.set_temperature(agent_name, temperature)
        if success:
            await ctx.send(f"Agent '{agent_name}' temperature set to '{temperature}'.")
        else:
            await ctx.send(f"Agent '{agent_name}' does not exist.")

    @commands.command(name='model')
    async def set_agent_model(self, ctx, agent_name: str, *, model_string: str):
        """Set the model string for an agent."""
        success = self.agent_manager.set_model_string(agent_name, model_string)
        if success:
            await ctx.send(f"Agent '{agent_name}' model set to '{model_string}'.")
        else:
            await ctx.send(f"Agent '{agent_name}' does not exist.")

    @commands.command(name='list_agents')
    async def list_agents(self, ctx):
        """List all initialized agents."""
        agents = self.agent_manager.agents.keys()
        if agents:
            agent_list = ', '.join(agents)
            await ctx.send(f"Initialized agents: {agent_list}")
        else:
            await ctx.send("No agents have been initialized.")

    @commands.command(name='remove_agent')
    async def remove_agent(self, ctx, agent_name: str):
        """Remove an agent."""
        success = self.agent_manager.remove_agent(agent_name)
        if success:
            await ctx.send(f"Agent '{agent_name}' has been removed.")
        else:
            await ctx.send(f"Agent '{agent_name}' does not exist.")

def setup(bot):
    bot.add_cog(EosCog(bot))
