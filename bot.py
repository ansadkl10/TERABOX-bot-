const { Telegraf } = require('telegraf');
const axios = require('axios');
const fs = require('fs-extra');
const express = require('express');
const path = require('path');

// Environment Variables
const BOT_TOKEN = process.env.BOT_TOKEN;
const KOYEB_API_URL = process.env.API_URL || "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass";

const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Health check for Render
app.get('/', (req, res) => res.send('Bot is Alive!'));
app.listen(process.env.PORT || 8080);

bot.start((ctx) => ctx.reply('Hello! Terabox link ayakkuka, njan bypass cheythu tharaam.'));

bot.on('text', async (ctx) => {
    const url = ctx.message.text;
    if (!url.includes('terabox') && !url.includes('1024tera')) return;

    const statusMsg = await ctx.reply('🔍 Processing... please wait.');

    try {
        const response = await axios.get(`${KOYEB_API_URL}?url=${url}`);
        const data = response.data;

        if (data.status) {
            const fileInfo = data.result.list[0];
            const fileName = fileInfo.server_filename;
            const directLink = fileInfo.direct_link;
            const sizeInBytes = fileInfo.size;
            const fileSizeMB = (sizeInBytes / (1024 * 1024)).toFixed(2);

            // 400 MB-yil kooduthal aanel Link ayakkum
            if (fileSizeMB > 400) {
                await ctx.telegram.editMessageText(ctx.chat.id, statusMsg.message_id, null, 
                    `⚠️ **File is too large for Telegram!**\n\n` +
                    `📁 **Name:** \`${fileName}\` \n` +
                    `📊 **Size:** ${fileSizeMB} MB\n\n` +
                    `🔗 [Download Direct Link](${directLink})`,
                    { parse_mode: 'Markdown' }
                );
            } 
            // 400 MB-yil thaye aanel File ayakkum
            else {
                await ctx.telegram.editMessageText(ctx.chat.id, statusMsg.message_id, null, `📥 Downloading: ${fileName} (${fileSizeMB} MB)`);

                const filePath = path.join(__dirname, fileName);
                const writer = fs.createWriteStream(filePath);

                const fileStream = await axios({
                    method: 'get',
                    url: directLink,
                    responseType: 'stream'
                });

                fileStream.data.pipe(writer);

                writer.on('finish', async () => {
                    await ctx.telegram.editMessageText(ctx.chat.id, statusMsg.message_id, null, `📤 Uploading to Telegram...`);
                    try {
                        await ctx.replyWithDocument({ source: filePath, filename: fileName }, {
                            caption: `✅ **File:** \`${fileName}\` \n📊 **Size:** ${fileSizeMB} MB`,
                            parse_mode: 'Markdown'
                        });
                        // File delete cheyyunnu
                        await fs.remove(filePath);
                        await ctx.telegram.deleteMessage(ctx.chat.id, statusMsg.message_id);
                    } catch (err) {
                        ctx.reply(`❌ Upload failed. Direct Link: ${directLink}`);
                        await fs.remove(filePath);
                    }
                });

                writer.on('error', async (err) => {
                    ctx.reply(`❌ Download Error: ${err.message}`);
                    await fs.remove(filePath);
                });
            }
        } else {
            ctx.reply('❌ Link bypass cheyyan pattiyilla.');
        }
    } catch (error) {
        ctx.reply(`❌ System Error: ${error.message}`);
    }
});

bot.launch();
console.log("Bot started successfully!");
