// ego-browser 에서 실행: 운영자 마스터 접속으로 열린 /cms 탭을 전송층으로 써서 사진을 올린다(고객 비밀번호를 쓰지 않는다)
//   ego-browser nodejs -e "await import('file:///D:/work/외주/소로롱/초안/tools/cms_load_ego.mjs')"
// 다시 돌려도 같은 결과: 올린 사진은 cms_media_map.json 에 적어 두고 건너뛴다. 쓰기 예산(세션당 10분 120회)은 스스로 맞춘다.
import { createHash } from 'node:crypto'
import { existsSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const ROOT = 'D:/work/외주/소로롱/초안'
const HERE = ROOT + '/tools'
const MAP_FILE = HERE + '/cms_media_map.json'
const CUSTOMER_OPS = 'https://tengtengsoft.kr/admin/cms-ops/customers/0a7d6d8d-e2fd-4e07-b5ea-24e994c5dabd'
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const task = await taskSpace('sororong cms load')
const pages = await task.pages()
const page = pages.length ? task.page(pages[0].label) : await task.newPage()
await page.cdp('egoAutomated.disable').catch(() => {})

async function openMaster() {
  log('마스터 접속 열기')
  await page.goto(CUSTOMER_OPS)
  await page.waitForTimeout(3000)
  const popup = page.waitForEvent('popup', { timeout: 15000 }).catch(() => null)
  await page.click('text=관리자 페이지 열기', { label: 'open sororong admin' })
  const pp = await popup
  if (pp) await pp.close().catch(() => {})
  await page.goto('https://tengtengsoft.kr/cms')
  await page.waitForTimeout(2500)
  writes.length = 0
}

const writes = []
async function slot(n = 1) {
  for (;;) {
    const now = Date.now()
    while (writes.length && now - writes[0] > 600_000) writes.shift()
    if (writes.length + n <= 105) { for (let i = 0; i < n; i++) writes.push(now); return }
    const wait = 600_000 - (now - writes[0]) + 1000
    log(`쓰기 예산 대기 ${Math.round(wait / 1000)}초`)
    await sleep(wait)
  }
}

async function raw(method, path, body) {
  return page.evaluate(async ([m, p, b]) => {
    const res = await fetch(p, { method: m, credentials: 'same-origin', headers: { accept: 'application/json', ...(b !== null ? { 'content-type': 'application/json' } : {}) }, body: b, cache: 'no-store' })
    const text = await res.text()
    let data = null
    try { data = text ? JSON.parse(text) : null } catch { data = { text: text.slice(0, 200) } }
    return { status: res.status, data }
  }, [method, path, body === undefined ? null : typeof body === 'string' ? body : JSON.stringify(body)])
}
async function api(method, path, body, reserved = false) {
  if (method !== 'GET' && !reserved) await slot()
  for (let attempt = 0; attempt < 4; attempt++) {
    const r = await raw(method, path, body)
    if (r.status === 401 || r.status === 403) { await openMaster(); await assertSpace(); continue }
    if (r.status === 429) { log('429 대기 60초'); await sleep(60_000); continue }
    if (r.status >= 500) { log(`${r.status} 재시도`); await sleep(5000); continue }
    if (r.status >= 400) throw new Error(`${method} ${path} → ${r.status} ${JSON.stringify(r.data).slice(0, 400)}`)
    return r.data
  }
  throw new Error(`${method} ${path} 재시도 끝`)
}
async function assertSpace() {
  const r = await raw('GET', '/api/cms/site-content')
  if (r.status !== 200 || !/소로롱/.test(r.data?.package?.name ?? '')) throw new Error(`소로롱 공간이 아닙니다: ${r.status} ${r.data?.package?.name}`)
}

const mediaMap = existsSync(MAP_FILE) ? JSON.parse(await readFile(MAP_FILE, 'utf8')) : {}
const saveMap = () => writeFile(MAP_FILE, JSON.stringify(mediaMap, null, 1))
let done = 0
async function upload(rel) {
  if (mediaMap[rel]) return mediaMap[rel]
  const buf = await readFile(resolve(ROOT, rel))
  const sha256 = createHash('sha256').update(buf).digest('hex')
  await slot(3)
  const intent = await api('POST', '/api/cms/media', { mime: 'image/jpeg', bytes: buf.length, sha256 }, true)
  if (intent.status !== 'verified' && intent.status !== 'committed') {
    if (!intent.objectExists) {
      if (!intent.signedUrl) throw new Error(`업로드 주소 없음: ${rel}`)
      const put = await fetch(intent.signedUrl, { method: 'PUT', headers: { 'content-type': 'image/jpeg' }, body: buf })
      if (!put.ok) throw new Error(`PUT ${rel} → ${put.status}`)
    }
    await api('POST', `/api/cms/media/${intent.mediaId}`, '{}', true)
  }
  try {
    await api('POST', `/api/cms/media/${intent.mediaId}/commit`, { documentId: null }, true)
  } catch (error) {
    if (!/→ 409 /.test(String(error.message))) throw error
  }
  mediaMap[rel] = intent.mediaId
  done += 1
  if (done % 10 === 0) { await saveMap(); log(`사진 ${done}장 · 누적 ${Object.keys(mediaMap).length}`) }
  return intent.mediaId
}

await openMaster()
await assertSpace()
log('소로롱 공간 확인')
const seed = JSON.parse(await readFile(HERE + '/cms_seed.json', 'utf8'))
const content = {}
for (const [key, value] of Object.entries(seed)) {
  if (Array.isArray(value)) {
    const rows = []
    for (const row of value) {
      const image = { mediaId: await upload(row.file), alt: (row.alt ?? row.title ?? '').slice(0, 200) }
      rows.push(row.title ? { image, title: row.title, desc: row.desc, kicker: row.kicker, cat: row.cat } : { image })
    }
    content[key] = rows
  } else {
    content[key] = { mediaId: await upload(value.file), alt: (value.alt ?? '').slice(0, 200) }
  }
}
await saveMap()
log('사진 끝 · 고유', Object.keys(mediaMap).length, '· 이번', done, '· 콘텐츠 바이트', Buffer.byteLength(JSON.stringify(content)))
await assertSpace()
const loaded = await api('GET', '/api/cms/site-content')
const theme = { ...loaded.theme, siteContent: { ...loaded.content, ...content } }
await api('PUT', '/api/cms/theme', { theme, themeRev: loaded.themeRev })
log('저장 끝')
const docs = await api('GET', '/api/cms/documents')
await api('POST', '/api/cms/site-content/publish', { baseTransitionNo: docs.baseTransitionNo })
log('공개 끝')
await task.finish({ keep: [] }).catch(() => {})
