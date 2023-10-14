import discord
from sydney.sydney import SydneyClient
import re, requests, os

# Bing Chatを手動で

class Bing_BOT():
    def __init__(self):
        self.word_type = 'balanced'

    async def send_split_message(self, message, text):
        # メッセージの長さが2000文字以上の場合は分割して送信
        if len(text) > 2000:
            split_contents = [text[i:i+2000] for i in range(0, len(text), 2000)]

            for split_content in split_contents:
                await message.channel.send(split_content)

        # 2000文字以下の場合はそのまま送信
        else:
            await message.channel.send(text)


    def discord_api(self):
        # Discord チャンネルID
        CHANNEL_ID = ''

        intents=discord.Intents.none()
        intents.reactions = True
        intents.messages = True
        intents.message_content = True

        # Bing AI
        os.environ['BING_U_COOKIE'] = ''

        # バランス型
        self.Bing_instance = SydneyClient(style=self.word_type)

        # Discord BOTトークン
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
            elif re.match(r'\+', message.content):
                if re.match(r'\+バランス', message.content):
                    self.word_type = 'balanced'
                    self.Bing_instance.reset_conversation(style=self.word_type)
                    await message.channel.send('では、これからバランスをとって喋ります。')
                    return

                elif re.match(r'\+厳密', message.content):
                    self.word_type = 'precise'
                    self.Bing_instance.reset_conversation(style=self.word_type)
                    await message.channel.send('では、これから厳密的に喋ります。')
                    return

                elif re.match(r'\+創造', message.content):
                    self.word_type = 'creative'
                    self.Bing_instance.reset_conversation(style=self.word_type)
                    await message.channel.send('では、これから創造的に喋ります。')
                    return

                elif re.match(r'\+help', message.content):
                    text = '---ヘルプ\n \
                            バランス = balanced \n \
                            厳密 = precise \n \
                            創造 = creative'

                    await message.channel.send(text)
                    return

                # Bing Chatをスタートさせる為に必要
                await self.Bing_instance.start_conversation()
                text = message.content.lstrip('+')
                #img_exist = True

                #if len(message.attachments) > 0:

                # 添付ファイルが1つでもある場合は順番に送信する
                #    for url in message.attachments:
                #        file    = requests.get(url)

                 #       if file.status_code == 200:
                 #           res = await self.Bing_instance.compose_stream(input_text=text, image=file.content, lang='ja')['content']
                 #           await self.send_split_message(message, res)

                 #       else:
                 #           img_exist = False

                 #   # エラーメッセージ
                 #   if img_exist == False:
                 #       await message.channel.send('申し訳ありません。一部画像が読み取れませんでした。\n\
                 #                                   画像のURLが正しいかご確認してください。')

                #else:
                res = await self.Bing_instance.compose_stream(text, tone='professional', format='ideas', length='medium')
                await self.send_split_message(message, res)


        # 返信もらった時
        @bot.event
        async def on_raw_reaction_add(message):
            if message.author != bot.user:
                text = message.content.lstrip('+')
                res  = await self.Bing_instance.compose(text)
                await self.send_split_message(message, res)

        bot.run(dis_TOKEN)

if __name__ == '__main__':
    instance = Bing_BOT()
    instance.discord_api()
