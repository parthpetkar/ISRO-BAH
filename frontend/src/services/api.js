import axios from 'axios';

const API_URL = 'http://localhost:8000/';

export const saveChat = async (inputResponsePairs) => {
    try {
        const response = await axios.post(`${API_URL}save_chat/`, { input_response_pairs: inputResponsePairs });
        return response.data;
    } catch (error) {
        console.error('Error saving chat', error);
        throw error;
    }
};
