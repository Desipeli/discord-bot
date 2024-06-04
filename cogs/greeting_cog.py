from discord.ext import commands
import logging

class GreetingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def greetings(self, ctx):
        await ctx.send('This is the greetings group. Use `!greetings hello`.')

    @greetings.command(name="hello")
    async def greetings_hello(self, ctx):
        logging.info("HELLO command triggered")
        await ctx.send(f'Hello from GreetingCog, {ctx.author.mention}!')
