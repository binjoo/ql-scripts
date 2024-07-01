/*
 * cron: 15 7 * * *
 * 巴拉巴拉
 * 
 * TEST 
 */
const Env = require('./env');
const notify = require('./notify');

const $ = new Env('测试');

!(async () => {
  await notify.telegram($.name, text);
})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});