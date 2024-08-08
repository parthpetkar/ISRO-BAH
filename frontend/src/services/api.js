import axios from 'axios';

const API_URL = 'http://localhost:8000/';

export const createChat = async (messages) => {
    try {
        const response = await axios.post(`${API_URL}save_chat/`, { input_response_pairs: messages });
        return response.data;
    } catch (error) {
        console.error('Error creating chat', error);
        throw error;
    }
};

export const addMessageToChat = async (chatId, messages) => {
    try {
        const response = await axios.put(`${API_URL}update_chat/${chatId}/`, { input_response_pairs: messages });
        return response.data;
    } catch (error) {
        console.error('Error updating chat', error);
        throw error;
    }
};

export const saveChatToCache = async (messages) => {
    try {
        const response = await axios.post(`${API_URL}save_chat_to_cache/`, { chat_data: messages });
        return response.data;
    } catch (error) {
        console.error('Error saving chat to cache', error);
        throw error;
    }
};

export const saveCacheToDb = async () => {
    try {
        const response = await axios.post(`${API_URL}save_cache_to_db/`);
        return response.data;
    } catch (error) {
        console.error('Error saving cache to db', error);
        throw error;
    }
};

export const fetchChatFromDb = async (chatId) => {
    try {
        const response = await axios.get(`${API_URL}fetch_chat_from_db/${chatId}/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching chat from db', error);
        throw error;
    }
};

export const fetchChats = async () => {
    try {
        const response = await axios.get(`${API_URL}list_chats/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching chats', error);
        throw error;
    }
};
