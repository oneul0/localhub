import apiClient from './client'

const CHATBOT_TIMEOUT_MS = 60000

export const sendChatMessage = async (message) => {
  const { data } = await apiClient.post(
    '/api/chatbot/query',
    { message },
    { timeout: CHATBOT_TIMEOUT_MS },
  )
  return data
}
