const id = new URLSearchParams(location.search).get('user') || 'A'
const store = { ready: true, userInfo: { openid: id, nickName: id === 'A' ? '阿白的朋友' : id === 'B' ? '老朋友小陈' : '朋友小林' } }
export const useAppStore = () => store
