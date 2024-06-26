from cogs.utils import create_subcommand_response

import os
import openai
from discord.ext import commands

MODEL = "gpt-3.5-turbo"
GPT_TOKEN = os.getenv("GPT_TOKEN")
openai.api_key = GPT_TOKEN


class GPTCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channels = {}

    @commands.group(name="gpt", invoke_without_command=True)
    async def gpt(self, ctx: commands.Context):
        """ Chat with chatGPT """
        if ctx.channel.id not in self.channels:
            self.channels[ctx.channel.id] = GptMessages()
        message = ctx.message.content[5:]
        if len(message) > 0:
            gpt: GptMessages = self.channels[ctx.channel.id]
            reply = gpt.chat(message=message)
            await ctx.send(reply)
        else:
            subcommands = self.gpt.commands
            response = create_subcommand_response(subcommands)
            await ctx.send(response)

    @gpt.command(
        name="setrole",
        description="Set new role for GPT")
    async def set_role(self, ctx: commands.Context):
        """ Set role for chatGPT """
        if ctx.channel.id not in self.channels:
            self.channels[ctx.channel.id] = GptMessages()
        self.channels[ctx.channel.id].role = ctx.message.content[12:]
        await ctx.send(f'Role set')

    @gpt.command(
        name="role",
        description="Show current role")
    async def role(self, ctx: commands.Context):
        """ Get role for chatGPT """
        channel_id = ctx.channel.id
        if channel_id in self.channels:
            role = self.channels[channel_id].role
            await ctx.send(f"Role: {role}")
        else:
            await ctx.send("No role set for this channel.")


class GptMessages:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.__role = {"role": "system",
                       "content": "You are a helpful assistant"}
        self.messages = []
        self.model = MODEL

    def chat(self, message: str) -> str:
        self.add_message({"role": "user", "content": message})
        messages_with_role = [self.__role.copy()]
        messages_with_role.extend(self.messages)
        chat = openai.chat.completions.create(
            model=self.model,
            messages=messages_with_role,
        )
        reply = chat.choices[0].message.content
        self.add_message({"role": "assistant", "content": reply})
        return reply

    def add_message(self, message: dict):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[1:]

    @property
    def role(self):
        return self.__role["content"]

    @role.setter
    def role(self, role: str):
        self.__role["content"] = role
