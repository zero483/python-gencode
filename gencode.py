import nextcord
import pytz
from nextcord.ext import commands
import asyncio
import json
from nextcord.ext.commands import has_permissions
import mysql.connector
import random
import string

with open("config.json", mode="r", encoding="utf-8") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["TOKEN"]

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

DATABASE_HOST = config["Datenbank_Host"]
DATABASE_USER = config["Datenbank_User"]
DATABASE_PASSWORD = config["Datenbank_Password"]
DATABASE_DATABASE = config["Datenbank_Database"]
DATABASE_PORT = config["Datenbank_port"]
ALLOWED_ROLE_NAME = config["Allowed_Role"]

db_config = {
    "host": DATABASE_HOST,
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "database": DATABASE_DATABASE,
    "port": DATABASE_PORT
}

def split_key(key):
    return '-'.join([key[i:i+4] for i in range(0, len(key), 4)])

@bot.slash_command(guild_ids=None)
async def generiere_key(ctx, member:nextcord.Member, reward:str):
    global conn, cursor
    user = ctx.user
    allowed_role = nextcord.utils.get(user.roles, name=ALLOWED_ROLE_NAME)
    if not allowed_role:
        await ctx.send("Du hast keine Rechte für diesen Command!", ephemeral=True)
        return

    try:
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        formatted_key = split_key(key)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = "INSERT INTO redeemcodes (code, reward) VALUES (%s, %s)"
        cursor.execute(insert_query, (formatted_key, reward))
        conn.commit()

        
        # You can change the code
        keyembed = nextcord.Embed(
            title="Key Generator :key:",
            description=f"Unten findest du deinen Key, du kannst ihn wie folgt einlösen:\n\n\n**1.** Connecte auf Server\n**2.** Öffne die F8 Konsole\n**3.** Schreibe /key und drücke Enter\n**4.** Gebe deinen Key in die Zeile ein\n\nKey: **{formatted_key}**\nBelohnung: **{reward}**",
            color=0xbf00ff
        )

        await member.send(embed=keyembed)
        await ctx.send(f"Der Code wurde an {member.global_name} gesendet!", ephemeral=True)

        logembed = nextcord.Embed(
            title="Key Generator :key:",
            description=f"Der Admin **{ctx.user.display_name}** hat an **{member.global_name}** einen Code geschickt!\nBelohnung: **{reward}**",
            color=0xbf00ff
        )
        await bot.get_channel(1167177527224184832).send(embed=logembed)

    except Exception as e:
        await ctx.send(f'Fehler beim Hinzufügen des Schlüssels zur Datenbank: {str(e)}')

    finally:
        cursor.close()
        conn.close()

@bot.slash_command(description="Load the Redeem SQL", guild_ids=None)
async def loadredeem(ctx: nextcord.Interaction):
    # Check if the user has the allowed role
    user = ctx.user
    allowed_role = nextcord.utils.get(user.roles, name=ALLOWED_ROLE_NAME)
    if not allowed_role:
        await ctx.send("Du hast keine Rechte für diesen Command!", ephemeral=True)
        return

    try:
        db_config = {
            "host": DATABASE_HOST,
            "user": DATABASE_USER,
            "password": DATABASE_PASSWORD,
            "database": DATABASE_DATABASE,
            "port": DATABASE_PORT
        }

        conn = mysql.connector.connect(**db_config)

        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS redeemcodes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(255) NOT NULL,
            reward VARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        cursor.close()
        conn.close()

        await ctx.send("Die Redeem SQL wurde erfolgreich geladen.", ephemeral=True)

    except Exception as e:
        print(f"Fehler bei der Verbindung zur MySQL-Datenbank: {str(e)}")
        await ctx.send("Es gab einen Fehler bei der Verbindung zur MySQL-Datenbank.", ephemeral=True)


@bot.event
async def on_ready():
    print("Bot ist gestartet!")
    bot.add_view(MyView())
    bot.add_view(delete())

    try:
        db_config = {
            "host": DATABASE_HOST,
            "user": DATABASE_USER,
            "password": DATABASE_PASSWORD,
            "database": DATABASE_DATABASE,
            "port": DATABASE_PORT
        }

        conn = mysql.connector.connect(**db_config)
        print("Bot ist mit der MySQL-Datenbank verbunden!")

        conn.close()

    except Exception as e:
        print(f"Fehler bei der Verbindung zur MySQL-Datenbank: {str(e)}")

bot.run(BOT_TOKEN)