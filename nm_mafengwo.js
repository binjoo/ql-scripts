/*
 * cron: 16 9 * * *
 */
const Env = require('./env');
const axios = require('axios');
const cheerio = require('cheerio');
const notify = require('./notify');

const $ = new Env('马蜂窝签到');
const COOKIE_NAME = 'NM_MAFENGWO_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function postDaka () {
  const formData = new FormData();
  formData.append('act', 'doDaka');
  return await axios.post('https://m.mafengwo.cn/sales/activity/ajax.php', formData, config).then((response) => {
    const body = response.data;
    if(body.data){
      $.log(`✔️打卡成功`);
      return body.data;
    }else if(body.error){
      $.log(`🚧${body.error.msg}`);
      return false;
    }
  }).catch((err) => {
    if (err.response.status === 400 || err.response.data === 0) {
      $.log('❌签到失败，当前 Cookie 可能已失效。');
    }
    return false;
  })
}

!(async () => {
  if (!process.env[COOKIE_NAME]) {
    $.log(`未设置环境变量 [${COOKIE_NAME}]`);
    return;
  }

  const result = await postDaka();
  if (!result) {
    return;
  }

//   const text = `👨‍💻我的积分
// 🥇当前积分：${point.current}
// 🏆已用积分：${point.used}`;
//     $.log(text);
    // await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});