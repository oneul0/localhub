import apiClient from './client'

export const getPosts = async (page = 1, pageSize = 10) => {
  const { data } = await apiClient.get('/api/posts', { params: { page, page_size: pageSize } })
  return data
}

export const getPostById = async (postId) => {
  const { data } = await apiClient.get(`/api/posts/${postId}`)
  return data
}

export const createPost = async (payload) => {
  const { data } = await apiClient.post('/api/posts', payload)
  return data
}

export const updatePost = async (postId, payload) => {
  const { data } = await apiClient.put(`/api/posts/${postId}`, payload)
  return data
}

export const verifyPostPassword = async (postId, password) => {
  const { data } = await apiClient.post(`/api/posts/${postId}/verify-password`, { password })
  return data
}

export const deletePost = async (postId, password) => {
  const { data } = await apiClient.delete(`/api/posts/${postId}`, { data: { password } })
  return data
}
