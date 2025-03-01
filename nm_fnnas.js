/*
 * cron: 20 14 * * *
 */
const Env = require('./env');
const axios = require('axios');
const cheerio = require('cheerio');
const notify = require('./notify');

const $ = new Env('飞牛NAS签到');
const COOKIE_NAME = 'NM_FNNAS_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function getSignToken () {
  return await axios.get('https://club.fnnas.com/', config).then((response) => {
    const root = cheerio.load(response.data);
    console.log(root('.pc-icon-wrap li.wrap-item:first-child a span').text().trim())
    const cookie = true;
    if (root('.pc-icon-wrap li.wrap-item:first-child a span').text().trim() === '登录') {
      $.log('❌当前未登录...');
      cookie = false;
    } else {
      $.log('✔️当前已登录...');
    }

    return {
      cookie: cookie,
      sign: root('input[name="formhash"]').attr('value')?.trim() || undefined
    }
  })
}

async function postSgSign (sign) {
  const formData = new FormData();
  formData.append('id', 'zqlj_sign');
  formData.append('sign', sign);
  return await axios.post('https://club.fnnas.com/plugin.php', formData, config).then((response) => {
    const root = cheerio.load(response.data);
    $.log('📢' + root('#messagetext p:first-child').text().trim());
  })
}

async function getSignDetail () {
  return await axios.get('https://club.fnnas.com/plugin.php?id=zqlj_sign', config).then(async (response) => {
    const root = cheerio.load(response.data);

    return root('div.bm:has(strong:contains("我的打卡动态")) ul.xl1 li').map((i, el) => {
      const raw = root(el).text().trim();
      const parts = raw.split(/[：:](.+)/);
      return parts[1] ? parts[1].trim() : '';
    }).get();
  })
}

!(async () => {
  if (!process.env[COOKIE_NAME]) {
    $.log(`未设置环境变量 [${COOKIE_NAME}]`);
    return;
  }

  const { cookie, sign } = await getSignToken();

  if (!cookie) {
    $.log(`Cookie已过期，请更新环境变量 ` + COOKIE_NAME);
    return;
  }

  await postSgSign(sign);

  const detail = await getSignDetail();

  const text = `👨‍💻 打卡动态
🥇打卡登记：${detail[6]}
🥇最近打卡：${detail[0]}
🥇本月打卡：${detail[1]}
🥇连续打卡：${detail[2]}
🥇累计打卡：${detail[3]}
🥇累计奖励：${detail[4]}
🥇最近奖励：${detail[5]}`;
  $.log(text);
  await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});