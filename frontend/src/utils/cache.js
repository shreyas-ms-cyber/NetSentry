// Simple in-memory cache with expiration
const cache = new Map()

export const getCached = (key) => {
  const item = cache.get(key)
  if (!item) return null
  if (Date.now() > item.expiry) {
    cache.delete(key)
    return null
  }
  return item.data
}

export const setCached = (key, data, ttlSeconds = 60) => {
  cache.set(key, {
    data,
    expiry: Date.now() + ttlSeconds * 1000
  })
}

export const clearCache = () => cache.clear()
