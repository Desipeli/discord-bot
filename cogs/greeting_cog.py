from discord.ext import commands
from cogs.utils import create_subcommand_response


class GreetingCog(commands.Cog):
    """ I will greet you """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="greetings", invoke_without_command=True)
    async def greetings(self, ctx: commands.Context):
        """ hello for you """
        subcommands = self.greetings.commands
        response = create_subcommand_response(subcommands)
        await ctx.send(response)

    @greetings.command(name="Hello", description="This prints Hello there")
    async def greetings_hello(self, ctx):
        await ctx.send("Hello there")

    @greetings.command(name="Moikka", description="Morottaja")
    async def greetings_hello(self, ctx):
        await ctx.send("Moro moro")
