import discord, pytumblr
import sys, os, io
import logging

### ENV

GRAPP_TOKEN = os.environ.get("GRAPP_TOKEN")
GRAPP_APP_ID = os.environ.get("GRAPP_APP_ID")
GRAPP_PUB_KEY = os.environ.get("GRAPP_PUB_KEY")

GRAPP_TUMBLR_CONSUMER_SECRET = os.environ.get("GRAPP_TUMBLR_CONSUMER_SECRET")
GRAPP_TUMBLR_CONSUMER_KEY = os.environ.get("GRAPP_TUMBLR_CONSUMER_KEY")
GRAPP_TUMBLR_TOKEN = os.environ.get("GRAPP_TUMBLR_TOKEN")
GRAPP_TUMBLR_SECRET = os.environ.get("GRAPP_TUMBLR_SECRET")

### LOGGING

logger = logging.getLogger('discord')
for h in logger.handlers:
    logger.removeHandler(h)

# Add std out logger
handler = logging.StreamHandler(stream=sys.stdout)
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# Add file logger
file_handler = logging.FileHandler(filename="grapp.log", encoding="utf-8", mode="w")
logger.addHandler(file_handler)

### APP

class GRApp(discord.Client):
    def __init__(self, tumblr_client: pytumblr.TumblrRestClient):
        super().__init__(intents=discord.Intents.all())

        self.tumblr = tumblr_client

    async def on_connect(self):
        logger.info("Connected to API, checking tumblr...")

        try:
            print(
                self.tumblr.blog_info("gumblr")
            )
        except Exception as e:
            logger.error(f"Failed to connect to tumblr")
            raise e

    async def on_ready(self):
        logger.info("Ready")

def main():
    client = pytumblr.TumblrRestClient(
        GRAPP_TUMBLR_CONSUMER_KEY,
        GRAPP_TUMBLR_CONSUMER_SECRET,
        GRAPP_TUMBLR_TOKEN,
        GRAPP_TUMBLR_SECRET,
    )

    app = GRApp(client)

    app.run(GRAPP_TOKEN)


if __name__ == "__main__":
    main()
