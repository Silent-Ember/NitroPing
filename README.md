⭐️ Star History
 Please give this repository a star if you like it. This will help us grow and reach even more people!


[![Star History Chart](https://api.star-history.com/svg?repos=Silent-Ember/NitroPing&type=Date)](https://www.star-history.com/#Silent-Ember/NitroPing&Date)

# NitroPing

![NitroPing Banner](https://i.ibb.co/jkCBJ2RK/71505-booster-gem-24months.png)

**NitroPing** is a Discord bot designed to manage and celebrate server boosts. It provides automated notifications for boost events, role management for boosters, and a suite of administrative commands to customize the experience. Built with `discord.py`, NitroPing is lightweight, easy to set up, and perfect for enhancing your server's boost engagement.

## Features

- **Boost Notifications**: Automatically sends embed messages to a designated channel when users start or stop boosting the server.
- **Role Management**: Assigns or removes specified roles for users when they start or stop boosting.
- **Customizable Messages**: Allows server admins to set custom thank-you messages for boosters.
- **Interactive Role Picker**: Configure booster roles using an interactive dropdown menu.
- **Booster List**: Displays a paginated list of current server boosters with their boost duration.
- **Admin Commands**: Secure commands for configuring channels, roles, and testing notifications (admin-only).
- **Support Server**: Get help via the dedicated support server.
- **Lightweight & Reliable**: Built with `discord.py` 2.x for optimal performance and compatibility.

## Installation

### Prerequisites
- Python 3.8+
- `discord.py` 2.x (`pip install discord.py`)
- `python-dotenv` (`pip install python-dotenv`)
- A Discord bot token (from the [Discord Developer Portal](https://discord.com/developers/applications))
- A server with manage roles and send messages permissions for the bot

### Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/nitroping.git
   cd nitroping
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` File**
   In the project root, create a `.env` file with your bot token:
   ```
   BOT_TOKEN=your_discord_bot_token_here
   ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```

5. **Invite the Bot**
   Use the `/invite` command in Discord to get the bot's invite link, or generate one from the Discord Developer Portal with the following scopes:
   - `bot`
   - `applications.commands`
   Required permissions:
   - Manage Roles
   - Send Messages
   - Embed Links
   - Read Message History

   Example invite link: [Click here](https://discord.com/oauth2/authorize?client_id=1411081092689166460&permissions=268438544&scope=bot%20application.commands)

## Configuration

1. **Set Notification Channel**
   Use the `/set_channel` command to specify where boost notifications will be sent:
   ```
   /set_channel #channel-name
   ```

2. **Set Custom Thank-You Message**
   Customize the boost thank-you message with:
   ```
   /set_message Thank you for boosting our community!
   ```

3. **Configure Booster Roles**
   Use the interactive `/set_roles` command to select roles to assign/remove for boosters. Only roles below the bot's highest role and non-managed roles are shown.

4. **Test Notifications**
   Admins can test boost notifications with:
   ```
   /test_boost
   /test_boostloss
   ```

## Commands

| Command            | Description                                          | Admin Only |
|--------------------|-----------------------------------------------------|------------|
| `/invite`          | Get the bot's invite link                           | No         |
| `/boosters`        | List current server boosters and their boost duration | No         |
| `/support`         | Get the support server invite                       | No         |
| `/credits`         | View bot credits                                    | No         |
| `/help`            | Show available commands                             | No         |
| `/test_boost`      | Test boost notification                             | Yes        |
| `/test_boostloss`  | Test boost loss notification                        | Yes        |
| `/set_channel`     | Set channel for boost notifications                 | Yes        |
| `/channel_unset`   | Unset boost notifications channel                   | Yes        |
| `/set_message`     | Set boost thank-you message                         | Yes        |
| `/set_roles`       | Interactive role picker for boosters                | Yes        |
| `/roles_list`      | List configured boost roles                         | Yes        |

## Folder Structure

```
nitroping/
├── bot.py              # Main bot script
├── .env                # Environment file for bot token
├── servers/            # Per-server configuration and user data
│   ├── <guild_id>/     # Guild-specific folder
│   │   ├── <guild_id>.json  # Guild config (channel, message, roles)
│   │   ├── <user_id>.json   # User boost data
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Support

Join our [Support Server](https://discord.gg/Y64smue5uZ) for help, feature requests, or bug reports.

## Credits

- **Developer**: Sketch494
- **Bot Host**: [Silent Ember Hosting](https://silent-ember.com/)
- **Banner**: [NitroPing Banner](https://i.ibb.co/6QfPTnh/1credits.png)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Powered by Silent Ember Hosting*
```
https://silent-ember.com
```
