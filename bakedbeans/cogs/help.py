import discord
from discord.ext import commands


class EmbedHelpCommand(commands.HelpCommand):
    """The implementation of the default help command.
    This inherits from :class:`HelpCommand`.
    It extends it with the following attributes.
    Attributes
    ------------
    sort_commands: :class:`bool`
        Whether to sort the commands in the output alphabetically. Defaults to ``True``.
    dm_help: :class:`bool`
        A bool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, none of the help
        output is DM'd. Defaults to ``False``.
    commands_heading: :class:`str`
        The command list's heading string used when the help command is invoked with a category name.
        Useful for i18n. Defaults to ``"Commands:"``
    """

    def __init__(self, **options):
        self.sort_commands = options.pop('sort_commands', True)
        self.dm_help = options.pop('dm_help', False)
        self.commands_heading = options.pop('commands_heading', "Commands:")

        self.embed_colour = discord.Colour.green()

        self.embed = discord.Embed(colour=self.embed_colour)

        super().__init__(**options)

    @property
    def ending_note(self):
        """Returns help command's ending note. This is mainly useful to override for i18n purposes."""
        command_name = self.invoked_with
        return f"Type {self.clean_prefix}{command_name} command for more info on a command."

    def add_commands(self, commands_, *, heading):
        """Indents a list of commands after the specified heading.
        The formatting is added to the :attr:`embed`.
        The default implementation is the command name followed by
        the command's :attr:`Command.short_doc`.
        Parameters
        -----------
        commands_: Sequence[:class:`Command`]
            A list of commands to indent for output.
        heading: :class:`str`
            The heading to add to the output. This is only added
            if the list of commands is greater than 0.
        """

        if not commands_:
            return

        if heading:
            self.embed.title = heading

        for command in commands_:
            val = '\u200b'
            if command.short_doc:
                val = command.short_doc
                if len(command.aliases) != 0:
                    val += f'\n*Aliases:* {", ".join(command.aliases)}'

            self.embed.add_field(
                name=command.name,
                value=val,
                inline=False
            )

    @property
    def destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        else:
            return ctx.channel

    async def send_embed(self):
        """A helper utility to send the page output from :attr:`embed` to the destination."""
        await self.destination.send(embed=self.embed)

    async def prepare_help_command(self, ctx, command=None):
        self.embed = discord.Embed(colour=self.embed_colour)
        await super().prepare_help_command(ctx, command)

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        if bot.description:
            self.embed.description = bot.description

        filtered = await self.filter_commands(bot.commands, sort=self.sort_commands)
        self.add_commands(filtered, heading=self.commands_heading)

        note = self.ending_note
        if note:
            self.embed.set_footer(text=note)

        await self.send_embed()

    async def send_command_help(self, command):
        self.add_commands([command], heading='')
        await self.send_embed()

    async def send_group_help(self, group):
        # bot = self.context.bot

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.add_commands(filtered, heading=self.commands_heading)

        note = self.ending_note
        if note:
            self.embed.set_footer(text=note)

        await self.send_embed()


class EmbedHelpCog(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = EmbedHelpCommand()
        bot.help_command.cog = self
        self.bot = bot

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(EmbedHelpCog(bot))
