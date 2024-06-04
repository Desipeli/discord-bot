from discord.ext import commands


class GreetingCog(commands.Cog):
    """ I will greet you """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="greetings")
    async def greetings(self, ctx: commands.Context):
        """ hello for you """
        await ctx.send(f"Hello {ctx.message.author}")
