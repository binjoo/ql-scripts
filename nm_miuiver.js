/*
 * cron: 16 9 * * *
 */
const Env = require('./env');
const axios = require('axios');
const cheerio = require('cheerio');
const notify = require('./notify');

const $ = new Env('MIUI历史版本签到');
const COOKIE_NAME = 'NM_MIUIVER_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function postCheckIn () {
  const formData = new FormData();
  formData.append('action', 'epd_checkin');
  return await axios.post('https://miuiver.com/wp-admin/admin-ajax.php', formData, config).then((response) => {
    const body = response.data;
    if (body.status === 200) {
    } else if (body.status === 201) {
      $.log(`🚧${body.msg}`);
    }
    return true;
  }).catch((err) => {
    if (err.response.status === 400 || err.response.data === 0) {
      $.log('❌签到失败，当前 Cookie 可能已失效。');
    }
    return false;
  })
}

async function getUserProfile () {
  return await axios.get('https://miuiver.com/user-profile', config).then(async (response) => {
    const root = cheerio.load(response.data);
    const span = root('div.pagecontent.profile-content .row').eq(2).find('.profile-box p span');
    return {
      current: span.eq(0).find('b').text(),
      used: span.eq(1).find('b').text()
    }
  })
}

!(async () => {
  if (!process.env[COOKIE_NAME]) {
    $.log(`未设置环境变量 [${COOKIE_NAME}]`);
    return;
  }

  const result = await postCheckIn();
  if (!result) {
    return;
  }

  const point = await getUserProfile();

  const text = `👨‍💻我的积分
🥇当前积分：${point.current}
🏆已用积分：${point.used}`;
    $.log(text);
    await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});