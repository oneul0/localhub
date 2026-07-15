import apiClient from './client'

export const sendChatMessage = async (message) => {
  const { data } = await apiClient.post('/api/chatbot/query', { message })
  return data
}
