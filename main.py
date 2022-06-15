import asyncio
import requests
from pyppeteer import connect
import hmac, base64, struct, hashlib, time

async def openBrowser(url):
    response = requests.get(url).json()['data']['ws']['puppeteer']
    print(response)
    browser = await connect(browserWSEndpoint=response, ignoreHTTPSErrors=True, slowMo=1.5)
    page = list(await browser.pages())[0]

    [await p.close() for p in list(await browser.pages())[1:]]
    await page.setViewport({'width': 1920, 'height': 800})
    await asyncio.sleep(10)
    return page, browser


async def start(uid, login, password, twoFactor, option_value):
    url = f'http://local.adspower.com:50325/api/v1/browser/start?user_id={uid}'
    page, browser = await openBrowser(url)

    await mainProcess(page, login, password, twoFactor, option_value)
    await asyncio.sleep(100)
    urlStop = f'http://local.adspower.com:50325/api/v1/browser/stop?user_id={uid}'
    requests.get(urlStop)
    return await browser.close()

async def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


async def get_token(secret):
    return await get_hotp_token(secret, intervals_no=int(time.time()) // 30)


async def mainProcess(page, login, password, twoFactor, option_value):
    if await auth(page, login, password, twoFactor):
        if await page.JJ('a[href="/trade"]'):
            await page.goto('https://sales.coinlist.co/tribal#sale-options')
            await asyncio.sleep(10)

            element = await page.JJ('div[class="sale-options s-grid-colLg20"]')
            link = await element[option_value-1].J('a[class="c-button c-button--large cta-button register-buttons"]')
            link = await page.evaluate('link => link.getAttribute("href")', link)
            print(link)

            await page.goto(link)
            await asyncio.sleep(10)
            return True
        else:
            """ Error auth """
            return False
    else:
        """ Error auth """
        return False
async def auth(page, login, password, twoFactor):
    await page.goto('https://sales.coinlist.co/login')
    await asyncio.sleep(10)

    if await page.JJ('input[id="user_email"]'):
        await page.type('input[id="user_email"]', login)
        await page.type('input[id="user_password"]', password)
        await page.click('input[type="submit"]')
        await asyncio.sleep(10)

        if await page.JJ('input[id="multi_factor_authentication_totp_otp_attempt"]') and twoFactor:
            await page.type('input[id="multi_factor_authentication_totp_otp_attempt"]', str(await get_token(twoFactor)))
            await page.click('input[type="submit"]')
            await asyncio.sleep(10)
            return True

        else:
            return False

    return True


uid = 'i1rcogn'
login = 'gughsbelery@gmail.com'
password = 'pO$iKJUYBfd@'
twoFactor = 'xhycsj2bttjguf3dvfqw7sro'
option_value = 2
asyncio.run(start(uid, login, password, twoFactor, option_value))








