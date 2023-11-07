import discord, pytumblr
import discord.ext.tasks
import sys, os, datetime, bs4, time
import logging

### ENV

GRAPP_TOKEN = os.environ.get("GRAPP_TOKEN")
GRAPP_APP_ID = os.environ.get("GRAPP_APP_ID")
GRAPP_PUB_KEY = os.environ.get("GRAPP_PUB_KEY")

GRAPP_TUMBLR_CONSUMER_SECRET = os.environ.get("GRAPP_TUMBLR_CONSUMER_SECRET")
GRAPP_TUMBLR_CONSUMER_KEY = os.environ.get("GRAPP_TUMBLR_CONSUMER_KEY")
GRAPP_TUMBLR_TOKEN = os.environ.get("GRAPP_TUMBLR_TOKEN")
GRAPP_TUMBLR_SECRET = os.environ.get("GRAPP_TUMBLR_SECRET")

GRAPP_FORUM_CHANNELS = os.environ.get("GRAPP_FORUM_CHANNELS").split(",")

GRAPP_TUMBLR_NAME = os.environ.get("GRAPP_TUMBLR_NAME")
GRAPP_ADMIN_DISCORD_NAME = os.environ.get("GRAPP_ADMIN_DISCORD_NAME")
GRAPP_FORUM_THREAD_TEMPLATE = os.environ.get("GRAPP_FORUM_THREAD_TEMPLATE")
GRAPP_FORUM_THREAD_TAGS = os.environ.get("GRAPP_FORUM_THREAD_TAGS").split(",")
GRAPP_MAX_SECS_TO_POST = 60 * 20
GRAPP_CHECK_TUMBLR_EVERY_SECS = 5

GRAPP_POSTED_FILE = "posted.txt"

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

        self.tumblr: pytumblr.TumblrRestClient = tumblr_client
        self.channels: list[discord.ForumChannel] = []
        self.initial_tags: dict[string, list[discord.ForumTag]] = {}
        self.admin_mentions: dict[int, str] = {}

        self.posted = self.load_posted()

    @discord.ext.tasks.loop(seconds=GRAPP_CHECK_TUMBLR_EVERY_SECS)
    async def poll_tumblr(self):
        print("Polling tumblr...")

        raw_posts = self.tumblr.posts(GRAPP_TUMBLR_NAME, type="text", limit=1)
        
        # blog = raw_posts["blog"]
        posts = raw_posts["posts"]
        latest = posts[0]

        latest_url = latest["short_url"]
        latest_id = latest["id"]
        latest_body = latest["body"]
        latest_rendered_content = bs4.BeautifulSoup(latest_body, features="html.parser").get_text(separator="\n")
        time_since_latest = time.time() - latest["timestamp"]

        print("Latest post: ", latest_rendered_content)
        print("Latest post ID: ", latest_id)
        print("Time since post: ", time_since_latest)

        if latest_id in self.posted:
            print("Already posted this. Moving on.")
        else:
            if time_since_latest > GRAPP_MAX_SECS_TO_POST:
                print("Post too old, not posting...")
            else:
                print(">>>>>> !!! Posting to discord...")
                await self.post(latest_rendered_content + "\n\n_" + latest_url + "_ ")
                self.posted.append(latest_id)


    def load_posted(self):
        print("Loading posted IDs...")

        try:
            posted_file = open(GRAPP_POSTED_FILE, "r")
            posted_ids = [int(line) for line in posted_file.readlines()]
        except:
            return []

        return posted_ids
    
    def save_posted(self):
        print("Saving posted IDs...")

        posted_file = open(GRAPP_POSTED_FILE, "w+")
        posted_file.write(
            "\n".join([str(id) for id in self.posted])
        )


    async def on_connect(self):
        logger.info("Connected to API, checking tumblr...")

        try:
            print(
                self.tumblr.blog_info(GRAPP_TUMBLR_NAME)
            )
        except Exception as e:
            logger.error(f"Failed to connect to tumblr")
            raise e

    async def on_ready(self):
        logger.info("Ready")

        await self.update_channels()

        self.poll_tumblr.start()

    # saving handlers
    async def on_disconnect(self):
        self.save_posted()

    async def on_error(self):
        self.save_posted()

    async def close(self):
        self.save_posted()

        await super().close()

    async def post(self, content: str):
        for c in self.channels:
            print("posting to " + str(c))

            content = self.admin_mentions[c.guild.id] + "\n\n" + content

            tags = self.initial_tags[c.name]
            dt = "{:%m/%d/%y}".format(datetime.datetime.now())
            await c.create_thread(name=GRAPP_FORUM_THREAD_TEMPLATE.format(dt), content=content, applied_tags=tags)

    async def update_channels(self):
        for guild in self.guilds:
            print("scanning guild " + str(guild))
            for member in guild.members:
                if member.name == GRAPP_ADMIN_DISCORD_NAME:
                    print("found admin in guild " + str(guild))
                    self.admin_mentions[guild.id] = member.mention

            for channel in guild.channels:
                print(channel)
                if channel.name in GRAPP_FORUM_CHANNELS:
                    print("channel with correct name in guild " + str(guild))
                    if type(channel) == discord.channel.ForumChannel:
                        print("found channel " + str(channel))
                        for tag in channel.available_tags:
                            if tag.name in GRAPP_FORUM_THREAD_TAGS:
                                print("adding tag {} for channel {} on guild {}".format(tag, channel, guild))
                                if not channel.name in self.initial_tags.keys():
                                    self.initial_tags[channel.name] = []
                                self.initial_tags[channel.name].append(tag)

                        self.channels.append(channel)


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
