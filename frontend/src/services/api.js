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

export const saveChatToCache = async (messages) => {
    try {
        const response = await axios.post(`${API_URL}save_chat_to_cache/`, { chat_data: messages });

        // Check if the response status code indicates success
        if (response.status !== 200) {
            throw new Error(`API error: ${response.statusText}`);
        }

        // Update the messages with the new chat_data returned from the server
        return response.data.chat_data;
    } catch (error) {
        console.error('Error saving chat to cache:', error.message);
        throw error;  // Re-throw the error to be caught by the caller
    }
};



export const saveCacheToDb = async (chatId) => {
    try {
        const response = await axios.post(`${API_URL}save_cache_to_db/`, { chat_id: chatId });
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
