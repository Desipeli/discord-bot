from discord.ext.commands import Command


def create_subcommand_response(subcommands: list[Command]):
    response = "```bash\n"  # bash for text color
    for subcommand in subcommands:
        response += subcommand.name + "\n"
        response += "# " + subcommand.description + "\n"
        response += "\n"

    response += "```"
    return response
