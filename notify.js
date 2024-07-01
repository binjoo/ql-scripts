async function telegram (title, content) {
  return new Promise((resolve, reject) => {
    const TG_BOT_TOKEN = process.env.TG_BOT_TOKEN;
    console.log('TG_BOT_TOKEN', TG_BOT_TOKEN)
    const TG_USER_ID = process.env.TG_USER_ID;
    console.log('TG_USER_ID', TG_USER_ID)
    const TG_API_HOST = process.env.TG_API_HOST || 'https://api.telegram.org';
    console.log('TG_API_HOST', TG_API_HOST)
    if (!TG_BOT_TOKEN || !TG_USER_ID) {
      console.log('!TG_BOT_TOKEN || !TG_USER_ID')
      resolve();
      return;
    }
    let text = '#' + title; // 前面加个'#', 方便搜索
    if (content) {
      text += `\n\n${content}`;
    }
    const data = {
      chat_id: TG_USER_ID,
      text: text
    }

    const axios = require('axios');
    axios.post(`${TG_API_HOST}/bot${TG_BOT_TOKEN}/sendMessage`, data).then((response) => {
      if (response.data.ok) {
        console.log('[Telegram] 🎉 发送通知消息成功🎉。');
      }
      resolve(response.data);
    }).catch((err) => {
      console.error(`[Telegram] 🥀 发送失败：`, err.message);
    });
  });
}

module.exports = {
  telegram
}