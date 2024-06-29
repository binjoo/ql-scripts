/*
 * cron: 15 7 * * *
 * 巴拉巴拉
 * 
 * TEST 
 */

const $ = new Env('测试');

!(async () => {
  // 代码开始
  if (!process.env['TEST']) {
    $.log('444444');
    $.logErr('aaaaa');
    return;
  }

  $.log($.name);

  // 常用代码
  const env = JSON.parse(process.env.TEST); // 读取环境变量
  const data = $.getdata($.name) || {}; // 读取配置
  $.setdata(data, $.name); // 保存配置

})().catch((e) => {
  $.logErr(e);
}).finally(() => {
  $.done();
});