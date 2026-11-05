// 소로롱 실제 사진 → 탱탱소프트 CMS (사이트 묶음 sororong 공간)
//
// 고객 관리자 화면과 같은 API 로 올린다(미디어 업로드 → 검증 → 연결 · 사이트 콘텐츠 저장 · 공개). DB 를 직접 만지지 않는다.
// 다시 돌려도 같은 결과: 올린 사진은 cms_media_map.json 에 적어 두고 건너뛴다(서버도 같은 sha256 이면 이미 있는 것으로 돌려준다).
//
// 사용 (비밀번호는 명령줄이 아니라 환경 변수로):
//   SORORONG_CMS_PW='…' node tools/cms_load.mjs --login <관리자 아이디> [--base https://tengtengsoft.kr] [--dry] [--no-publish]
//
// 입력: tools/cms_seed.json (build_cms_site.py 가 만든다) · assets/real/**

import { createHash } from 'node:crypto'
import { existsSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(HERE, '..')
const MAP_FILE = resolve(HERE, 'cms_media_map.json')

const args = process.argv.slice(2)
const arg = (name, fallback = null) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : fallback }
const BASE = (arg('base', 'https://tengtengsoft.kr') || '').replace(/\/$/, '')
const LOGIN = arg('login'), DRY = args.includes('--dry'), NO_PUBLISH = args.includes('--no-publish'), PASSWORD = process.env.SORORONG_CMS_PW || ''
if (!LOGIN && !DRY) { console.error("사용: SORORONG_CMS_PW='…' node tools/cms_load.mjs --login <아이디>"); process.exit(2) }

let cookie = ''
async function api(method, path, body, extra = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { accept: 'application/json', origin: BASE, referer: `${BASE}/cms`, ...(cookie ? { cookie } : {}), ...(body !== undefined ? { 'content-type': 'application/json' } : {}), ...extra },
    body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body),
    redirect: 'manual',
  })
  const setCookies = res.headers.getSetCookie?.() ?? []
  if (setCookies.length) {
    const jar = new Map(cookie.split('; ').filter(Boolean).map((c) => [c.split('=')[0], c]))
    for (const sc of setCookies) { const pair = sc.split(';')[0]; jar.set(pair.split('=')[0], pair) }
    cookie = [...jar.values()].join('; ')
  }
  const text = await res.text()
  let data = null
  try { data = text ? JSON.parse(text) : null } catch { data = { text: text.slice(0, 300) } }
  if (!res.ok) throw new Error(`${method} ${path} → ${res.status} ${JSON.stringify(data).slice(0, 400)}`)
  return data
}

const mediaMap = existsSync(MAP_FILE) ? JSON.parse(await readFile(MAP_FILE, 'utf8')) : {}
const saveMap = () => writeFile(MAP_FILE, JSON.stringify(mediaMap, null, 1))
let done = 0

async function upload(rel) {
  if (mediaMap[rel]) return mediaMap[rel]
  const buf = await readFile(resolve(ROOT, rel))
  const sha256 = createHash('sha256').update(buf).digest('hex')
  if (DRY) return (mediaMap[rel] = `dry-${sha256.slice(0, 8)}`)
  const intent = await api('POST', '/api/cms/media', { mime: 'image/jpeg', bytes: buf.length, sha256 })
  if (intent.status !== 'verified' && intent.status !== 'committed') {
    if (!intent.objectExists) {
      if (!intent.signedUrl) throw new Error(`업로드 주소 없음: ${rel}`)
      const put = await fetch(intent.signedUrl, { method: 'PUT', headers: { 'content-type': 'image/jpeg' }, body: buf })
      if (!put.ok) throw new Error(`PUT ${rel} → ${put.status} ${(await put.text()).slice(0, 200)}`)
    }
    await api('POST', `/api/cms/media/${intent.mediaId}`, '{}')
  }
  try {
    await api('POST', `/api/cms/media/${intent.mediaId}/commit`, { documentId: null })
  } catch (error) {
    // 409 = 이미 연결됨(이전 실행에서 commit 끝)
    if (!/→ 409 /.test(String(error.message))) throw error
  }
  mediaMap[rel] = intent.mediaId
  done += 1
  if (done % 20 === 0) { await saveMap(); console.log(`  사진 ${done}장 올림`) }
  return intent.mediaId
}

const seed = JSON.parse(await readFile(resolve(HERE, 'cms_seed.json'), 'utf8'))
if (!DRY) {
  const session = await api('POST', '/api/cms/login', { loginId: LOGIN, password: PASSWORD })
  if (session && session.sessionIssued === false) throw new Error('공간을 골라야 합니다')
}
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
console.log('사진 준비 끝 · 칸', Object.keys(content).length, '· 고유 사진', Object.keys(mediaMap).length, '· 이번에 올림', done)
console.log('콘텐츠 크기(바이트)', Buffer.byteLength(JSON.stringify(content)))
if (DRY) process.exit(0)

// 관리자 화면처럼: 지금 값(저장본 + 묶음 기본값) 위에 덮어 통째로 저장한다.
const loaded = await api('GET', '/api/cms/site-content')
const theme = { ...loaded.theme, siteContent: { ...loaded.content, ...content } }
await api('PUT', '/api/cms/theme', { theme, themeRev: loaded.themeRev })
console.log('저장 끝')
if (!NO_PUBLISH) {
  const docs = await api('GET', '/api/cms/documents')
  await api('POST', '/api/cms/site-content/publish', { baseTransitionNo: docs.baseTransitionNo }, { 'idempotency-key': `sororong-${Date.now()}` })
  console.log('공개 끝')
}
