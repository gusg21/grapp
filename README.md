# grapp

A small discord bot that polls a tumblr blog and makes a new discord forum thread whenever a new tumblr blog post is posted. Utilizes pytumblr and discord.py, as well as bs4 for some quick and dirty HTML parsing.

## Installation

1. Grab the requirements:

`pip install -r requirements.txt`

2. Make a script that fills in the following environment variables.

```
export GRAPP_TOKEN=(from discord API)
export GRAPP_APP_ID=(from discord API)
export GRAPP_PUB_KEY=(from discord API)

export GRAPP_TUMBLR_CONSUMER_SECRET=(from tumblr API)
export GRAPP_TUMBLR_CONSUMER_KEY=(from tumblr API)
export GRAPP_TUMBLR_TOKEN=(from tumblr API)
export GRAPP_TUMBLR_SECRET=(from tumblr API)

export GRAPP_FORUM_CHANNELS=(A comma-separated list of forum channel names to post in)

export GRAPP_TUMBLR_NAME=(The name of the tumblr blog to poll)
export GRAPP_ADMIN_DISCORD_NAME=(The username of a discord user to ping in every post)
export GRAPP_FORUM_THREAD_TEMPLATE=(The name of a discord forum post where {} is subbed for the date)
export GRAPP_FORUM_THREAD_TAGS=(A comma-separated list of tags to apply to posts)
```
