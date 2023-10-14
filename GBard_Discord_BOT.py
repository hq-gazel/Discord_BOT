import discord
from bardapi import Bard
import re, requests, os


class normal_bot():
    def __init__(self):
        # Bard Token
        self.GBard_token = ''
        os.environ['_BARD_API_KEY'] = self.GBard_token

        self.Bard_instance = Bard(token=self.GBard_token)

    async def send_split_message(self, message, text):
        # メッセージの長さが2000文字以上の場合は分割して送信
        if len(text) > 2000:
            split_contents = [text[i:i+2000] for i in range(0, len(text), 2000)]

            for split_content in split_contents:
                await message.channel.send(split_content)
        else:
            # 2000文字以下の場合はそのまま送信
            await message.channel.send(text)


    # Google Bardにメッセージ送信
    def GBard_post(self, post_str):
        return self.Bard_instance.get_answer(post_str)['content']

    def discord_api(self):
        # DiscordチャンネルID
        CHANNEL_ID = ''

        intents=discord.Intents.none()
        intents.reactions = True
        intents.messages = True
        intents.message_content = True

        # BOTトークン
        dis_TOKEN = ""
        bot = discord.Client(intents=intents)

        @bot.event
        async def on_connect():
            print('ログインしました')
            bot.get_channel(CHANNEL_ID)


        @bot.event
        async def on_message(message):
            # BOT以外のユーザーが発言したか
            if message.author == bot.user:
                return False

            # BOT宛てメッセージか
            elif re.match(r'\*', message.content):
                text = message.content.lstrip('*')
                img_exist = True

               # 添付ファイルが1つでもある場合は順番に送信する
                for url in enumerate(message.attachments):
                    file    = requests.get(url)

                    if file.status_code == 200:
                        res = await self.Bard_instance.ask_about_image(input_text=text, image=file.content, lang='ja')['content']
                        await self.send_split_message(message, res)

                    else:
                        img_exist = False

                # エラーメッセージ
                if img_exist == False:
                    await message.channel.send('申し訳ありません。一部画像が読み取れませんでした。\n\
                                                画像のURLが正しいかご確認してください。')

                else:
                    res = self.GBard_post(text)
                    await self.send_split_message(message, res)


        # 返信もらった時
        @bot.event
        async def on_raw_reaction_add(message):
            if message.author != bot.user:
                text = message.content.lstrip('*')
                res  = self.GBard_post(text)
                await self.send_split_message(message, res)

        bot.run(dis_TOKEN)

if __name__ == '__main__':
    instance = normal_bot()
    instance.discord_api()