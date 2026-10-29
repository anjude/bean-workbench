async function call(op, key, value, ttl) {
  const response = await fetch('/__redis', { method: 'POST', body: JSON.stringify({ op, key, value, ttl }) })
  const data = await response.json(); return { errCode: 0, data: { redisValue: data.value } }
}
export const commonApi = {
  getFeRedis: ({ redisKey }) => call('get', redisKey),
  setFeRedis: ({ redisKey, redisValue, expireSeconds }) => call('set', redisKey, redisValue, expireSeconds),
  delFeRedis: ({ redisKey }) => call('del', redisKey),
}
