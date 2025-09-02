# bot.py
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# --------------------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------------------
BASE_PATH = Path(__file__).resolve().parent
ENV_PATH = BASE_PATH / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN or not TOKEN.strip():
    print("[NitroPing] ERROR: BOT_TOKEN is missing.")
    print(f"[NitroPing] Looked for .env at: {ENV_PATH}")
    print(f"[NitroPing] .env exists? {ENV_PATH.exists()}")
    print(f"[NitroPing] Current working dir: {Path.cwd()}")
    sys.exit(1)

# --------------------------------------------------------------------------------------
# Discord Intents & helpers
# --------------------------------------------------------------------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

UTCNOW = getattr(discord.utils, "utcnow", datetime.utcnow)

SERVERS_DIR = BASE_PATH / "servers"
SERVERS_DIR.mkdir(parents=True, exist_ok=True)

def ensure_guild_config(guild_id: int) -> Path:
    gdir = SERVERS_DIR / str(guild_id)
    gdir.mkdir(parents=True, exist_ok=True)
    cfg = gdir / f"{guild_id}.json"
    if not cfg.exists():
        cfg.write_text(
            json.dumps(
                {"channel_id": None, "message": "Thank you for boosting the server!", "roles": []},
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    return cfg

def admin_only(func):
    func = app_commands.default_permissions(administrator=True)(func)
    func = app_commands.checks.has_permissions(administrator=True)(func)
    return func

def resolve_announce_channel(bot: commands.Bot, guild: discord.Guild, config: dict) -> discord.abc.Messageable | None:
    """Prefer configured channel; else fallback to system channel if present."""
    channel = None
    channel_id = config.get("channel_id")
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            try:
                # Try fetching if not cached
                channel = bot.loop.create_task(bot.fetch_channel(int(channel_id)))  # will be awaited when used
            except Exception:
                channel = None
    if channel is None:
        channel = guild.system_channel
    return channel

# --------------------------------------------------------------------------------------
# Bot class
# --------------------------------------------------------------------------------------
class NitroPing(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        self.bot_name = "NitroPing"
        self.boost_emoji = "<a:nitro:1411082919019155456>"
        self.footer_emoji = "<:boostergem:1411082984450162718>"  # (not used in footer anymore)
        self._boost_counts: dict[int, int] = {}

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"[NitroPing] Synced {len(synced)} app commands.")
        except Exception as e:
            print(f"[NitroPing] WARNING: tree.sync() failed: {e}")

    async def on_ready(self):
        print(f"[NitroPing] discord.py: {discord.__version__}")
        for g in self.guilds:
            ensure_guild_config(g.id)
            try:
                self._boost_counts[g.id] = getattr(g, "premium_subscription_count", 0) or 0
            except Exception:
                self._boost_counts[g.id] = 0
        print(f"[NitroPing] Logged in as {self.user} (ID: {self.user.id})")
        await self.update_presence()

    async def update_presence(self):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers")
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild: discord.Guild):
        ensure_guild_config(guild.id)
        try:
            self._boost_counts[guild.id] = getattr(guild, "premium_subscription_count", 0) or 0
        except Exception:
            self._boost_counts[guild.id] = 0
        await self.update_presence()

    async def on_guild_remove(self, guild: discord.Guild):
        self._boost_counts.pop(guild.id, None)
        await self.update_presence()

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Backup announcer: if total boost count increases, send a message even if member event was missed."""
        try:
            before_cnt = getattr(before, "premium_subscription_count", 0) or 0
            after_cnt = getattr(after, "premium_subscription_count", 0) or 0
        except Exception:
            return

        # If it increased, announce
        if after_cnt > before_cnt:
            config_path = ensure_guild_config(after.id)
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {"channel_id": None, "message": "Thank you for boosting the server!", "roles": []}

            channel = resolve_announce_channel(self, after, cfg)
            # If resolve_announce_channel returned a Task (fetch), await it
            if isinstance(channel, asyncio.Task):
                try:
                    channel = await channel
                except Exception:
                    channel = None
            if not channel:
                self._boost_counts[after.id] = after_cnt
                return

            gained = after_cnt - before_cnt
            embed = discord.Embed(
                title=f"{self.boost_emoji} New Server Boost{'s' if gained>1 else ''}! {self.boost_emoji}",
                description=f"We just received **{gained}** new boost{'s' if gained>1 else ''}! {cfg.get('message','Thank you for boosting the server!')}",
                color=discord.Color.purple(),
                timestamp=UTCNOW()
            )
            embed.set_footer(text=f"{self.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")
            try:
                if after.icon:
                    embed.set_thumbnail(url=after.icon.url)
            except Exception:
                pass

            try:
                await channel.send(embed=embed)
            except Exception:
                pass

        self._boost_counts[after.id] = after_cnt

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.premium_since == after.premium_since:
            return

        guild_id = after.guild.id
        user_id = after.id
        config_file = ensure_guild_config(guild_id)
        user_file = SERVERS_DIR / str(guild_id) / f"{user_id}.json"

        try:
            with config_file.open("r", encoding="utf-8") as f:
                config = json.load(f)

            channel = resolve_announce_channel(self, after.guild, config)
            if isinstance(channel, asyncio.Task):
                try:
                    channel = await channel
                except Exception:
                    channel = None
            if channel is None:
                return

            embed = discord.Embed(
                title=f"{self.boost_emoji} Server Boost Update {self.boost_emoji}",
                color=discord.Color.purple(),
                timestamp=UTCNOW()
            )
            try:
                embed.set_thumbnail(url=after.display_avatar.url)
            except Exception:
                pass

            # Footer WITHOUT emojis (per request)
            embed.set_footer(text=f"{self.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

            user_data = {'boost_start': None}
            if user_file.exists():
                user_data = json.loads(user_file.read_text(encoding="utf-8"))

            if after.premium_since and not before.premium_since:
                # Started boosting
                boost_start = after.premium_since
                if boost_start and boost_start.tzinfo is not None:
                    boost_start = boost_start.astimezone(tz=None).replace(tzinfo=None)
                user_data['boost_start'] = (boost_start or datetime.utcnow()).isoformat()

                embed.description = f"{after.mention} {config.get('message', 'Thank you for boosting the server!')}"
                for role_id in config.get('roles', []):
                    role = after.guild.get_role(int(role_id))
                    if role:
                        try:
                            await after.add_roles(role, reason="Started boosting")
                        except discord.Forbidden:
                            pass
            elif before.premium_since and not after.premium_since:
                # Stopped boosting
                user_data['boost_start'] = None
                embed.description = f"{after.mention} stopped boosting the server. Thank you for your support!"
                for role_id in config.get('roles', []):
                    role = after.guild.get_role(int(role_id))
                    if role:
                        try:
                            await after.remove_roles(role, reason="Stopped boosting")
                        except discord.Forbidden:
                            pass
            else:
                embed.description = f"{after.mention} updated their boost status."

            user_file.write_text(json.dumps(user_data, ensure_ascii=False), encoding="utf-8")
            await channel.send(embed=embed)

        except Exception as e:
            print(f"[NitroPing] Error in on_member_update: {e}")

bot = NitroPing()

# --------------------------------------------------------------------------------------
# Interactive Role Config View for /set_roles
# --------------------------------------------------------------------------------------
class RolesConfigView(discord.ui.View):
    def __init__(self, guild: discord.Guild, author_id: int, config_file: Path):
        super().__init__(timeout=300)
        self.guild = guild
        self.author_id = author_id
        self.config_file = config_file
        self.selected_ids: list[str] = []

        # Build manageable role options (Discord max 25 options)
        bot_member = guild.me
        manageables = []
        if bot_member and bot_member.top_role:
            top = bot_member.top_role
            for r in guild.roles:
                if r.is_default():
                    continue
                if r.managed:  # bot/integration managed
                    continue
                if r >= top:   # can't manage roles >= bot's top role
                    continue
                manageables.append(r)

        manageables = list(reversed(manageables))
        manageables = manageables[:25]

        options = [
            discord.SelectOption(label=r.name[:100], value=str(r.id), description=f"ID {r.id}")
            for r in manageables
        ]

        max_vals = min(25, max(1, len(options))) if options else 1

        self.select = discord.ui.Select(
            placeholder="Select booster roles (multi-select)",
            min_values=0,
            max_values=max_vals,
            options=options,
            row=0
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

        self.add_item(self.SaveButton(self))
        self.add_item(self.CancelButton(self))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    async def select_callback(self, interaction: discord.Interaction):
        self.selected_ids = list(self.select.values)
        await interaction.response.defer()

    class SaveButton(discord.ui.Button):
        def __init__(self, parent: "RolesConfigView"):
            super().__init__(label="Save", style=discord.ButtonStyle.success, row=1)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            try:
                with self.parent.config_file.open("r", encoding="utf-8") as f:
                    config = json.load(f)
                config["roles"] = self.parent.selected_ids
                self.parent.config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

                embed = discord.Embed(
                    title="Booster Roles Updated",
                    color=discord.Color.purple(),
                    timestamp=UTCNOW()
                )
                role_mentions = []
                for rid in self.parent.selected_ids:
                    r = self.parent.guild.get_role(int(rid))
                    if r:
                        role_mentions.append(r.mention)
                display = ", ".join(role_mentions) if role_mentions else "*None*"
                embed.add_field(name="Roles", value=display, inline=False)
                embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

                await interaction.response.edit_message(embed=embed, view=None)
            except Exception as e:
                await interaction.response.edit_message(content=f"Error saving roles: {e}", view=None)

    class CancelButton(discord.ui.Button):
        def __init__(self, parent: "RolesConfigView"):
            super().__init__(label="Cancel", style=discord.ButtonStyle.secondary, row=1)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.edit_message(content="Cancelled.", embed=None, view=None)

# --------------------------------------------------------------------------------------
# Slash commands
# --------------------------------------------------------------------------------------
@bot.tree.command(name="invite", description="Get the bot invite link")
async def invite(interaction: discord.Interaction):
    url = "https://discord.com/oauth2/authorize?client_id=1411081092689166460"
    await interaction.response.send_message(f"Add **{bot.bot_name}** to your server:\n{url}", ephemeral=True)

@bot.tree.command(name="test_boost", description="Test the boost notification (Admin only)")
@admin_only
async def test_boost(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        channel_id = config.get('channel_id')
        if not channel_id:
            await interaction.response.send_message("No boost channel set! Use /set_channel first.", ephemeral=True)
            return

        channel = bot.get_channel(int(channel_id)) or await bot.fetch_channel(int(channel_id))

        embed = discord.Embed(
            title=f"{bot.boost_emoji} Test Server Boost {bot.boost_emoji}",
            description=f"{interaction.user.mention} {config.get('message','Thank you for boosting the server!')}",
            color=discord.Color.purple(),
            timestamp=UTCNOW()
        )
        try:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        except Exception:
            pass
        embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

        await channel.send(embed=embed)
        await interaction.response.send_message("Test boost message sent!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="test_boostloss", description="Test the boost loss notification (Admin only)")
@admin_only
async def test_boostloss(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        channel_id = config.get('channel_id')
        if not channel_id:
            await interaction.response.send_message("No boost channel set! Use /set_channel first.", ephemeral=True)
            return

        channel = bot.get_channel(int(channel_id)) or await bot.fetch_channel(int(channel_id))

        embed = discord.Embed(
            title=f"{bot.boost_emoji} Test Boost Loss {bot.boost_emoji}",
            description=f"{interaction.user.mention} stopped boosting the server. Thank you for your support!",
            color=discord.Color.purple(),
            timestamp=UTCNOW()
        )
        try:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        except Exception:
            pass
        embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

        await channel.send(embed=embed)
        await interaction.response.send_message("Test boost loss message sent!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="set_channel", description="Set the channel for boost notifications (Admin only)")
@admin_only
@app_commands.describe(channel="The channel to send boost notifications to")
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        config['channel_id'] = str(channel.id)
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

        await interaction.response.send_message(f"Boost notifications channel set to {channel.mention}", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="channel_unset", description="Unset the boost notifications channel (Admin only)")
@admin_only
async def channel_unset(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        config['channel_id'] = None
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

        await interaction.response.send_message("Boost notifications channel unset", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="set_message", description="Set the boost thank you message (Admin only)")
@admin_only
@app_commands.describe(message="The new thank you message")
async def set_message(interaction: discord.Interaction, message: str):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        config['message'] = message
        config_file.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

        await interaction.response.send_message("Boost thank you message updated!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# ===== NEW: Interactive /set_roles with role embed & dropdown =====
@bot.tree.command(name="set_roles", description="Set roles to give/remove for boosters (Admin only)")
@admin_only
async def set_roles(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    embed = discord.Embed(
        title="Configure Booster Roles",
        description="Select one or more roles from the dropdown, then press **Save**.\n"
                    "Only roles the bot can manage are shown (max 25).",
        color=discord.Color.purple(),
        timestamp=UTCNOW()
    )
    embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

    view = RolesConfigView(interaction.guild, interaction.user.id, config_file)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="roles_list", description="List configured boost roles (Admin only)")
@admin_only
async def roles_list(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    config_file = ensure_guild_config(guild_id)

    try:
        with config_file.open('r', encoding="utf-8") as f:
            config = json.load(f)

        roles = config.get('roles', [])
        if not roles:
            await interaction.response.send_message("No boost roles configured!", ephemeral=True)
            return

        role_mentions = [interaction.guild.get_role(int(r)).mention for r in roles if interaction.guild.get_role(int(r))]
        embed = discord.Embed(
            title="Configured Booster Roles",
            description=", ".join(role_mentions) if role_mentions else "*None*",
            color=discord.Color.purple(),
            timestamp=UTCNOW()
        )
        embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="boosters", description="List current server boosters")
async def boosters(interaction: discord.Interaction):
    guild = interaction.guild
    boosters = [m for m in guild.members if m.premium_since]
    page_size = 10
    pages = [boosters[i:i + page_size] for i in range(0, len(boosters), page_size)]
    current_page = 0

    if not boosters:
        await interaction.response.send_message("No boosters found!", ephemeral=True)
        return

    def get_embed(page_idx: int):
        embed = discord.Embed(
            title=f"{bot.boost_emoji} Server Boosters {bot.boost_emoji}",
            color=discord.Color.purple(),
            timestamp=UTCNOW()
        )
        embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")
        for booster in pages[page_idx]:
            since = booster.premium_since
            if since and since.tzinfo is not None:
                since = since.astimezone(tz=None).replace(tzinfo=None)
            days = (datetime.utcnow() - (since or datetime.utcnow())).days
            embed.add_field(name=booster.display_name, value=f"Boosting for {days} days", inline=False)
        if guild.icon:
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except Exception:
                pass
        return embed

    view = discord.ui.View(timeout=None)

    async def next_callback(inter: discord.Interaction):
        nonlocal current_page
        current_page = (current_page + 1) % len(pages)
        await inter.response.edit_message(embed=get_embed(current_page), view=view)

    if len(pages) > 1:
        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)
        next_button.callback = next_callback
        view.add_item(next_button)

    await interaction.response.send_message(embed=get_embed(current_page), view=view)

@bot.tree.command(name="support", description="Get support server invite")
async def support(interaction: discord.Interaction):
    await interaction.response.send_message("Join our support server: https://discord.gg/Y64smue5uZ", ephemeral=True)

@bot.tree.command(name="credits", description="View bot credits")
async def credits(interaction: discord.Interaction):
    # Embed 1/2: banner only
    embed1 = discord.Embed(color=discord.Color.purple())
    embed1.set_image(url="https://i.ibb.co/6QfPTnh/1credits.png")

    # Embed 2/2: gem + bot name, fields, and matching banner image
    embed2 = discord.Embed(
        title=f"<:boostergem:1411082984450162718> {bot.bot_name}",
        color=discord.Color.purple(),
        timestamp=UTCNOW()
    )
    embed2.add_field(name="Developers", value="Sketch494", inline=False)
    embed2.add_field(
        name="Bot host",
        value="[Silent Ember Hosting](https://silent-ember.com/)",
        inline=False
    )
    # Use a banner image to match size/feel with embed1
    embed2.set_image(url="https://i.ibb.co/5WjymY0h/Nitro-Ping-Banner-2.png")

    await interaction.response.send_message(embeds=[embed1, embed2], ephemeral=True)

@bot.tree.command(name="help", description="View available commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"{bot.boost_emoji} {bot.bot_name} Help {bot.boost_emoji}",
        color=discord.Color.purple(),
        timestamp=UTCNOW()
    )
    embed.set_footer(text=f"{bot.bot_name} • Silent Ember Hosting • {datetime.utcnow().strftime('%Y-%m-%d')}")

    commands_list = [
        ("/invite", "Get the bot invite link"),
        ("/boosters", "List current server boosters and their boost duration"),
        ("/support", "Get invite to the support server"),
        ("/credits", "View bot credits"),
        ("/help", "Show this help message")
    ]

    if interaction.user.guild_permissions.administrator:
        commands_list.extend([
            ("/test_boost", "Test boost notification"),
            ("/test_boostloss", "Test boost loss notification"),
            ("/set_channel", "Set channel for boost notifications"),
            ("/channel_unset", "Unset boost notifications channel"),
            ("/set_message", "Set boost thank you message"),
            ("/set_roles", "Interactive role picker for boosters"),
            ("/roles_list", "List configured boost roles")
        ])

    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# --------------------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------------------
try:
    major, minor, *_ = map(int, discord.__version__.split("."))
    if major < 2:
        print("[NitroPing] ERROR: discord.py 2.x is required.")
        sys.exit(1)
except Exception:
    pass

bot.run(TOKEN)
