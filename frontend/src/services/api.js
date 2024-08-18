import axios from 'axios';

const API_URL = 'http://localhost:8000/';

/**
 * Creates a new chat by sending a POST request to the API.
 *
 * @param {Object[]} messages - An array of objects representing the chat messages.
 * @param {string} messages[].input - The user input.
 * @param {string} messages[].response - The bot response.
 *
 * @returns {Promise<Object>} - A promise that resolves with the API response data.
 *
 * @throws {Error} - If the API request fails, the promise will be rejected with an error.
 */
export const createChat = async (messages) => {
    try {
        const response = await axios.post(`${API_URL}save_chat/`, { input_response_pairs: messages });
        return response.data;
    } catch (error) {
        console.error('Error creating chat:', error.message || error);
        throw error;
    }
};

/**
 * Saves chat data to the cache by sending a POST request to the API.
 *
 * @param {Object} chatData - The chat data to be saved.
 * @param {string} option - The option for saving the chat data.
 *
 * @returns {Promise<Object>} - A promise that resolves with the API response data.
 *
 * @throws {Error} - If the API request fails, the promise will be rejected with an error.
 */
export const saveChatToCache = async (chatData, option) => {
    try {
        const response = await axios.post(`${API_URL}save_chat_to_cache/`, {
            chat_data: chatData,
            option: option
        });

        // Check if the response status code indicates success
        if (response.status !== 200) {
            throw new Error(`API error: ${response.statusText}`);
        }

        // If the option is "mapping", handle mapping-specific response
        if (option === "mapping") {
            return response;  // Adjust based on actual response structure
        }

        return response.data;
    } catch (error) {
        console.error('Error saving chat to cache:', error.message || error);
        throw error;  // Re-throw the error to be caught by the caller
    }
};

/**
 * Saves chat data from the cache to the database by sending a POST request to the API.
 *
 * @param {string} chatId - The ID of the chat to be saved.
 *
 * @returns {Promise<Object>} - A promise that resolves with the API response data.
 *
 * @throws {Error} - If the API request fails, the promise will be rejected with an error.
 */
export const saveCacheToDb = async (chatId) => {
    try {
        const response = await axios.post(`${API_URL}save_cache_to_db/`, { chat_id: chatId });

        if (response.status !== 200) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.data;
    } catch (error) {
        console.error('Error saving cache to db:', error.message || error);
        throw error;
    }
};

/**
 * Fetches a chat from the database by sending a GET request to the API.
 *
 * @param {string} chatId - The ID of the chat to be fetched.
 *
 * @returns {Promise<Object>} - A promise that resolves with the API response data.
 *
 * @throws {Error} - If the API request fails, the promise will be rejected with an error.
 */
export const fetchChatFromDb = async (chatId) => {
    try {
        const response = await axios.get(`${API_URL}fetch_chat_from_db/${chatId}/`);

        if (response.status !== 200) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.data;
    } catch (error) {
        console.error('Error fetching chat from db:', error.message || error);
        throw error;
    }
};

/**
 * Fetches a list of chats from the database by sending a GET request to the API.
 *
 * @returns {Promise<Object[]>} - A promise that resolves with an array of API response data.
 *
 * @throws {Error} - If the API request fails, the promise will be rejected with an error.
 */
export const fetchChats = async () => {
    try {
        const response = await axios.get(`${API_URL}list_chats/`);

        if (response.status !== 200) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.data;
    } catch (error) {
        console.error('Error fetching chats:', error.message || error);
        throw error;
    }
};
