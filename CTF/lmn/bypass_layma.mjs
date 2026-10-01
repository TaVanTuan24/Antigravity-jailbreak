import fs from 'fs';
import crypto from 'crypto';
import { scrypt } from './scrypt.js';

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
const enc = new TextEncoder();

function leadingZeroBits(bytes) {
  let bits = 0;
  for (const b of bytes) {
    if (b === 0) { bits += 8; continue; }
    bits += Math.clz32(b) - 24;
    break;
  }
  return bits;
}

async function solvePow(pow) {
  if (!pow || !pow.bits) return '0';
  const saltBytes = enc.encode(String(pow.salt));
  for (let i = 0; i < 8192; i++) {
    const out = await scrypt(saltBytes, enc.encode(String(i)), { N: pow.N || 256, r: pow.r || 8, p: 1, dkLen: 32 });
    if (leadingZeroBits(out) >= pow.bits) {
      return String(i);
    }
  }
  return '0';
}

function countBeepsFromWavBuffer(wavBuf, countType = 'high') {
  let pos = 12;
  let framerate = 16000;
  while (pos < wavBuf.length) {
    const chunkId = wavBuf.toString('ascii', pos, pos + 4);
    const chunkSize = wavBuf.readUInt32LE(pos + 4);
    if (chunkId === 'fmt ') {
      framerate = wavBuf.readUInt32LE(pos + 12);
    }
    if (chunkId === 'data') {
      pos += 8;
      break;
    }
    pos += 8 + chunkSize;
  }

  const numSamples = Math.floor((wavBuf.length - pos) / 2);
  const samples = new Int16Array(numSamples);
  for (let i = 0; i < numSamples; i++) {
    samples[i] = wavBuf.readInt16LE(pos + i * 2);
  }

  const winSize = Math.floor(framerate * 0.02); // 20ms
  const hopSize = Math.floor(framerate * 0.01); // 10ms
  const activeRegions = [];
  let inRegion = false;
  let startT = 0;

  for (let i = 0; i <= samples.length - winSize; i += hopSize) {
    let sumSq = 0;
    for (let j = 0; j < winSize; j++) {
      const s = samples[i + j];
      sumSq += s * s;
    }
    const rms = Math.sqrt(sumSq / winSize);
    const t = i / framerate;
    if (rms > 1000) {
      if (!inRegion) {
        inRegion = true;
        startT = t;
      }
    } else {
      if (inRegion) {
        inRegion = false;
        activeRegions.push([startT, t]);
      }
    }
  }
  if (inRegion) {
    activeRegions.push([startT, samples.length / framerate]);
  }

  let highCount = 0;
  let lowCount = 0;
  for (const [st, et] of activeRegions) {
    const dur = et - st;
    if (dur < 0.12) continue; // skip click/glitch
    const startIdx = Math.floor(st * framerate);
    const endIdx = Math.floor(et * framerate);
    let zc = 0;
    for (let i = startIdx + 1; i < endIdx; i++) {
      if ((samples[i - 1] >= 0 && samples[i] < 0) || (samples[i - 1] < 0 && samples[i] >= 0)) {
        zc++;
      }
    }
    const freq = (zc / 2) / dur;
    if (freq > 800) {
      highCount++;
    } else {
      lowCount++;
    }
  }

  return countType === 'low' ? lowCount : highCount;
}

