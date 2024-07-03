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
    cookie: 'mfw_uuid=668275e2-fa47-a189-959f-b610d8075183; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222024-07-01+17%3A24%3A50%22%3B%7D; __mfwc=direct; uva=s%3A92%3A%22a%3A3%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1719825894%3Bs%3A10%3A%22last_refer%22%3Bs%3A24%3A%22https%3A%2F%2Fwww.mafengwo.cn%2F%22%3Bs%3A5%3A%22rhost%22%3BN%3B%7D%22%3B; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1719825894%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=668275e2-fa47-a189-959f-b610d8075183; __jsluid_s=166a37e5fc0df0bf2b0e999ed2980de0; login=mafengwo; mafengwo=1799a383f6b607c3818d3b96d2dd8bab_19555304_668275fd7e3ad9.14547138_668275fd7e3b10.26215296; PHPSESSID=dj40mum93ss49itt20965537j2; uol_throttle=19555304; mfw_uid=19555304; __mfwa=1719825894453.46067.2.1719825894453.1719983143856; __mfwlv=1719983143; __mfwvn=2; __omc_chl=; __omc_r=; isCookie=1; isDownClick_adis_baidu=1; wakeApp_unshow_baidu=1; __mfwb=324485e5e6ed.3.direct; __mfwlt=1719983225'
    // cookie: process.env[COOKIE_NAME]
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
  // if (!process.env[COOKIE_NAME]) {
  //   $.log(`未设置环境变量 [${COOKIE_NAME}]`);
  //   return;
  // }

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