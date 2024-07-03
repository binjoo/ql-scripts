/*
 * cron: 16 9 * * *
 */
const Env = require('./env');
const axios = require('axios');
const notify = require('./notify');

const $ = new Env('AcFun签到');
const COOKIE_NAME = 'NM_ACFUN_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function postSignIn () {
  return await axios.post('https://www.acfun.cn/rest/pc-direct/user/signIn', {}, config).then((response) => {
    const body = response.data;
    if (response.status === 200) {
      $.log(`✔️${body.msg}`);
      return body;
    } else if (response.status === 401) {
      $.log('❌签到失败，当前 Cookie 可能已失效。');
      return false;
    }
  }).catch((err) => {
    if (err.response.status === 400 || err.response.data === 0) {
      $.log('❌签到失败，当前 Cookie 可能已失效。');
    }
    return false;
  })
}

async function postPersonalInfo () {
  return await axios.post('https://www.acfun.cn/rest/pc-direct/user/personalInfo', {}, config).then((response) => {
    const body = response.data;
    return body.info;
  });
}

!(async () => {
  // if (!process.env[COOKIE_NAME]) {
  //   $.log(`未设置环境变量 [${COOKIE_NAME}]`);
  //   return;
  // }

  const result = await postSignIn();
  if (!result) {
    return;
  }
  const info = await postPersonalInfo();

  const text = `🥇签到结果：${result.msg}
🥇用户名：${info.userName}
🥇等级：LV ${info.level}
🍌香蕉数量：${info.banana}
🍌金香蕉数量：${info.goldBanana}`
  $.log(text);
  await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});