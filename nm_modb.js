/*
 * cron: 16 11 * * *
 */
const Env = require('./env');
const axios = require('axios');
const notify = require('./notify');

const $ = new Env('墨天轮每日签到');
const COOKIE_NAME = 'NM_MODB_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function postCheckIn () {
  const formData = new FormData();
  return await axios.post('https://www.modb.pro/api/user/checkIn', formData, config).then((response) => {
    const body = response.data;
    if (body.success === 'true') {
      $.log('✅ 签到成功');
      $.log(`🚧 ${body.operateMessage}`);
    } else {
      $.log(`🚧 ${body.operateMessage}`);
    }
    return true;
  }).catch((err) => {
    if (err.response.status === 401 || err.response.data?.success === 'false') {
      $.log('❌ 签到失败，当前 Cookie 已失效。');
    } else {
      $.log('❌ 签到失败，未知错误。');
    }
    return false;
  })
}

async function getUserProfile () {
  return await axios.get('https://www.modb.pro/api/user/dailyTask', config).then(async (response) => {
    return response.data;
  })
}

!(async () => {
  if (!process.env[COOKIE_NAME]) {
    $.log(`❌ 未设置环境变量 [${COOKIE_NAME}]`);
    return;
  }

  const result = await postCheckIn();
  if (!result) {
    return;
  }

  const user = await getUserProfile();

  const text = `👨 我的积分
🥇 连续签到：${user.day} 天
🏆 累计签到：${user.totalDays} 天
🪙 墨值数量：${user.point} 墨值`;
  $.log(text);
  await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});