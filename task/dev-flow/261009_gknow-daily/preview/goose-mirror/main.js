import { createApp, h } from 'vue'
import Page from '@/pages/quiz/goose-mirror/index.vue'
import Collection from '@/pages/collection/index.vue'
import ResultPoster from '@/components/gk-result-poster.vue'
import source from '@/styles/index.scss?inline'
const css = source.replace(/(-?\d*\.?\d+)rpx/g, (_, value) => `calc(var(--rpx) * ${value})`)
const style = document.createElement('style')
style.textContent = `:root{--rpx:calc(100vw / 750)}html,body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}*{box-sizing:border-box}view{display:block}button{font:inherit;border:0;cursor:pointer}button:disabled{opacity:.45}img{object-fit:contain}button[open-type]{min-height:44px} ${css}`
document.head.appendChild(style)
window.uni = {
  getStorageSync: key => JSON.parse(localStorage.getItem(key) || 'null'),
  setStorageSync: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
  removeStorageSync: key => localStorage.removeItem(key),
  showModal: async () => ({ confirm: true }), showToast: () => {}, navigateTo: ({ url }) => {
    const query = new URLSearchParams(location.search)
    const target = new URL(url, location.origin)
    query.set('surface', target.pathname.includes('collection') ? 'collection' : 'mirror')
    for (const [key, value] of target.searchParams) query.set(key, value)
    location.href = '/?' + query
  },
}
window.getCurrentPages = () => [{}]
const app = createApp(new URLSearchParams(location.search).get('surface') === 'collection' ? Collection : Page)
for (const tag of ['view', 'text']) app.component(tag, { setup(_, { attrs, slots }) { return () => h(tag === 'text' ? 'span' : 'div', attrs, slots.default?.()) } })
app.component('gk-page', { setup(_, { slots }) { return () => h('div', { class: new URLSearchParams(location.search).get('theme') === 'dark' ? 'theme-dark' : 'theme-light', style: { minHeight: '100vh', background: 'var(--gk-bg)', color: 'var(--gk-text)' } }, [slots.header?.(), slots.default?.()]) } })
app.component('gk-header', { setup() { return () => h('div', { style: { height: '88px', padding: '48px 24px 0', fontSize: '17px', textAlign: 'center', borderBottom: '1px solid var(--gk-border)' } }, '‹　　鹅眼中的我　　···') } })
app.component('gk-goose-expression', { setup() { return () => h('span', '鹅') } })
app.component('gk-result-poster', ResultPoster)
app.component('gk-loading-state', { setup() { return () => h('div', '正在读取…') } })
document.addEventListener('click', e => { const button = e.target.closest('button'); if (button && !button.disabled) button.dispatchEvent(new Event('tap', { bubbles: true })) })
app.mount('#app')
