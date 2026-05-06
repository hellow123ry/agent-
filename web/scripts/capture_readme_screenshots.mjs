import { chromium } from 'playwright'
import fs from 'fs/promises'

const OUT_DIR = '/Users/bytedance/Desktop/multi_agent_dialog_system/docs/assets'
const APP_URL = 'http://127.0.0.1:5174/'

async function ensureDir() {
  await fs.mkdir(OUT_DIR, { recursive: true })
}

async function waitForPageReady(page) {
  await page.waitForSelector('textarea', { timeout: 15000 })
  await page.waitForFunction(
    () => {
      const text = document.body.innerText || ''
      return text.includes('生活服务 Multi-Agent Workbench') && !text.includes('Vite')
    },
    { timeout: 15000 },
  )
  await page.waitForTimeout(3000)
}

async function run() {
  await ensureDir()
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({
    viewport: { width: 1720, height: 1300 },
    deviceScaleFactor: 1,
  })
  page.on('console', (message) => console.log('browser:', message.type(), message.text()))

  await page.goto(APP_URL, { waitUntil: 'networkidle' })
  await waitForPageReady(page)

  const textarea = page.locator('textarea')
  await textarea.fill('我想订明天晚上的烤肉店，2个人')
  await page.getByRole('button', { name: '发送' }).click()

  await page.waitForFunction(
    () => {
      const text = document.body.innerText || ''
      return text.includes('请问您想订哪一家？') || text.includes('全聚德烤鸭')
    },
    { timeout: 90000 },
  )

  await page.getByRole('button', { name: '运行评测' }).click()
  await page.waitForFunction(
    () => {
      const text = document.body.innerText || ''
      return text.includes('运行中...') || text.includes('status: running') || text.includes('current_system:')
    },
    { timeout: 15000 },
  )
  await page.waitForTimeout(3000)

  await page.screenshot({ path: `${OUT_DIR}/workbench-overview.png`, fullPage: true })
  await page.locator('.chat-panel').screenshot({ path: `${OUT_DIR}/chat-debug-view.png` })
  await page.locator('.eval-panel').screenshot({ path: `${OUT_DIR}/eval-dashboard.png` })
  await page.locator('.knowledgebase-panel').screenshot({ path: `${OUT_DIR}/knowledgebase-editor.png` })

  await browser.close()
}

run().catch((error) => {
  console.error(error)
  process.exit(1)
})