async function solveQCaptcha(sitekey, host, action = null) {
  console.log(`[QCaptcha] Solving for sitekey=${sitekey}, host=${host}${action ? `, action=${action}` : ''}...`);
  const initRes = await fetch('https://frame.103-141-140-153.sslip.io/v1/init', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'User-Agent': UA,
      'Origin': 'https://frame.103-141-140-153.sslip.io',
      'Referer': 'https://frame.103-141-140-153.sslip.io/frame.html'
    },
    body: JSON.stringify({ sitekey, host, ...(action ? { action } : {}) })
  });
  const init = await initRes.json();
  if (init.error) throw new Error('Init error: ' + JSON.stringify(init));

  const accRes = await fetch('https://frame.103-141-140-153.sslip.io/v1/accessible', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'User-Agent': UA,
      'Origin': 'https://frame.103-141-140-153.sslip.io',
      'Referer': 'https://frame.103-141-140-153.sslip.io/frame.html'
    },
    body: JSON.stringify({ sid: init.sid })
  });
  const acc = await accRes.json();
  if (acc.error) throw new Error('Accessible error: ' + JSON.stringify(acc));

  const qText = (acc.spec?.question?.en || acc.spec?.question?.vi || '').toLowerCase();
  const countType = (qText.includes('low') || qText.includes('thấp')) ? 'low' : 'high';

  const powNonce = await solvePow(acc.pow);
  const audioRes = await fetch('https://frame.103-141-140-153.sslip.io' + acc.audioUrl, {
    headers: { 'User-Agent': UA, 'Referer': 'https://frame.103-141-140-153.sslip.io/frame.html' }
  });
  const audioBuf = Buffer.from(await audioRes.arrayBuffer());
  const answer = countBeepsFromWavBuffer(audioBuf, countType);
  console.log(`[QCaptcha] Question type: count ${countType} beeps -> Answer: ${answer}`);

  const solveRes = await fetch('https://frame.103-141-140-153.sslip.io/v1/solve', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'User-Agent': UA,
      'Origin': 'https://frame.103-141-140-153.sslip.io',
      'Referer': 'https://frame.103-141-140-153.sslip.io/frame.html'
    },
    body: JSON.stringify({
      sid: init.sid,
      cid: acc.cid,
      answer: [answer],
      powNonce: powNonce,
      telemetry: {
        solveMs: 2200 + Math.floor(Math.random() * 800),
        mouseEvents: 6 + Math.floor(Math.random() * 5),
        keyboardNav: false
      }
    })
  });
  const res = await solveRes.json();
  if (!res.ok || !res.token) {
    throw new Error('Solve failed: ' + JSON.stringify(res));
  }
  console.log(`[QCaptcha] Token acquired successfully.`);
  return res.token;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function bypass(inputUrlOrToken) {
  let token = inputUrlOrToken;
  if (token.includes('/')) {
    token = token.split('/').pop().split('?')[0].split('#')[0];
  }
  console.log(`\n======================================================`);
  console.log(`[*] Target short link: https://layma.net/${token}`);
  console.log(`======================================================`);

  const uuid = crypto.randomUUID();

  // Step 1: Layma Visitor Session with retry
  console.log('\n[1/6] Initializing visitor session on layma.net...');
  let laymaSessionToken = null;
  for (let retry = 0; retry < 3; retry++) {
    try {
      const visitorRes = await fetch('https://api.layma.net/api/traffic/visitor', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'User-Agent': UA,
          'Origin': 'https://layma.net',
          'Referer': `https://layma.net/${token}`
        },
        body: JSON.stringify({
          uuid: uuid,
          browser: 'Chrome',
          browserVersion: '120.0.0.0',
          browserMajorVersion: 120,
          cookies: true,
          mobile: false,
          os: 'Windows',
          osVersion: '10',
          screen: '1920 x 1080',
          userAgent: UA,
          token: token
        })
      });
      const vText = await visitorRes.text();
      const visitorData = JSON.parse(vText);
      laymaSessionToken = visitorData.sessionToken || visitorData.SessionToken;
      if (laymaSessionToken) break;
    } catch (e) {
      console.log(`[!] Visitor init retry ${retry + 1}/3...`);
      await sleep(1000);
    }
  }

  if (!laymaSessionToken) {
    throw new Error('Failed to acquire visitor session token from layma.net');
  }
  console.log('[+] Layma visitor session token:', laymaSessionToken);

  // Step 2-5: Get target domain, locate widget, match campaign, wait, and get code
  let chosenSolution = '0';
  let chosenFlatform = 'google';
  let targetDomain = null;
  let keyToken = null;
  let targetSitekey = 'd0c97bcc-d88c-42d1-8a0c-1180bf53e2a1';
  let widgetSessionToken = null;
  let code = null;
  let trafficId = null;

  for (let attempt = 0; attempt < 5; attempt++) {
    let camp = null;
    console.log(`\n[2/6] Querying target host domain (attempt ${attempt + 1}/5)...`);
    const urlCopyRes = await fetch(`https://layma.net/${token}/url-copy`, {
      method: 'POST',
      headers: {
        'User-Agent': UA,
        'X-Traffic-Session': laymaSessionToken,
        'Referer': `https://layma.net/${token}`
      }
    });
    targetDomain = (await urlCopyRes.text()).trim();
    console.log('[+] Target host domain:', targetDomain);

    // Step 3: Scrape target website for keyToken
    console.log(`\n[3/6] Fetching target site (https://${targetDomain}/) to locate traffic widget...`);
    try {
      const targetSiteRes = await fetch(`https://${targetDomain}/`, {
        headers: { 'User-Agent': UA }
      });
      const targetSiteHtml = await targetSiteRes.text();
      const keyTokenMatch = targetSiteHtml.match(/https:\/\/layma\.net\/Traffic\/Index\/([a-zA-Z0-9_\-]+)/i)
        || targetSiteHtml.match(/\/Traffic\/Index\/([a-zA-Z0-9_\-]+)/i)
        || targetSiteHtml.match(/Traffic\/Index\/([a-zA-Z0-9_\-]+)/i);
      keyToken = keyTokenMatch ? keyTokenMatch[1] : null;

      if (!keyToken) {
        console.log('[!] Warning: Could not auto-detect keyToken from HTML, searching for fallback pattern...');
        const genericToken = targetSiteHtml.match(/(?:keyToken|token)["']?\s*[:=]\s*["']([a-zA-Z0-9_\-]+)["']/i);
        if (genericToken) keyToken = genericToken[1];
      }
      console.log('[+] Target keyToken:', keyToken);

      if (keyToken) {
        try {
          const trafficJsRes = await fetch(`https://layma.net/Traffic/Index/${keyToken}`, {
            headers: { 'User-Agent': UA }
          });
          const trafficJs = await trafficJsRes.text();
          const guidMatch = trafficJs.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
          if (guidMatch) {
            targetSitekey = guidMatch[0];
          }
        } catch (e) {
          console.log('[!] Error fetching traffic script, using default sitekey:', e.message);
        }
      }
      console.log('[+] Target QCaptcha sitekey:', targetSitekey);

      if (!keyToken) {
        throw new Error('Could not find keyToken on target site');
      }

      // Step 4: Traffic session and campaign matching
      console.log('\n[4/6] Initializing campaign session on target site...');
      const sessRes = await fetch('https://api.layma.net/api/traffic/session', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'User-Agent': UA,
          'Origin': `https://${targetDomain}`,
          'Referer': `https://www.google.com/`
        },
        body: JSON.stringify({ keyToken })
      });
      const sessData = await sessRes.json();
      widgetSessionToken = sessData.sessionToken || sessData.SessionToken;

      const candidateFlatforms = ['tructiep', 'google', 'facebook'];
      const candidateSolutions = [
        { waitMode: 1, requiredPageVisits: 1, solution: '0' },
        { waitMode: 2, requiredPageVisits: 2, solution: '1' },
        { waitMode: 2, requiredPageVisits: 3, solution: '2' },
        { waitMode: 1, requiredPageVisits: 2, solution: '4' }
      ];

      for (const flatform of candidateFlatforms) {
        for (const sol of candidateSolutions) {
          const campUrl = `https://api.layma.net/api/admin/campain?keytoken=${keyToken}&flatform=${flatform}&waitMode=${sol.waitMode}&requiredPageVisits=${sol.requiredPageVisits}`;
          const campRes = await fetch(campUrl, {
            headers: {
              'User-Agent': UA,
              'X-Traffic-Session': widgetSessionToken,
              'Referer': flatform === 'google' ? 'https://www.google.com/' : `https://${targetDomain}/`
            }
          });
          if (campRes.ok) {
            const campText = await campRes.text();
            try {
              const parsed = JSON.parse(campText);
              if (parsed && parsed.id) {
                camp = parsed;
                chosenSolution = sol.solution;
                chosenFlatform = flatform;
                console.log(`[+] Found active campaign: flatform=${flatform}, waitMode=${sol.waitMode}, visits=${sol.requiredPageVisits}, solution=${sol.solution}`);
                break;
              }
            } catch (e) {}
          }
        }
        if (camp) break;
      }
    } catch (err) {
      console.log('[!] Error during campaign check:', err.message);
    }

    if (!camp || !camp.id) {
      console.log('[!] No active campaign found on target domain, requesting mission change...');
      try {
        await fetch('https://api.layma.net/api/traffic/mission/change', {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            'User-Agent': UA,
            'X-Traffic-Session': laymaSessionToken,
            'Referer': `https://layma.net/${token}`
          },
          body: JSON.stringify({ Token: token })
        });
        await sleep(2000);
      } catch (e) {
        console.log('[!] Mission change error:', e.message);
      }
      continue;
    }

    const currentTrafficId = camp.id;
    const trafficSessionToken = camp.trafficSessionToken;
    let visitTicket = camp.visitTicket;
    const waitSeconds = camp.requiredWaitSeconds || 60;
    console.log(`[+] Campaign ID: ${currentTrafficId}`);
    console.log(`[+] Countdown required: ${waitSeconds} seconds`);

    // Visit ping
    const visitReferrer = chosenFlatform === 'google' ? 'https://www.google.com/' : `https://${targetDomain}/`;
    const visitRes = await fetch('https://api.layma.net/api/traffic/visit', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'User-Agent': UA,
        'X-Traffic-Session': widgetSessionToken,
        'Referer': visitReferrer
      },
      body: JSON.stringify({
        trafficSessionToken: trafficSessionToken,
        visitTicket: visitTicket,
        trafficId: currentTrafficId
      })
    });
    const visitData = await visitRes.json();
    if (visitData.visitTicket) visitTicket = visitData.visitTicket;

    const waitTime = waitSeconds + 5;
    console.log(`[*] Waiting for server countdown (${waitTime}s)...`);
    for (let s = waitTime; s > 0; s -= 10) {
      console.log(`    ${s}s remaining...`);
      await sleep(Math.min(s, 10) * 1000);
    }
    await sleep(1000);

    // Step 5: Solve QCaptcha for target site and get code
    console.log('\n[5/6] Solving QCaptcha on target domain to retrieve verification code...');

    // 5a. Fetch fresh captcha nonce/action with polling
    let captchaAction = null;
    for (let ret = 0; ret < 10; ret++) {
      try {
        const nonceRes = await fetch('https://api.layma.net/api/traffic/captcha-nonce', {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            'User-Agent': UA,
            'Origin': `https://${targetDomain}`,
            'Referer': visitReferrer,
            'X-Traffic-Session': widgetSessionToken
          },
          body: JSON.stringify({
            trafficSessionToken: trafficSessionToken,
            trafficId: currentTrafficId
          })
        });
        const rawText = await nonceRes.text();
        try {
          const nonceData = JSON.parse(rawText);
          if (nonceData && nonceData.action) {
            captchaAction = nonceData.action;
            console.log('[+] Acquired captcha action nonce:', captchaAction);
            break;
          }
        } catch (parseErr) {
          console.log(`[*] Nonce status ${nonceRes.status} (${rawText.trim()}), waiting 3s before retry...`);
        }
      } catch (e) {
        console.log('[!] Warning: fetch error on captcha-nonce:', e.message);
      }
      await sleep(3000);
    }

    if (!captchaAction && camp.captchaNonceAction) {
      console.log('[!] Using campaign initial captchaNonceAction as fallback');
      captchaAction = camp.captchaNonceAction;
    }

    const targetQCaptchaToken = await solveQCaptcha(targetSitekey, `https://${targetDomain}`, captchaAction);

    // 5b. Submit getcode
    const bodyReferrer = chosenFlatform === 'google'
      ? 'https://www.google.com/'
      : (chosenFlatform === 'facebook' ? 'https://fbclid.facebook.com' : '');

    let getCodeData = null;
    const solutionsToTry = [String(chosenSolution), '0', '1'].filter((v, i, a) => a.indexOf(v) === i);

    for (const sol of solutionsToTry) {
      console.log(`[*] Submitting getcode with solution="${sol}"...`);
      const getCodeRes = await fetch('https://api.layma.net/api/traffic/getcode', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'User-Agent': UA,
          'Origin': `https://${targetDomain}`,
          'Referer': `https://${targetDomain}/`,
          'X-Traffic-Session': widgetSessionToken
        },
        body: JSON.stringify({
          uuid: uuid,
          browser: 'Chrome',
          browserVersion: '120.0.0.0',
          browserMajorVersion: 120,
          cookies: true,
          mobile: false,
          os: 'Windows',
          osVersion: '10',
          screen: '1920 x 1080',
          referrer: bodyReferrer,
          trafficId: currentTrafficId,
          trafficSessionToken: trafficSessionToken,
          solution: sol,
          qCaptchaToken: targetQCaptchaToken
        })
      });

      const rawText = await getCodeRes.text();
      try {
        const parsed = JSON.parse(rawText);
        if (parsed && parsed.success && parsed.html) {
          getCodeData = parsed;
          break;
        } else {
          console.log(`[!] GetCode (sol ${sol}) returned:`, rawText);
        }
      } catch (e) {
        console.log(`[!] GetCode (sol ${sol}) parse error: ${rawText}`);
      }
    }

    if (getCodeData && getCodeData.success && getCodeData.html) {
      code = getCodeData.html.trim();
      trafficId = currentTrafficId;
      break;
    }

    console.log('[!] Failed to obtain verification code on this domain, requesting mission change...');
    try {
      await fetch('https://api.layma.net/api/traffic/mission/change', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'User-Agent': UA,
          'X-Traffic-Session': laymaSessionToken,
          'Referer': `https://layma.net/${token}`
        },
        body: JSON.stringify({ Token: token })
      });
      await sleep(2000);
    } catch (e) {
      console.log('[!] Mission change error:', e.message);
    }
  }

  if (!code) {
    throw new Error('Failed to retrieve verification code after all attempts');
  }

  console.log(`\n======================================================`);
  console.log(`[★] RETRIEVED VERIFICATION CODE: ${code}`);
  console.log(`======================================================\n`);

  // Step 6: Solve QCaptcha for layma.net and checkcode
  console.log('[6/6] Solving QCaptcha on layma.net and submitting verification code...');
  const laymaSitekey = 'facd4b6c-53e6-44a2-9b27-b01844a6bd75';
  const laymaQCaptchaToken = await solveQCaptcha(laymaSitekey, 'https://layma.net');

  const checkRes = await fetch('https://api.layma.net/api/traffic/checkcode', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'User-Agent': UA,
      'X-Traffic-Session': laymaSessionToken,
      'Origin': 'https://layma.net',
      'Referer': `https://layma.net/${token}`
    },
    body: JSON.stringify({
      Code: code,
      Token: token,
      CampainId: trafficId,
      UserAgent: UA,
      DeviceScreen: '1920 x 1080',
      FingerprintData: JSON.stringify({
        version: "v1",
        uuid: uuid,
        language: 'vi-VN',
        platform: 'Win32',
        browser: 'Chrome',
        browserVersion: '120.0.0.0',
        screen: '1920 x 1080',
        colorDepth: 24,
        pixelRatio: 1,
        battery: null,
        orientation: { supported: false },
        createdAt: new Date().toISOString()
      }),
      HCaptchaToken: '',
      QCaptchaToken: laymaQCaptchaToken
    })
  });
  const checkData = await checkRes.json();
  console.log('[+] CheckCode response:', checkData);
  const redirectUrl = typeof checkData === 'string' ? checkData : (checkData.redirectUrl || checkData.RedirectUrl);

  if (!redirectUrl) {
    throw new Error('Checkcode failed: ' + JSON.stringify(checkData));
  }

  const finalCheckUrl = redirectUrl.startsWith('http') ? redirectUrl : `https://layma.net${redirectUrl}`;
  console.log(`\nFollowing redirect: ${finalCheckUrl}`);
  const finalResp = await fetch(finalCheckUrl, {
    headers: {
      'User-Agent': UA,
      'Referer': `https://layma.net/${token}`
    },
    redirect: 'manual'
  });
  const destLocation = finalResp.headers.get('location');
  const finalResult = destLocation || redirectUrl;

  console.log(`\n======================================================`);
  console.log(`[✔] FINAL DESTINATION URL: ${finalResult}`);
  console.log(`======================================================\n`);

  return finalResult;
}

const input = process.argv[2] || 'eVO6eQDdl';
bypass(input).catch(err => {
  console.error('[!] Error executing bypass:', err);
  process.exit(1);
});
