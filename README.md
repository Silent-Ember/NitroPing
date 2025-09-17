# NitroPing

![NitroPing Banner](https://i.ibb.co/JjGWzycT/Nitro-Ping-Banner-3.png)

<p align="center">
<a href="https://top.gg/bot/1411081092689166460">
  <img src="https://top.gg/api/widget/servers/1411081092689166460.svg" alt="Top.gg Widget">
</a>
</p>

**NitroPing** is a Discord bot designed to manage and celebrate server boosts.  
It provides **automated notifications**, **role management**, **custom embeds**, and an **admin toolkit** to keep your community engaged.  
Built with `discord.py`, NitroPing is lightweight, fast, and perfect for servers of all sizes.

---

## ✨ Features

- **Boost Notifications** → Sends stylish purple embeds when users start or stop boosting.
- **Role Management** → Automatically assigns or removes booster roles you choose.
- **Customizable Messages** → Personalize thank-you messages with `/set_message`.
- **Interactive Role Picker** → Select booster roles using a dropdown.
- **Booster List** → See all current boosters and their support duration.
- **Testing Tools** → Safely preview boost messages with `/test_boost` and `/test_boostloss`.
- **Top.gg Integration** → Encourage votes with `/vote` and check them with `/has_voted`.
- **Config Import/Export** → Save or restore per-guild settings with JSON files.
- **Lightweight & Reliable** → No database, just per-guild JSON configs for simplicity.

---

## 🚀 Installation

### Prerequisites
- Python **3.8+**
- `discord.py` 2.x → `pip install discord.py`
- `python-dotenv` → `pip install python-dotenv`
- A bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Setup
```bash
# Clone repository
git clone https://github.com/Silent-Ember/NitroPing.git
cd nitroping

# Install dependencies
pip install -r requirements.txt
````

Create a `.env` file:

```env
BOT_TOKEN=your_discord_bot_token_here
TOPGG_API_TOKEN=optional_topgg_api_token
TOPGG_BOT_ID=1411081092689166460
TOPGG_WEBHOOK_AUTH=changeme
```

Run the bot:

```bash
python bot.py
```

Invite the bot:
[Click here](https://discord.com/oauth2/authorize?client_id=1411081092689166460&permissions=268553232&scope=bot%20applications.commands)

---

## ⚙️ Configuration

### Set Boost Channel

```bash
/set_channel #boosts
```

### Set Custom Message

```bash
/set_message Thank you for boosting our community!
```

### Assign Booster Roles

```bash
/set_roles
```

### Test Notifications

```bash
/test_boost
/test_boostloss
```

### Export/Import Config

```bash
/config_export
/config_import <json file>
```

---

## 📜 Commands

| Command                   | Description                                         | Admin Only |
|----------------------------|-----------------------------------------------------|------------|
| `/invite`                  | Get the bot's invite link                           | No         |
| `/boosters`                | List current boosters with duration                 | No         |
| `/support`                 | Get the support server link                         | No         |
| `/credits`                 | View bot credits                                    | No         |
| `/help`                    | Show available commands                             | No         |
| `/vote`                    | Get the Top.gg voting link                          | No         |
| `/sync`                    | Force sync commands for this guild                  | Yes        |
| `/status`                  | Show bot status & current config                    | Yes        |
| `/set_channel`             | Set channel for boost notifications                 | Yes        |
| `/channel_unset`           | Unset boost channel                                 | Yes        |
| `/set_message`             | Set custom thank-you message                        | Yes        |
| `/set_roles`               | Configure booster roles (dropdown)                  | Yes        |
| `/reset_roles`             | Clear configured booster roles                      | Yes        |
| `/roles_list`              | Show configured booster roles                       | Yes        |
| `/test_boost`              | Send a test boost embed                             | Yes        |
| `/test_boostloss`          | Send a test boost loss embed                        | Yes        |
| `/boost_message_preview`   | Preview current boost message                       | Yes        |
| `/config_show`             | Show this guild's JSON config                       | Yes        |
| `/config_export`           | Export guild config as a file                       | Yes        |
| `/config_import <file>`    | Import guild config from a JSON file                | Yes        |
| `/has_voted <user>`        | Check if a user has voted on Top.gg                 | Yes        |

---

## 📂 Folder Structure

```
nitroping/
├── bot.py              # Main bot script
├── .env                # Environment file
├── servers/            # Guild configs
│   ├── <guild_id>/     
│   │   ├── <guild_id>.json  # Guild settings
│   │   ├── images/          # Uploaded boost images
├── requirements.txt    # Dependencies
└── README.md           # This file
```

---

## 💬 Support

* Join our [Support Server](https://discord.gg/Y64smue5uZ)
* Report issues via [GitHub Issues](https://github.com/Silent-Ember/NitroPing/issues)

---

## 👑 Credits

* **Developer** → Sketch494
* **Hosting** → [Silent Ember Hosting](https://silent-ember.com)
* **Banner** → Custom NitroPing branding

---

## 📜 License

Licensed under the MIT License. See [LICENSE](LICENSE).

---

⭐ *If you like NitroPing, please give it a star on GitHub!*
[![Star History Chart](https://api.star-history.com/svg?repos=Silent-Ember/NitroPing\&type=Date)](https://www.star-history.com/#Silent-Ember/NitroPing&Date)
