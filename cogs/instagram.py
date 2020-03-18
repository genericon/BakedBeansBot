import discord
from discord.ext import tasks, commands

import os
import asyncio
from instagram_private_api import Client as IgClient

# See https://github.com/ping/instagram_private_api

class InstagramCog(commands.Bot):
    def __init__(self, bot):
        self.bot = bot
        self.ig_api = IgClient(
            os.environ.get('IG_USERNAME'),
            os.environ.get('IG_PASSWORD'),
            auto_patch=True
        )

    @classmethod
    async def is_rsfa_admin(cls, ctx):
        try:
            guild = ctx.bot.get_guild(ctx.bot.config['server'])
            member = guild.get_member(ctx.author.id)
            return member.guild_permissions.administrator
        except:
            return False

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def ig_broadcast(self, ctx, uname: str):
        logging.info(f'Getting Instagram broadcast info for "{uname}"')
        u_id = self.ig_api.username_info(uname)['user']['id']
        logging.debug(f'"{uname}" corresponds to user id "{u_id}"')
        b_id = self.ig_api.user_story_feed(u_id)['broadcast']
        logging.debug(f'"{uname}" ({u_id}) is broadcasting ({b_id})')
        b_info = self.ig_api.broadcast_info(b_id)
        dash = b_info['dash_playback_url']
        rtmp = b_info['rtmp_playback_url']
        logging.debug(f'{b_id}: DASH - {dash}')
        logging.debug(f'{b_id}: RTMP - {rtmp}')
        await ctx.send(f"**DASH:** {dash}\n**RTMP:** {rtmp}")

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def ig_follow(self, ctx, uname: str):
        logging.info(f'Following "{uname}" on Instagram')
        u_id = self.ig_api.username_info(uname)['user']['id']
        logging.debug(f'"{uname}" corresponds to id "{u_id}"')
        self.ig_api.friendships_create(u_id)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(InstagramCog(bot))
