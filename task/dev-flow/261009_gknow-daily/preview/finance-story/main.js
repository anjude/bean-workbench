import { createApp, h, watch, ref, onMounted } from 'vue'
import Page from '@/pages/quiz/finance-personality/index.vue'
import styles from '@/styles/06-pages/_finance-personality.scss?inline'
const css = styles.replace(/(-?\d*\.?\d+)rpx/g, (_, value) => `calc(var(--rpx) * ${value})`)
const style = document.createElement('style')
style.textContent = `:root{--rpx:calc(100vw / 750)}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}view,scroll-view{display:block}text{display:inline}button{font:inherit;cursor:pointer}button:disabled{cursor:default}img{display:block;object-fit:cover} .finance button.finance__preview-poster{display:block;margin:16px auto 0;padding:12px 18px;border:1px solid #294e50;border-radius:10px;background:#fff5df;color:#294e50} ${css}`
document.head.appendChild(style)
if (new URLSearchParams(location.search).has('still')) {
  const still = document.createElement('style')
  still.textContent = '*{animation:none!important;transition:none!important}'
  document.head.appendChild(still)
}
window.uni = { getWindowInfo: () => ({ statusBarHeight: 44, windowWidth: innerWidth }), getMenuButtonBoundingClientRect: () => ({ top: 50, height: 32, left: innerWidth - 96 }), navigateBack: () => { location.href = '/' }, reLaunch: () => { location.href = '/' } }
window.getCurrentPages = () => [{}]
const app = createApp(Page)
app.component('view', { setup(_, { attrs, slots }) { return () => h('div', attrs, slots.default?.()) } })
app.component('text', { setup(_, { attrs, slots }) { return () => h('span', attrs, slots.default?.()) } })
app.component('scroll-view', { setup(_, { attrs, slots }) {
  const element = ref(null)
  watch(() => attrs['scroll-top'], value => { if (element.value) element.value.scrollTop = Number(value) }, { flush: 'post' })
  return () => h('div', { ...attrs, ref: element, style: [attrs.style, { overflowY: 'auto', overscrollBehavior: 'contain' }] }, slots.default?.())
} })
app.component('gk-header', { setup(_, { attrs }) {
  return () => h('div', { class: 'finance-preview-nav', style: { position: 'fixed', zIndex: 20, top: 0, left: 0, right: 0, height: '88px', paddingTop: '44px', boxSizing: 'border-box', display: 'flex', alignItems: 'center' } }, [
    h('button', { onClick: () => { location.href = '/' }, 'aria-label': '返回', style: { width: '48px', height: '44px', padding: 0, border: 'none', background: 'transparent', color: 'inherit', fontSize: '28px' } }, '‹'),
    h('span', { style: { position: 'absolute', top: '44px', height: '44px', left: '104px', right: '104px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '17px' } }, attrs.title),
    h('span', { class: 'finance-preview-capsule', 'aria-hidden': true, style: { position: 'absolute', top: '50px', right: '8px', width: '88px', height: '32px', border: '1px solid #294e5044', borderRadius: '18px', display: 'flex', alignItems: 'center', justifyContent: 'space-evenly', fontSize: '17px' } }, '···　◉'),
  ])
} })
app.component('gk-page', { setup(_, { slots }) { return () => h('div', { class: new URLSearchParams(location.search).get('theme') === 'dark' ? 'theme-dark' : 'theme-light' }, slots.default?.()) } })
app.component('gk-result-poster', { setup() { return () => h('button', { class: 'finance__preview-poster', disabled: true }, '微信小程序内可生成结果海报') } })
document.addEventListener('click', event => {
  if (event.target.closest('button')?.disabled) return
  event.target.dispatchEvent(new Event('tap', { bubbles: true }))
}, true)
app.mount('#app')
