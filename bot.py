const { Telegraf } = require('telegraf');
const axios = require('axios');
const fs = require('fs-extra');
const express = require('express');
const path = require('path');

// ENV Variables
const BOT_TOKEN = process.env.BOT_TOKEN;
const KOYEB_API_URL = process.env.API_URL || "https://top-warbler-brofbdb699965-a3727b0a.koyeb.app/bypass";

const bot = new Telegraf(BOT_TOKEN);
const app = express();

// Render Health Check
app.get('/', (req, res) => res.send('Bot is Running!'));
app.listen(process.env.PORT || 8080);

bot.start((ctx) => ctx.reply('ഹലോ! Terabox ലിങ്ക് അയക്കൂ, ഞാൻ ഫയൽ നേരിട്ട് അയച്ചു തരാം.'));

bot.on('text', async (ctx) => {
    const url = ctx.message.text;
    if (!url.includes('terabox') && !url.includes('1024tera')) return;

    const statusMsg = await ctx.reply('🔍 പ്രോസസ്സ് ചെയ്യുന്നു...');

    try {
        // API Call
        const response = await axios.get(`${KOYEB_API_URL}?url=${url}`);
        const data = response.data;

        if (data.status) {
            const fileInfo = data.result.list[0];
            const fileName = fileInfo.server_filename;
            const directLink = fileInfo.direct_link;
            const fileSizeMB = (fileInfo.size / (1024 * 1024)).toFixed(2);

            await ctx.telegram.editMessageText(ctx.chat.id, statusMsg.message_id, null, `📥 ഡൗൺലോഡ് ചെയ്യുന്നു: ${fileName} (${fileSizeMB} MB)`);

            const filePath = path.join(__dirname, fileName);

            // File Downloading
            const writer = fs.createWriteStream(filePath);
            const fileStream = await axios({
                method: 'get',
                url: directLink,
                responseType: 'stream'
            });

            fileStream.data.pipe(writer);

            writer.on('finish', async () => {
                await ctx.telegram.editMessageText(ctx.chat.id, statusMsg.message_id, null, `📤 ടെലഗ്രാമിലേക്ക് അപ്‌ലോഡ് ചെയ്യുന്നു...`);
                
                try {
                    await ctx.replyWithDocument({ source: filePath, filename: fileName }, {
                        caption: `✅ **File:** \`${fileName}\` \n📊 **Size:** ${fileSizeMB} MB`,
                        parse_mode: 'Markdown'
                    });
                    // Cleanup
                    await fs.remove(filePath);
                    await ctx.telegram.deleteMessage(ctx.chat.id, statusMsg.message_id);
                } catch (uploadError) {
                    ctx.reply(`അപ്‌ലോഡ് പരാജയപ്പെട്ടു: ${uploadError.message}`);
                    await fs.remove(filePath);
                }
            });

            writer.on('error', (err) => {
                ctx.reply(`ഡൗൺലോഡ് എറർ: ${err.message}`);
                fs.remove(filePath);
            });

        } else {
            ctx.reply('ക്ഷമിക്കണം, ലിങ്ക് ബൈപാസ് ചെയ്യാൻ കഴിഞ്ഞില്ല.');
        }
    } catch (error) {
        ctx.reply(`എറർ: ${error.message}`);
    }
});

bot.launch();
console.log("Bot Started...");
