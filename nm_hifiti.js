/*
 * cron: 15 14 * * *
 */
const Env = require('./env');
const axios = require('axios');
const cheerio = require('cheerio');
const notify = require('./notify');

const $ = new Env('HiFiTi签到');
const COOKIE_NAME = 'NM_HIFITI_COOKIE';

const config = {
  headers: {
    cookie: process.env[COOKIE_NAME]
  }
}

async function getSignToken () {
  return await axios.get('https://www.hifiti.com', config).then((response) => {
    const root = cheerio.load(response.data);
    const cookie = true;
    if (root('header.navbar ul.navbar-nav li').last('a').text().trim() === '登录') {
      $.log('❌当前未登录...');
      cookie = false;
    } else {
      $.log('✔️当前已登录...');
    }
    const regex = /var\s+sign\s*=\s*"([^"]+)";/;
    const match = response.data.match(regex);

    if (match) {
      return {
        cookie: cookie,
        sign: match[1]
      }
    } else {
      return {
        cookie: cookie,
        sign: undefined
      }
    }
  })
}

async function postSgSign (sign) {
  const formData = new FormData();
  formData.append('sign', sign);
  return await axios.post('https://www.hifiti.com/sg_sign.htm', formData, config).then((response) => {
    const root = cheerio.load(response.data);
    $.log('📢' + root('div.container h4.card-title.text-center').text().trim());
  })
}

async function getMyCredits () {
  return await axios.get('https://hifiti.com/my-credits.htm', config).then(async (response) => {
    const root = cheerio.load(response.data);
    const val = root('div.card div.card-body input[type=text]:eq(1)').attr('value');
    return {
      total: val
    }
  })
}

async function getSignDetail () {
  return await axios.get('https://www.hifiti.com/sg_sign.htm', config).then(async (response) => {
    const root = cheerio.load(response.data);
    /**
     * 0 今日签到排名
     * 1 用户名
     * 2 总奖励
     * 3 今日奖励
     * 5 签到天数
     * 6 连续签到天数
     */
    const td = root('div.card table.table tr:last-child td');
    return {
      rank: td.eq(0).text(),
      username: td.eq(1).text(),
      totalGold: td.eq(2).text(),
      dailyGold: td.eq(3).text(),
      checkInDays: td.eq(5).text(),
      consecutiveDays: td.eq(6).text()
    }
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

  const detail = await getMyCredits();

  const text = `👛总金币：${detail.total}`;

  //   const detail = await getSignDetail();

  //   const text = `👨‍💻${detail.username} 签到明细
  // 🥇今日签到排名：${detail.rank}
  // 🏆今日签到金币：${detail.dailyGold}
  // 👛总金币：${detail.totalGold}
  // 📆连续签到天数：${detail.consecutiveDays}
  // 📅签到总天数：${detail.checkInDays}`;
  $.log(text);
  await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});