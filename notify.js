async function telegram (title, content) {
  return new Promise((resolve, reject) => {
    const TG_BOT_TOKEN = process.env.TG_BOT_TOKEN;
    const TG_USER_ID = process.env.TG_USER_ID;
    const TG_PROXY_URL = process.env.TG_PROXY_URL || 'https://api.telegram.org';
    if (!TG_BOT_TOKEN || !TG_USER_ID) {
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
    axios.post(`${TG_PROXY_URL}/bot${TG_BOT_TOKEN}/sendMessage`, data).then((response) => {
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