import { onMounted } from 'vue'
export const onLoad = callback => onMounted(() => callback(Object.fromEntries(new URLSearchParams(location.search))))
export const onHide = () => {}
export const onShow = callback => onMounted(callback)
export const onShareAppMessage = callback => { window.__share = callback }
